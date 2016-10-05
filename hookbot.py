#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import json
import logging
import requests

import bottle

logging.basicConfig(stream=sys.stderr, format='%(asctime)s [%(name)s:%(levelname)s] %(message)s', level=logging.DEBUG if sys.argv[-1] == '-v' else logging.INFO)

HSession = requests.Session()
app = bottle.Bottle()

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def wrap_attrdict(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = wrap_attrdict(v)
        return AttrDict(obj)
    elif isinstance(obj, list):
        for k, v in enumerate(obj):
            obj[k] = wrap_attrdict(v)
        return obj
    else:
        return obj

class BotAPIFailed(Exception):
    def __init__(self, ret):
        self.ret = ret
        self.description = ret['description']
        self.error_code = ret['error_code']
        self.parameters = ret.get('parameters')

    def __repr__(self):
        return 'BotAPIFailed(%r)' % self.ret

def bot_api(method, **params):
    for att in range(3):
        try:
            req = HSession.post(('https://api.telegram.org/bot%s/' %
                                CFG.apitoken) + method, data=params, timeout=45)
            retjson = req.content
            ret = json.loads(retjson.decode('utf-8'))
            break
        except Exception as ex:
            if att < 1:
                time.sleep((att + 1) * 2)
            else:
                raise ex
    if not ret['ok']:
        raise BotAPIFailed(ret)
    return ret['result']

def load_config():
    return wrap_attrdict(json.load(open('config.json', encoding='utf-8')))

def apply_format(d, *args, **kwargs):
    for k, v in d.items():
        if isinstance(v, str):
            d[k] = v.format(*args, **kwargs)

@app.route('/<mount:path>')
def webhook(mount):
    try:
        hook = CFG.hooks[mount].copy()
        method = hook.pop('method')
    except KeyError:
        bottle.abort(404, "Mountpoint Not Found")
    apply_format(hook, q=bottle.request.query, f=bottle.request.forms)
    try:
        return bot_api(method, **hook)
    except BotAPIFailed as ex:
        bottle.abort(ex.error_code, ex.description)

CFG = load_config()

if __name__ == '__main__':
    bottle.run(app, host='0.0.0.0', port=8080)
