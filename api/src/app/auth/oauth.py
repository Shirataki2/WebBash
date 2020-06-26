from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import jwt
import uuid
import secrets
from datetime import timedelta, datetime
import os

config = Config(".env")

oauth = OAuth(config)
oauth.register(
    name='twitter',
    api_base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)


async def authenticate_user(oauth_token: str, oauth_token_secret: str):
    resp = await oauth.twitter.get(
        'account/verify_credentials.json', params={'skip_status': True}, token={
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret
        })
    if resp.status_code == 200:
        data = resp.json()
        avater_url = data['profile_image_url_https']
        if avater_url == "null":  # pragma: no cover
            try:
                avater_url = data['profile_image_url'].replace(
                    'http:', 'https:')
            except:
                avater_url = "https://blog.chomama.jp/wp-content/uploads/2020/06/noimage.jpg"
        return {
            'user_id': data['id'],
            'user_name': data['name'],
            'avater_url': data["profile_image_url_https"]
        }
    else:
        return None


def create_access_token(user_id: int, access_token_expire: timedelta):
    data = {
        'sub': user_id,
        'exp': datetime.utcnow() + access_token_expire,
        'iat': datetime.utcnow(),
        'jti': str(uuid.uuid4())
    }
    access_token = jwt.encode(
        data, key=os.environ['SECRET_KEY'], algorithm=os.environ['AUTH_ALGORITHM']
    )
    refresh_token = secrets.token_hex(128)
    return {
        "access_token": access_token.decode('utf-8'),
        "refresh_token": refresh_token,
        "expires_in": access_token_expire.total_seconds()
    }
