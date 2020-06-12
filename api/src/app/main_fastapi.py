from fastapi import (
    FastAPI,
    Header,
    Depends,
    HTTPException,
    Form,
    UploadFile,
    BackgroundTasks,
    File,
    Body,
    Query,
    Depends,
    Path
)
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from timeout_decorator import timeout, TimeoutError
from datetime import datetime
import elasticsearch
import json
import shutil
import os
import io
import urllib.parse
import hashlib
import binascii
import secrets
import base64
import glob
import aiofiles
from time import sleep, perf_counter
import docker
from docker import types
from shutil import rmtree
from .limiter import Limiter
from .conf import docker_prepare_conf, fastapi_config
from .decorators import run_container


api = FastAPI(**fastapi_config)
limiter = Limiter(user=os.environ['MONGO_INITDB_ROOT_USERNAME'],
                  passwd=os.environ['MONGO_INITDB_ROOT_PASSWORD'])
docker_client = docker.from_env()


def custom_openapi():
    if api.openapi_schema:
        return api.openapi_schema
    openapi_schema = get_openapi(
        title="Web Bash",
        version="v 1.1.1",
        openapi_prefix='/api',
        description="API for executing shell(gei) scripts",
        routes=api.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://blog.chomama.jp/wp-content/uploads/2020/06/webbashicon-2.png"
    }
    api.openapi_schema = openapi_schema
    return api.openapi_schema


api.openapi = custom_openapi  # type: ignore


class SupportedImages(str, Enum):
    shellgeibot = 'theoldmoon0602/shellgeibot:latest'


class SupportedCommands(str, Enum):
    default = 'bash -c "chmod +x %(filename)s && sync && ./%(filename)s | stdbuf -o0 head -c 100K | stdbuf -o0 head -n 105"'


class SupportedFilenames(str, Enum):
    shell = 'Main.sh'


class ShellgeiResponse(BaseModel):
    stdout: str = Body("Hello, World!", description='Standard Output')
    stderr: str = Body("", description='Standard Error')
    exit_code: str = Body(
        "0", description='Exit code.\n\nIf the command finishes without any errors, it returns `0`.')
    exec_sec: str = Body(
        "0.328 sec", description='Execution time.\n\nThe function returns the string, such as `1.234 sec`.')
    images: List[str] = Body([], description=('URL of the image generated during the execution of shell art code.\n\n'
                                              'The images saved in the `/images` folder during the execution of '
                                              'the shell script are automatically sent to the server as It will '
                                              'be uploaded.\n\nThis field contains the URL to access these images.'))


class PingResponse(BaseModel):
    status: str = Body("API Server Working", description="Server Status")


class StatusResponse(BaseModel):
    message: str = Body(None, description="HTTP Status Description")


@api.get(
    "/ping",
    response_model=PingResponse,
    tags=['General']
)
def ping():
    """
    Returns a simple response ... if the server is alive.
    """
    return {
        "status": "API Server Working",
    }


@api.get(
    "/images/{path}",
    response_class=FileResponse,
    description='Return an image generated from shell-gei code.',
    response_description='Requested Image',
    responses={
        200: {"content": {"image/*": {}}},
        404: {
            "model": StatusResponse,
            "message": "Image not Found Error"
        }
    },
    tags=['General']
)
async def image(path: str = Path(..., description='Image Name such as `029cd08ffe65c2da_6bb039e56b21c3665eb10fbeaf0a9cfd64b369645779a1e9.png`')):
    fp = '/images/' + path
    if os.path.exists(fp):
        return FileResponse(fp)
    return JSONResponse(content={"message": "Image not Found"}, status_code=404)


