#!/usr/bin/env python
# coding=utf-8

from loguru import logger
from megflow import register

from warehouse.track_iou import Tracker


@register(inputs=['inp'], outputs=['out'])
class Track:
    def __init__(self, name, args):
        self.name = name
        self._tracker = Tracker()

        self._log = args['log']

    def exec(self):
        #     msg['data']       -- frame
        #     msg['feeding']    -- feeding args
        #     msg['items']      -- All detected cats
        #     msg['process']    -- process
        # add msg['tracks']     -- all tracked targets
        #     msg['failed_ids'] -- all lost targets
        envelope = self.inp.recv()
        if envelope is None:
            logger.info('stream tracker finish')
            return

        msg = envelope.msg
        if msg['process']:
            if self._log:
                logger.debug(f'↓↓↓↓↓↓-----------track------------------↓↓↓↓↓↓')
            items = msg['items']

            tracks, failed_ids = self._tracker.track(items)
            msg['tracks'] = tracks
            msg['failed_ids'] = failed_ids

            for track in tracks:
                tid = track['tid']
                if self._log:
                    logger.info(f'track target: {tid}')

            for failed_id in failed_ids:
                if self._log:
                    logger.info(f'track target: {failed_id}')

            if self._log:
                logger.debug(f'↑↑↑↑↑↑-----------track------------------↑↑↑↑↑↑')
        self.out.send(envelope)
