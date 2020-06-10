from fastapi import Header, HTTPException
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
from typing import NamedTuple
from pytimeparse import parse
from os import environ


class Client(NamedTuple):
    ip: str
    name: str
    access_at: datetime
    unban_at: datetime


class Limiter:
    def __init__(self, host='mongo', port=27017, user='root', passwd='password'):
        self.client = MongoClient(f'mongodb://{user}:{passwd}@{host}:{port}')
        self.db = self.client.user_log
        self.log = self.db.access_log
        if environ.get('API_ENV') == 'TEST':
            self.log.drop()

    def limit(self, name, times=1, per='1 day', duration='1 week'):
        def _inner(x_forwarded_for: str = Header(..., description='To get your IP.')):
            params: Client = self._on_access(name, x_forwarded_for)
            log = self._get_logs(params, per)
            if self._access_on_ban(params):
                print(
                    f'Banned User Request: {x_forwarded_for} ({name}, until: {params.unban_at})')
                raise HTTPException(429)
            elif len(log) >= times:
                unban_at = datetime.utcnow() + self._duration_parse(duration)
                param_dict = params._asdict()
                param_dict.update({'unban_at': unban_at})
                self.log.insert_one(param_dict)
                print(
                    f'Too many Requests: {x_forwarded_for} ({name}, until: {params.unban_at})')
                raise HTTPException(429)
            else:
                self.log.insert_one(params._asdict())
        return _inner

    def _access_on_ban(self, params: Client):
        now = datetime.utcnow()
        return now < params.unban_at

    def _duration_parse(self, duration: str):
        return timedelta(seconds=parse(duration))

    def _on_access(self, name: str, _ip: str):
        ip = _ip.split(', ')[0]
        try:
            last = self.log.find({"ip": ip, 'name': name}).sort(
                'access_at', DESCENDING)[0]
            last['access_at'] = datetime.utcnow()
            del last['_id']
            params = Client(**last)
        except IndexError:
            params = Client(ip=ip, name=name, access_at=datetime.utcnow(
            ), unban_at=datetime(1970, 1, 1, 0, 0, 0))
        return params

    def _get_logs(self, params: Client, duration: str):
        td_duration: timedelta = self._duration_parse(duration)
        return list(self.log.find({'ip': params.ip, 'name': params.name, 'access_at': {
                    '$lt': datetime.utcnow(), '$gte': datetime.utcnow() - td_duration}}))
