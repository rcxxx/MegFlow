import cv2
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class Display:
    def __init__(self, name, args):
        self.name = name
        self._show = args['show_img']

    def exec(self):
        envelope = self.inp.recv()
        if envelope is None:
            return

        if self._show:
            msg = envelope.msg
            dst = msg['data']
            cv2.imshow("dst", dst)
            logger.debug("results shown as dst")
            cv2.waitKey(1)

        self.out.send(envelope)
