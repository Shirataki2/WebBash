import datetime
import responder
from typing import NamedTuple
import pymongo


class Client(NamedTuple):
    ip: str
    uri: str
    access_at: datetime.datetime
    unban_at: datetime.datetime
    perm_banned: bool
    unavail_count: int
    ban_count: int


def banned(req: responder.Request, resp: responder.Response):
    resp.text = 'You\'re banned for several days!'
    resp.status_code = 403


def perm_banned(req: responder.Request, resp: responder.Response):
    resp.text = 'You\'re PERMANENTLY banned!'
    resp.status_code = 403


def unavail(req: responder.Request, resp: responder.Response):
    resp.text = 'Access from your IP is temporarily restricted due to excessive access.'
    resp.status_code = 503


class Limiter:
    def __init__(self, host='mongo', port=27017, user='root', passwd='password'):
        self.client = pymongo.MongoClient(
            f'mongodb://{user}:{passwd}@{host}:{port}')
        self.access_log = self.client.access_log
        self.history = self.access_log.history
        # self.history.drop()

    def limit(self, num, sec, uri, ban_thres=7, permban_thres=3, ban_duration=datetime.timedelta(days=7)):
        def _middle(func):
            async def _inside(req, resp, **kwargs):
                try:
                    client_ip = dict(req.headers)['x-forwarded-for']
                except KeyError:
                    print('Failed to Get Client IP')
                    print(dict(req.headers))
                try:
                    client_ip = client_ip.split(', ')[0]
                except:
                    client_ip = client_ip
                params = {}
                try:
                    last = self.history.find({"ip": client_ip, 'uri': uri}).sort(
                        'access_at', pymongo.DESCENDING)[0]
                    params.update({
                        'ip': client_ip,
                        'uri': uri,
                        'access_at': datetime.datetime.utcnow(),
                        'unban_at': last['unban_at'],
                        'perm_banned': last['perm_banned'],
                        'unavail_count': last['unavail_count'],
                        'ban_count': last['ban_count'],
                    })
                except IndexError:
                    params.update({
                        'ip': client_ip,
                        'uri': uri,
                        'access_at': datetime.datetime.utcnow(),
                        'unban_at': datetime.datetime(1970, 1, 1, 0, 0, 0, 0),
                        'perm_banned': False,
                        'unavail_count': 0,
                        'ban_count': 0,
                    })
                if params['access_at'] < params['unban_at']:
                    print('Ban! {client_ip} - {uri}')
                    banned(req, resp)
                    return
                if params['perm_banned']:
                    print('Perm Ban! {client_ip} - {uri}')
                    banned(req, resp)
                    return
                end = datetime.datetime.now()
                start = end - datetime.timedelta(seconds=sec)
                access_log = list(self.history.find({'ip': client_ip, 'uri': uri, 'access_at': {
                    '$lt': end, '$gte': start}}))
                # print(params)
                f = False
                if len(access_log) >= num:
                    print(f'Unavail! {client_ip} - {uri}')
                    params['unavail_count'] += 1
                    f = True
                    unavail(req, resp)
                    return
                if params['unavail_count'] >= ban_thres:
                    print(f'Ban! {client_ip} - {uri}')
                    params['unban_at'] = datetime.datetime.now() + \
                        ban_duration
                    params['unavail_count'] = 0
                    params['ban_count'] += 1
                    f = True
                    banned(req, resp)
                if params['ban_count'] >= permban_thres:
                    print(f'Perm Ban! {client_ip} - {uri}')
                    params['perm_banned'] = True
                    f = True
                    banned(req, resp)
                self.history.insert_one(params)
                if not f:
                    await func(req, resp, **kwargs)
            return _inside
        return _middle
