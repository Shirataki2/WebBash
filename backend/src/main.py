import responder
import aiohttp
import asyncio
import json
import os
import base64
import binascii
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from asyncio import sleep


api = responder.API(
    static_dir='./static',
    templates_dir='./static'
)

host_prefix = os.environ['HOSTNAME']


class BytesJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return base64.b64encode(o).decode('utf-8')
        return super().default(o)


@api.route("/ping")
async def index(req, resp):
    await sleep(1)
    status = {
        "status": "Web Server Working"
    }
    resp.headers = {"Content-Type": "application/json; charset=utf-8"}
    resp.content = json.dumps(status, ensure_ascii=False)


@api.route("/")
def index(req: responder.Request, resp: responder.Response):
    if req.method != 'get':
        resp.status_code = 405
    else:
        resp.content = api.template('index.html')


@api.route("/run")
async def run(req: responder.Request, resp: responder.Response):
    if req.method != 'post':
        resp.status_code = 405
    else:
        data = await req.media(format='files')
        print('*' * 8 + '[CODE START]' + '*' * 8)
        print(data['source'].decode('utf-8', 'ignore'))
        print('*' * 8 + ' [CODE END] ' + '*' * 8)
        src = {
            "code": data['source'],
            "files": json.dumps(data, cls=BytesJSONEncoder),
            "image": "theoldmoon0602/shellgeibot:latest",
            "filename": "Main.sh",
            "command": "./Main.sh",
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.post(f'http://api/run_code', data=src) as response:
                data = await response.json()
                resp.status_code = response.status
        if response.status == 200:
            data['images'] = list(
                map(lambda path: host_prefix + path, data['images'])
            )
        resp.content = json.dumps(data, ensure_ascii=False)


if __name__ == "__main__":
    api.run(port=30000, address="0.0.0.0", debug=True)
