import cv2
import numpy as np
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class Name:
    def __init__(self, name, args):
        self.name = name
        self._cat_dt = ["danta", "danta_1", "danta_2", "danta_3", "danta_4",
                        "danta_5", "danta_6", "danta_7", "danta_8", "danta_9"]
        self._cat_ts = ["tansuan", "tansuan_1", "tansuan_2", "tansuan_3", "tansuan_4",
                        "tansuan_5", "tansuan_6", "tansuan_7", "tansuan_8", "tansuan_9"]

        self._log = args['log']
        self._cats = dict()

    def exec(self):
        #     msg['data']       -- frame
        #     msg['feeding']    -- feeding args
        #     msg['items']      -- All detected cats
        #     msg['process']    -- process
        #     msg['tracks']     -- all tracked targets
        #     msg['failed_ids'] -- all lost targets
        #     msg['shaper']     -- all tracked crop
        #     msg['features']   -- all crop reid
        #     msg['results']    -- all reid results
        # add msg['cat']        -- cat information
        envelope = self.inp.recv()
        if envelope is None:
            return

        msg = envelope.msg
        data = msg['data']
        items = msg['items']

        if 'tracks' in msg:
            tracks = msg['tracks']
            results = msg['results']
            feeding = msg['feeding']
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
                    put_x = int(tl_x + w * 0.06)
                    put_y = int(tl_y - h * 0.02)

                    if name in self._cat_dt:
                        text = 'Dan Ta'
                        cv2.putText(data, text, (put_x, put_y), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
                        self._cats[tid] = [text, feeding[0], feeding[1]]
                    elif name in self._cat_ts:
                        text = 'Tan Suan'
                        cv2.putText(data, text, (put_x, put_y), cv2.FONT_HERSHEY_COMPLEX, 1, (120, 120, 120), 2)
                        self._cats[tid] = [text, feeding[2], feeding[3]]

        msg['data'] = data
        msg['cats'] = self._cats
        if self._log:
            logger.info(msg['cats'])
        self.out.send(envelope)



