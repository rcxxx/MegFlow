from loguru import logger
from megflow import register
from warehouse.quality_naive import Quality

@register(inputs=['inp'], outputs=['out'])
class ShaperINV:
    def __init__(self, name, args):
        self.name = name
        self._mode = args['mode']
        self._map = dict()

    def expand(self, box, max_w, max_h, ratio):
        l = box[0]
        r = box[2]
        t = box[1]
        b = box[3]
        center_x = (l + r) / 2
        center_y = (t + b) / 2
        w_side = (r - l) * ratio / 2
        h_side = (b - t) * ratio / 2

        l = center_x - w_side
        r = center_x + w_side
        t = center_y - h_side
        b = center_y + h_side
        l = max(0, l)
        t = max(0, t)
        r = min(max_w, r)
        b = min(max_h, b)
        return int(l), int(t), int(r), int(b)

    def exec(self):
        envelope = self.inp.recv()
        if envelope is None:
            self._map.clear()
            return

        msg = envelope.msg

        if 'tracks' in msg:
            for track in msg['tracks']:
                tid = track['tid']
                box = track['bbox']
                if tid not in self._map:
                    self._map[tid] = envelope.repack(msg)

                    data = msg['data']
                    l, t, r, b = self.expand(box, data.shape[1], data.shape[0], 1.1)
                    crop = data[t:b, l:r]
                    assert crop is not None

                    self._map[tid].msg['crop'] = crop
                    self.out.send(self._map[tid])

                    logger.info(f'shaper: {tid}')
                    logger.debug(f'↑↑↑↑↑↑-----------shaper------------------↑↑↑↑↑↑')
                    return
                else:
                    logger.info(f'target {tid} has been shape')

            self.out.send(envelope)
            logger.debug(f'↑↑↑↑↑↑-----------shaper------------------↑↑↑↑↑↑')

            # logger.debug(f'↓↓↓↓↓↓-----------shaper------------------↓↓↓↓↓↓')
            # logger.debug(f'↑↑↑↑↑↑-----------shaper------------------↑↑↑↑↑↑')



