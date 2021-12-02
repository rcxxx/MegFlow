#!/usr/bin/env python
# coding=utf-8

import numpy as np
from loguru import logger
from megflow import register

from warehouse.reid_alignedreid import PredictorLite


@register(inputs=['inp'], outputs=['out'])
class ReID:
    def __init__(self, name, args):
        logger.info("loading Video ReidINV...")
        self.name = name
        self._features = dict()

        # load ReID model and warmup
        self._model = PredictorLite(path=args['path'],
                                    device=args['device'],
                                    device_id=args['device_id'])
        warmup_data = np.zeros((224, 224, 3), dtype=np.uint8)
        self._model.inference(warmup_data)
        logger.info(" ReIDVideo INV Reid loaded.")

    def exec(self):
        #     msg['data']       -- frame
        #     msg['items']      -- All detected cats
        #     msg['process']    -- process
        #     msg['tracks']     -- all tracked targets
        #     msg['failed_ids'] -- all lost targets
        #     msg['shaper']     -- all tracked crop
        # add msg['features']   -- all crop reid
        envelope = self.inp.recv()
        if envelope is None:
            logger.warning('reid inp is empty')
            self._features.clear()
            return

        msg = envelope.msg

        logger.debug(f'↓↓↓↓↓↓-----------reid------------------↓↓↓↓↓↓')

        if 'tracks' in msg:
            shaper = msg['shaper']
            for track in msg['tracks']:
                tid = track['tid']
                if tid not in self._features:
                    crop = shaper[tid]
                    feature = self._model.inference(crop)
                    self._features[tid] = feature
                    logger.info(f'target {tid} features: {feature}')
                else:
                    logger.info(f'target {tid} is being reid , feature: {self._features[tid]}')

        if 'failed_ids' in msg:
            fids = msg['failed_ids']
            if len(fids) > 0:
                for fid in fids:
                    if fid in self._features:
                        self._features.pop(fid)

        logger.debug(f'↑↑↑↑↑↑-----------reid------------------↑↑↑↑↑↑')
        msg['features'] = self._features
        self.out.send(envelope)
