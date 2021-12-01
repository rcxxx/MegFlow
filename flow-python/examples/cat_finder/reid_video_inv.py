#!/usr/bin/env python
# coding=utf-8

import numpy as np
from loguru import logger
from megflow import register

from warehouse.reid_alignedreid import PredictorLite


@register(inputs=['inp'], outputs=['out'])
class ReIDVideoINV:
    def __init__(self, name, args):
        logger.info("loading Video ReidINV...")
        self.name = name

        # load ReID model and warmup
        self._model = PredictorLite(path=args['path'],
                                    device=args['device'],
                                    device_id=args['device_id'])
        warmup_data = np.zeros((224, 224, 3), dtype=np.uint8)
        self._model.inference(warmup_data)
        logger.info(" ReIDVideo INV Reid loaded.")

    def exec(self):
        envelope = self.inp.recv()
        if envelope is None:
            logger.warning('reid inp is empty')
            return

        msg = envelope.msg

        logger.debug(f'↓↓↓↓↓↓-----------reid------------------↓↓↓↓↓↓')
        # for crop in image['shaper']:
        # cv2.imwrite(f'reid_video_{envelope.partial_id}.jpg', crop)
        # logger.info(f'envelope id {envelope.partial_id}')

        msg['features'] = []
        if 'crop' in msg:
            msg['feature'] = self._model.inference(msg['crop'])
            logger.info(msg['feature'])

        logger.info(msg['features'])
        logger.debug(f'↑↑↑↑↑↑-----------reid------------------↑↑↑↑↑↑')
        self.out.send(envelope)
