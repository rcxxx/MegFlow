import cv2
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class Capture:
    def __init__(self, name, args):
        logger.info("loading camera/video")
        self.name = name
        self.cap = cv2.VideoCapture(args['cap_id'])
        logger.info("camera/video loaded")

    def imgPreprocess(self, src):
        dst = src
        return dst

    def exec(self):
        ret, src = self.cap.read()
        dst = self.imgPreprocess(src)
        msg = dict()
        msg['data'] = dst
        envelope = Envelope.pack(msg)
        self.out.send(envelope)
