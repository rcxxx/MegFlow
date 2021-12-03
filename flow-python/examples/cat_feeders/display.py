import cv2
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class Display:
    def __init__(self, name, args):
        self.name = name
        self._show = args['show_img']

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

        if self._show:
            msg = envelope.msg
            dst = msg['data']
            cv2.imshow("dst", dst)
            # logger.debug("results shown as dst")
            cv2.waitKey(1)

        self.out.send(envelope)
