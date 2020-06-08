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
from fastapi.openapi.docs import get_redoc_html
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from timeout_decorator import timeout, TimeoutError
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
from .db import SourceController, Source
from .conf import docker_prepare_conf, fastapi_config
from .decorators import run_container


api = FastAPI(**fastapi_config)
docker_client = docker.from_env()
es_code_client = SourceController()


class SupportedImages(str, Enum):
    shellgeibot = 'theoldmoon0602/shellgeibot:latest'


class SupportedCommands(str, Enum):
    default = 'bash -c "chmod +x %(filename)s && sync && ./%(filename)s | stdbuf -o0 head -c 100K | stdbuf -o0 head -n 105"'


class SupportedFilenames(str, Enum):
    shell = 'Main.sh'


class ShellgeiResponse(BaseModel):
    stdout: str = Body(None, description='Standard Output')
    stderr: str = Body(None, description='Standard Error')
    exit_code: str = Body(
        None, description='Exit code.\n\nIf the command finishes without any errors, it returns `0`.')
    exec_sec: str = Body(
        None, description='Execution time.\n\nThe function returns the string, such as `1.234 sec`.')
    images: List[str] = Body([], description=('URL of the image generated during the execution of shell art code.\n\n'
                                              'The images saved in the `/images` folder during the execution of '
                                              'the shell script are automatically sent to the server as It will '
                                              'be uploaded.\n\nThis field contains the URL to access these images.'))


class ShellgeiSaveRequest(BaseModel):
    author: str = Body(..., description='User Name', max_length=16)
    description: str = Body(...,
                            description='Details about source code', max_length=280)
    main: str = Body(..., description='Source Code', max_length=4000)


class ShellgeiUpdateRequest(BaseModel):
    pid: str = Body(...)
    author: Optional[str] = Body(None, max_length=16)
    description: Optional[str] = Body(None, max_length=280)
    main: Optional[str] = Body(None, max_length=4000)
    votes: Optional[int] = Body(None, ge=0)
    views: Optional[int] = Body(None, ge=0)


class SortOrder(str, Enum):
    asc = 'asc'
    desc = 'desc'


class SortKey(str, Enum):
    _score = '_score'
    post_at = 'post_at'
    author = 'author'
    description = 'description'
    main = 'main'
    votes = 'votes'
    views = 'views'


class SearchQuery:
    def __init__(
        self,
        author: str = Query(
            None,
            description='User Name',
            max_length=16
        ),
        description: str = Query(
            None,
            description='Details about source code',
            max_length=280
        ),
        main: str = Query(None, description='Source Code', max_length=4000),
        offset: int = Query(
            0,
            description='`offset` is used to skip the number of records from the results.',
            ge=0,
            le=100000
        ),
        limit: int = Query(
            10,
            description=('`limit` will retrieveonly the number of records '
                         'specified after the `limit` keyword, unless the '
                         'query itself returns fewer records than the number '
                         'specified by `limit`.'),
            ge=1,
            le=20
        ),
        order: SortOrder = Query(
            SortOrder.desc,
            description='Ascending or Descending order.'
        ),
        key: SortKey = Query(
            SortKey.post_at,
            description='Sort key'
        )
    ):
        self.author: Optional[str] = author
        self.description: Optional[str] = description
        self.main: Optional[str] = main
        self.offset: Optional[int] = offset
        self.limit: Optional[int] = limit
        self.order: SortOrder = order
        self.key: SortKey = key

    def to_query(self):
        query = {
            'query': {
                'bool': {
                    'must': []
                }
            }
        }
        if self.author:
            query['query']['bool']['must'].append(
                {'match': {'author': self.author}})
        if self.description:
            query['query']['bool']['must'].append(
                {'match': {'description': self.description}})
        if self.main:
            query['query']['bool']['must'].append(
                {'match': {'main': self.main}})
        if not self.author and not self.description and not self.main:
            query['query'] = {'match_all': {}}
        query['sort'] = {
            self.key: {
                "order": self.order,
            }
        }
        query['from'] = self.offset
        query['size'] = self.limit
        return query


class PingResponse(BaseModel):
    status: str = Body("API Server Working", description="Server Status")


class StatusResponse(BaseModel):
    message: str = Body(None, description="HTTP Status Description")


@api.get("/ping", response_model=PingResponse, tags=['General'])
def ping():
    """
    Returns a simple response ... if the server is alive.
    """
    return {
        "status": "API Server Working",
    }


# @api.get("/welcome", deprecated=True)
# async def index():
#     with open('static/index.html') as f:
#         return HTMLResponse(f.read())


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
            "description": "Too many requests in short time"
        }
    },
    tags=['Shell Script']
)
async def run(
    background_tasks: BackgroundTasks,
    source: str = Form(
        ...,
        max_length=4000,
        description='Shell script source code'
    ),
    files: List[UploadFile] = File(
        None,
        description=('File to be attached.\n\nThese files are renamed '
                     'as `0`,`1`,`2`,`3`, and then added to `/media` '
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

        **1.** The maximum execution time is 20 seconds.

        **2.** The output file size limit is 5MB.

        **3.** The number of available processes is 128.

        **4.** Network connection is not available.

        **5.** The available memory is 256MB and the swap memory is 256MB.

        **6.** The number of characters that can be output is 3000, and the number of lines is 100.
    '''
    print(filename.value, image.value, command.value)
    container_list = docker_client.containers.list(
        filters={'ancestor': image.value}
    )
    if len(container_list) > 10:
        raise HTTPException(503)
    run_id = secrets.token_hex(8)
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


@api.post("/posts", status_code=204, tags=['Shell Script'])
async def post_code(req: ShellgeiSaveRequest):
    '''
    Storing the source code to the database.
    '''
    Source(**req.dict()).register(es_code_client)


@api.put("/posts", status_code=204, include_in_schema=False)
async def update_code(req: ShellgeiUpdateRequest):
    print(req.pid, req.dict())
    post_id = req.pid
    data = req.dict()
    try:
        es_code_client.update_by_id(post_id, data)
    except elasticsearch.exceptions.NotFoundError as e:
        raise HTTPException(404, 'Post not Found')


@api.get("/search", tags=['Shell Script'])
async def search(q: SearchQuery = Depends(SearchQuery)):
    '''
    Search for source code stored in the database.
    '''
    num, resp = es_code_client.fetch_by_query(q.to_query())
    return {
        "num": num,
        "content": resp
    }


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
            fps.append(fastapi_config['openapi_prefix'] + fp)
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
