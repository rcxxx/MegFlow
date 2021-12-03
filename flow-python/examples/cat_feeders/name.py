import cv2
import numpy as np
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class Name:
    def __init__(self, name, args):
        self.name = name

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
                    box = track['bbox']
                    name = results[tid]["name"]

                    tl_x = int(box[0])
                    tl_y = int(box[1])
                    br_x = int(box[2])
                    br_y = int(box[3])
                    w = br_x - tl_x
                    h = br_y - tl_y

                    cv2.rectangle(data, (tl_x, tl_y), (br_x, br_y), (220, 255, 20), 2)
                    text = '{}'.format(name)

                    put_x = int(tl_x + w * 0.06)
                    put_y = int(tl_y - h * 0.02)
                    cv2.putText(data, text, (put_x, put_y), cv2.FONT_HERSHEY_COMPLEX, 1, (220, 255, 20), 2)

        msg['data'] = data
        self.out.send(envelope)



