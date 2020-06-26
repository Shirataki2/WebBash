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
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from timeout_decorator import timeout, TimeoutError
from datetime import datetime
import starlette
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
from app.router import oauth, token, users, posts
from app.database import models
from app.database.base import engine, SessionLocal, get_db
from app.limiter import Limiter
from app.conf import docker_prepare_conf, fastapi_config
from app.decorators import run_container

models.Base.metadata.create_all(bind=engine)


api = FastAPI(**fastapi_config)
api.add_middleware(SessionMiddleware, secret_key=os.environ['SESSION_KEY'])


limiter = Limiter(user=os.environ['MONGO_INITDB_ROOT_USERNAME'],
                  passwd=os.environ['MONGO_INITDB_ROOT_PASSWORD'])
docker_client = docker.from_env()


def custom_openapi(openapi_prefix: str):  # pragma: no cover
    if api.openapi_schema:
        return api.openapi_schema
    openapi_schema = get_openapi(
        title="Web Bash API",
        version="v 2.0.5",
        openapi_prefix=openapi_prefix,
        description="シェル芸 on API",
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
    media: List[str] = Body([], description=(''))


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
    単純なレスポンスを返します
    """
    return {
        "status": "API Server Working",
    }


@api.get(
    "/images/{path}",
    response_class=FileResponse,
    description='過去のシェル芸の結果生成された画像を得ます．',
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
async def image(path: str = Path(..., description='画像名\n\n例: `029cd08ffe65c2da_6bb039e56b21c3665eb10fbeaf0a9cfd64b369645779a1e9.png`')):
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
        description='シェル芸を走らせます'
    ),
    f0: UploadFile = File(
        None,
        description=('添付するファイル．\n\nTwitterでの画像送信の要領で最大４枚送信可能です．\n\n'
                     'このファイルは`0`と改名されて`/media`フォルダに置かれます．\n\n'
                     'スクリプト中に呼び出すなどしてご活用ください．')
    ),
    f1: UploadFile = File(
        None,
        description=('添付するファイル．\n\nTwitterでの画像送信の要領で最大４枚送信可能です．\n\n'
                     'このファイルは`1`と改名されて`/media`フォルダに置かれます．\n\n'
                     'スクリプト中に呼び出すなどしてご活用ください．')
    ),
    f2: UploadFile = File(
        None,
        description=('添付するファイル．\n\nTwitterでの画像送信の要領で最大４枚送信可能です．\n\n'
                     'このファイルは`2`と改名されて`/media`フォルダに置かれます．\n\n'
                     'スクリプト中に呼び出すなどしてご活用ください．')
    ),
    f3: UploadFile = File(
        None,
        description=('添付するファイル．\n\nTwitterでの画像送信の要領で最大４枚送信可能です．\n\n'
                     'このファイルは`3`と改名されて`/media`フォルダに置かれます．\n\n'
                     'スクリプト中に呼び出すなどしてご活用ください．')
    ),
    filename: SupportedFilenames = Form(
        SupportedFilenames.shell,
        description='ソースコードを保存するファイル名'
    ),
    command: SupportedCommands = Form(
        SupportedCommands.default,
        description=('シェル芸実行の際に走らせるコード\n\n'
                     '上で定義したのパラメーター`filename`は`%(filename)s`とすることで利用できます.')
    ),
    image: SupportedImages = Form(
        SupportedImages.shellgeibot,
        description='シェル芸用のDockerコンテナ'
    ),
):
    '''
        シェル芸を走らせます．

        **以下の制約の下実行されます**

        1. 実行時間は最大20秒.

        2. 最大出力ファイルサイズは5MB.

        3. 利用可能プロセス数は128.

        4. ネットワークは利用不可.

        5. メモリは256MBまで使用可能.

        6. 3000文字もしくは100行以上の出力は省略される.

        短期間に集中してアクセスがあった場合，一定期間のアクセスが禁止されます，

        1. 120回 / 10分: 30分 利用停止

        2. 15回 / 1分: 90分 利用停止

        3. 10回 / 10秒: 24時間 利用停止

        4. 3回 / 1秒: 無期限 利用停止
    '''
    container_list = docker_client.containers.list(
        filters={'ancestor': image.value}
    )
    # TODO: ここの503をテストでカバーするのむずい
    if len(container_list) > 10:  # pragma: no cover
        raise HTTPException(503)
    run_id = secrets.token_hex(8)
    files = [f for f in [f0, f1, f2, f3] if f is not None]
    media = await write_source(run_id, source, filename, files)
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
        resp.media = media
    except TimeoutError:  # pragma: no cover
        resp.stdout = ''
        resp.stderr = ''
        resp.exec_sec = 'Timeout'
        resp.exit_code = ''
        resp.images = []
        resp.media = []
    background_tasks.add_task(clean_container, container, run_id, [
                              '/src', '/images', '/media'])
    return resp


api.include_router(
    oauth.router,
    prefix='/oauth',
    tags=['OAuth']
)

api.include_router(
    token.router,
    prefix='/token',
    tags=['Token']
)

api.include_router(
    users.router,
    prefix='/users',
    tags=['Users & Posts']
)

api.include_router(
    posts.router,
    prefix='/posts',
    tags=['Users & Posts']
)


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
    fps = []
    if media:  # pragma: no cover
        for i, image in enumerate(media):
            async with aiofiles.open(f"/tmp/app/{run_id}/media/{i}", 'wb') as f:
                await f.write(await image.read())
            ext = os.path.splitext(image.filename)[1]
            fp = f'/images/{run_id}_r{i}{ext}'
            shutil.copy(f"/tmp/app/{run_id}/media/{i}", fp)
            fps.append(
                (fastapi_config['openapi_prefix'] + fp).replace('//', '/'))
    return fps


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
