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
            return

        msg = envelope.msg
        if msg['process']:
            items = msg['items']

            tracks, failed_ids = self._tracker.track(items)
            msg['tracks'] = tracks
            msg['failed_ids'] = failed_ids

            if self._log:
                for track in tracks:
                    tid = track['tid']
                    logger.info(f'track target: {tid}')

                for failed_id in failed_ids:
                    logger.info(f'track target: {failed_id}')

        self.out.send(envelope)
