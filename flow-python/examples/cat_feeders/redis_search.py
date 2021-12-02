#!/usr/bin/env python
# coding=utf-8

import base64
import binascii
import json
import redis
import numpy as np
from loguru import logger
from megflow import register


@register(inputs=['inp'], outputs=['out'])
class RedisSearch:
    def __init__(self, name, args):
        logger.info("init redis pool...")
        self.name = name
        self._mode = args['mode']
        self._prefix = args['prefix']
        self._db = dict()

        ip = args['ip']
        port = args['port']
        self._pool = redis.ConnectionPool(host=ip,
                                            port=port,
                                            decode_responses=False)

    def search_key(self, r, feature):
        redis_keys = r.keys(self._prefix + '*')
        for key in redis_keys:
            if key not in self._db:
                try:
                    value_base64 = r.get(key)
                    assert value_base64 is not None
                    self._db[key] = np.frombuffer(
                        base64.b64decode(value_base64), dtype=np.float32)
                except redis.exceptions.ConnectionError as e:
                    logger.error(str(e))
                except binascii.Error as e:
                    logger.error(f'decode feature failed, key {key}, reason {str(e)}')

        assert feature is not None
        if len(self._db) == 0:
            logger.error("feature db empty")
            return {}

        min_dist = float("inf")
        min_key = ''
        for k, v in self._db.items():
            dist = np.linalg.norm(v - feature)
            # logger.info(f'key: {k} dist: {dist}')
            if dist < min_dist:
                min_key = k
                min_dist = dist
        min_key = min_key.decode('utf-8')

        name = min_key.replace(self._prefix, '', 1)
        # send notification
        r.lpush('notification.cat_finder', f'{name} leaving the room')
        return {"name": name, "distance": str(min_dist)}

    def exec(self):
        #     msg['data']       -- frame
        #     msg['items']      -- All detected cats
        #     msg['process']    -- process
        #     msg['tracks']     -- all tracked targets
        #     msg['failed_ids'] -- all lost targets
        #     msg['shaper']     -- all tracked crop
        #     msg['features']   -- all crop reid
        # add msg['results']    -- all reid results
        envelope = self.inp.recv()
        if envelope is None:
            return
        msg = envelope.msg
        items = msg['items']
        assert isinstance(items, list)
        r = redis.Redis(connection_pool=self._pool)

        results = dict()
        if 'tracks' in msg:
            features = msg['features']
            for track in msg['tracks']:
                tid = track['tid']
                results[tid] = self.search_key(r, features[tid])
                logger.info(f'target {tid} result : {results[tid]["name"]}')

        msg['results'] = results
        self.out.send(envelope)