@api.post(
    "/run",
    response_model=ShellgeiResponse,
    responses={
        503: {
            "model": StatusResponse,
            "description": "Resource exhaustion of the host due to many accesses."
        },
        429: {
            "model": StatusResponse,
            "description": "Too many requests in a short time"
        }
    },
    tags=['Shell Script'],
    dependencies=[
        Depends(limiter.limit('shellgei_10minlimit', 120, '10min', '30min')),
        Depends(limiter.limit('shellgei_1minlimit', 15, '1min', '90min')),
        Depends(limiter.limit('shellgei_10seclimit', 10, '10sec', '1days')),
        Depends(limiter.limit('shellgei_1seclimit', 3, '1sec', '1000000days')),
    ]
)
async def run(
    background_tasks: BackgroundTasks,
    source: str = Form(
        ...,
        max_length=4000,
        description='Shell script source code'
    ),
    f0: UploadFile = File(
        None,
        description=('File to be attached.\n\nThese files are renamed '
                     'as `0`, and then added to `/media` '
                     'folder.\nThe saved image can be called from the script.')
    ),
    f1: UploadFile = File(
        None,
        description=('File to be attached.\n\nThese files are renamed '
                     'as `1`, and then added to `/media` '
                     'folder.\nThe saved image can be called from the script.')
    ),
    f2: UploadFile = File(
        None,
        description=('File to be attached.\n\nThese files are renamed '
                     'as `2`, and then added to `/media` '
                     'folder.\nThe saved image can be called from the script.')
    ),
    f3: UploadFile = File(
        None,
        description=('File to be attached.\n\nThese files are renamed '
                     'as `3`, and then added to `/media` '
                     'folder.\nThe saved image can be called from the script.')
    ),
    filename: SupportedFilenames = Form(
        SupportedFilenames.shell,
        description='The file name to save the contents of `source`.'
    ),
    command: SupportedCommands = Form(
        SupportedCommands.default,
        description=('Commands for executing shell scripts.\n\n'
                     'The file name `filename` set above can be used with `%(filename)s`.')
    ),
    image: SupportedImages = Form(
        SupportedImages.shellgeibot,
        description='Docker container name for running shell scripts.'
    ),
):
    '''
        Run Shellgei.

        **Execute on the Docker container under the following constraints.**

        1. The maximum execution time is 20 seconds.

        2. The output file size limit is 5MB.

        3. The number of available processes is 128.

        4. Network connection is not available.

        5. The available memory is 256MB and the swap memory is 256MB.

        6. The number of characters that can be output is 3000, and the number of lines is 100.

        __If you make a large number of requests in a very short time, the application rejects the requests for a certain period of time.__

        1. Over 120 requests in 10 minutes: 30-minute ban

        2. Over 15 requests in 1 minutes: 90-minute ban

        3. Over 10 requests in 10 seconds: 7-day ban

        4. Over 3 requests in 1 seconds: 1 million hrs ban.
    '''
    print(filename.value, image.value, command.value)
    container_list = docker_client.containers.list(
        filters={'ancestor': image.value}
    )
    if len(container_list) > 10:
        raise HTTPException(503)
    run_id = secrets.token_hex(8)
    files = [f for f in [f0, f1, f2, f3] if f is not None]
    await write_source(run_id, source, filename, files)
    container = create_container(image, run_id, docker_prepare_conf)
    resp = ShellgeiResponse()
    try:
        time, (exit_code, stdout, stderr) = run_shellgei(
            container, command, filename, run_id
        )
        resp.stdout = decode(stdout)
        resp.stderr = decode(stderr)
        resp.exec_sec = f'{time:.3f} sec'
        resp.exit_code = exit_code
        images = upload_images(run_id)
        resp.images = images
    except TimeoutError:
        resp.stdout = ''
        resp.stderr = ''
        resp.exec_sec = 'Timeout'
        resp.exit_code = ''
        resp.images = []
    background_tasks.add_task(clean_container, container, run_id, [
                              '/src', '/images', '/media'])
    return resp


def decode(s, line=100, count=3000):
    s = s.decode('utf-8', "replace") if s else ""
    if len(s.split('\n')) > line:
        s = '\n'.join(s.split('\n')[:line]) + "\n..."
    if len(s) > count:
        s = s[:count] + "\n..."
    return s


def upload_images(run_id):
    images = glob.glob(f'/tmp/app/{run_id}/images/**.png')
    images.extend(glob.glob(f'/tmp/app/{run_id}/images/**.jpg'))
    images.extend(glob.glob(f'/tmp/app/{run_id}/images/**.gif'))
    images.extend(glob.glob(f'/tmp/app/{run_id}/images/**.jpeg'))
    fps = []
    if images:
        for i, image in enumerate(sorted(images)[:4]):
            print(image)
            ext = os.path.splitext(image)[1]
            fp = f'/images/{run_id}_{secrets.token_hex(24)}{ext}'
            shutil.copy(image, fp)
            fps.append(
                (fastapi_config['openapi_prefix'] + fp).replace('//', '/'))
    return fps


async def write_source(run_id, code, filename, media=None):
    os.makedirs(f'/tmp/app/{run_id}/src')
    os.makedirs(f'/tmp/app/{run_id}/media')
    os.makedirs(f'/tmp/app/{run_id}/images')
    async with aiofiles.open(f'/tmp/app/{run_id}/src/{filename.value}', 'w') as f:
        await f.write(code)
    if media:
        for i, image in enumerate(media):
            async with aiofiles.open(f"/tmp/app/{run_id}/media/{i}", 'wb') as f:
                await f.write(await image.read())


def create_container(image, run_id, conf):
    return docker_client.containers.run(
        image.value,
        name=f"{run_id}",
        volumes={
            f'/tmp/app/{run_id}/src': {'bind': f'/src', 'mode': 'rw'},
            f'/tmp/app/{run_id}/images': {'bind': '/images', 'mode': 'rw'},
            f'/tmp/app/{run_id}/media': {'bind': '/media', 'mode': 'rw'}
        },
        **conf
    )


@run_container()
@timeout(20)
def run_shellgei(container, command, filename, run_id):
    print(str(command.value) % {"filename": filename.value})
    (exit_code, (stdout, stderr)) = container.exec_run(
        cmd=str(command.value) % {"filename": filename.value},
        workdir=f'/src',
        demux=True
    )
    return exit_code, stdout, stderr


def clean_container(container, run_id, directories):
    cmd = '&&'.join(
        f"rm -rf {directory}" % {"run_id": run_id} for directory in directories
    )
    container.exec_run(cmd, workdir='/')
    container.kill()
    rmtree(f'/tmp/app/{run_id}')
