#!/usr/bin/env python
# coding=utf-8

from loguru import logger
from megflow import register

from warehouse.track_iou import Tracker


@register(inputs=['inp'], outputs=['out'])
class TrackDEBUG:
    def __init__(self, name, _):
        self.name = name
        self._tracker = Tracker()

    def exec(self):
        envelope = self.inp.recv()
        if envelope is None:
            logger.info('stream tracker finish')
            return

        msg = envelope.msg
        if msg['process']:
            logger.debug(f'↓↓↓↓↓↓-----------track------------------↓↓↓↓↓↓')
            items = msg['items']

            tracks, failed_ids = self._tracker.track(items)
            msg['tracks'] = tracks
            msg['failed_ids'] = failed_ids

            for track in tracks:
                tid = track['tid']
                logger.info(f'track target: {tid}')

            logger.debug(f'failed_ids: {failed_ids}')
            logger.debug(f'↑↑↑↑↑↑-----------track------------------↑↑↑↑↑↑')
        self.out.send(envelope)
