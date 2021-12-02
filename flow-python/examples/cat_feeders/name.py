import cv2
import numpy as np
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class Name:
    def __init__(self, name, args):
        self.name = name
        self._cat = dict()

    def exec(self):
        #     msg['data']       -- frame
        #     msg['items']      -- All detected cats
        #     msg['process']    -- process
        #     msg['tracks']     -- all tracked targets
        #     msg['failed_ids'] -- all lost targets
        #     msg['shaper']     -- all tracked crop
        #     msg['features']   -- all crop reid
        #     msg['results']    -- all reid results
        envelope = self.inp.recv()
        if envelope is None:
            return

        msg = envelope.msg
        data = msg['data']
        items = msg['items']

        if 'tracks' in msg:
            tracks = msg['tracks']
            results = msg['results']
            if len(tracks) > 0:
                for track in tracks:
                    tid = track['tid']
                    result = results[tid]
                    name = result["name"]



        msg['data'] = data
        self.out.send(envelope)



