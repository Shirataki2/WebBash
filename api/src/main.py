import responder
import json
import shutil
import os
import urllib.parse
import hashlib
import binascii
import secrets
import base64
import glob
import shutil
from time import sleep, perf_counter
import docker
from docker import types
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


api = responder.API()
docker_client = docker.from_env()
CONTENTTYPES = {
    'plain': 'text/plain',
    'csv': 'text/csv',
    'html': 'text/html',
    'js': 'text/javascript',
    'json': 'application/json',
    'pdf': 'application/pdf',
    'xlsx': 'application/vnd.ms-excel',
    'ppt': 'application/vnd.ms-powerpoint',
    'docx': 'application/msword',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'bmp': 'image/bmp',
    'zip': 'application/zip',
    'tar': 'application/x-tar'
}


@api.route("/ping")
def ping(req, resp):
    sleep(1)
    status = {
        "status": "API Server Working"
    }
    resp.headers = {"Content-Type": "application/json; charset=utf-8"}
    resp.content = json.dumps(status, ensure_ascii=False)


@api.route("/images/{path}")
async def image(req: responder.Request, resp: responder.Response, *, path):
    if req.method != 'get':
        resp.status_code = 405
    else:
        def readf(fp):
            fp = './images/' + fp
            with open(fp, 'rb') as f:
                dt = f.read()
            return dt
        downloadfilename = urllib.parse.unquote(path, 'utf-8')
        ext = os.path.splitext(downloadfilename)[1][1:]
        resp.headers['Content-Type'] = CONTENTTYPES.get(ext)
        resp.headers['Content-Disposition'] = 'attachment; filename=' + path
        resp.content = readf(downloadfilename)


@api.route("/run_code")
async def run(req: responder.Request, resp: responder.Response):
    if req.method != 'post':
        resp.status_code = 405
    else:
        src = await req.media()
        print(src)
        if not {'image', 'filename', 'code', 'command'}.issubset(set(src.keys())):
            resp.status_code = 400
            return
        container_list = docker_client.containers.list(
            filters={'ancestor': src['image']}
        )
        if len(container_list) > 10:
            resp.status_code = 503
            return
        run_id = secrets.token_hex(8)
        os.makedirs(f'/tmp/app/{run_id}')
        os.makedirs(f'/tmp/app/{run_id}/media')
        with open(f'/tmp/app/{run_id}/{src["filename"]}', 'w') as f:
            f.write(src['code'])
        file_i = 0
        files = json.loads(src['files'])
        for k, v in files.items():
            print(k)
            if k in ['file_0', 'file_1', 'file_2', 'file_3']:
                raw_data = v['content']
                with open(f'/tmp/app/{run_id}/media/{file_i}', 'wb') as f:
                    bin_data = base64.b64decode(raw_data)
                    f.write(bin_data)
                file_i += 1
        container = docker_client.containers.run(
            src['image'],
            command=f"bash",
            stdout=False,
            stderr=False,
            detach=True,
            remove=True,
            name=f"{run_id}",
            tty=True,
            environment={"LANG": "ja_JP.UTF-8"},
            network_disabled=True,
            network_mode='none',
            pids_limit=128,
            mem_limit='256m',
            memswap_limit='256m',
            shm_size='256m',
            cpuset_cpus='0,1',
            cpu_period=50000,
            cpu_quota=40000,
            oom_kill_disable=True,
            working_dir=f'/tmp/app',
            volumes={
                f'/tmp/app/{run_id}': {'bind': f'/tmp/app/{run_id}', 'mode': 'rw'},
                f'/tmp/app/{run_id}/images': {'bind': '/images', 'mode': 'rw'},
                f'/tmp/app/{run_id}/media': {'bind': '/media', 'mode': 'rw'}
            },
            ulimits=[
                types.Ulimit(name='fsize', soft=5000000, hard=5000000)
            ]
        )
        try:
            start = perf_counter()
            (exit_code, (stdout, stderr)) = container.exec_run(
                # rm -rf /tmp/app/{run_id}
                cmd=f"timeout 20s bash -c \"{src['command']}\"",
                workdir=f'/tmp/app/{run_id}',
                demux=True
            )
            dur = perf_counter() - start

            def decode(s):
                s = s.decode('utf-8', "replace") if s else ""
                if len(s.split('\n')) > 20:
                    s = '\n'.join(s.split('\n')[:20]) + "\n..."
                if len(s) > 500:
                    s = s[:500] + "\n..."
                return s
            images = glob.glob(f'/tmp/app/{run_id}/images/**.png')
            images.extend(glob.glob(f'/tmp/app/{run_id}/images/**.jpg'))
            images.extend(glob.glob(f'/tmp/app/{run_id}/images/**.gif'))
            images.extend(glob.glob(f'/tmp/app/{run_id}/images/**.jpeg'))
            fps = []
            if images:
                for i, image in enumerate(sorted(images)[:4]):
                    ext = os.path.splitext(image)[1]
                    fp = f'images/{run_id}_{secrets.token_hex(24)}{ext}'
                    shutil.copy(image, './' + fp)
                    fps.append('/' + fp)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            resp.headers = {"Content-Type": "application/json; charset=utf-8"}
            resp.content = json.dumps({
                "sec": f"{dur:.3f} sec.",
                "exit_code": exit_code,
                "stdout": decode(stdout),
                "stderr": decode(stderr),
                "images": fps
            }, ensure_ascii=False)
        finally:
            container.exec_run(
                cmd=f"rm -rf /tmp/app/{run_id};rm -rf /images",
                workdir=f'/tmp/app'
            )
            container.kill()

if __name__ == "__main__":
    api.run(port=32000, address="0.0.0.0", debug=True)
