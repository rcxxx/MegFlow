import time
import redis
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out', 'food'])
class Feeder:
    def __init__(self, name, args):
        logger.info("init Feeder")
        self.name = name
        self._pool = redis.ConnectionPool(host=args['ip'], port=args['port'], decode_responses=False)
        self._r = redis.Redis(connection_pool=self._pool)

        self._cat = dict()
        self._fed = dict()
        self._preset_time = args['preset_time']     # 每次投喂的时间间隔 / h
        self._cat_wait_time = args['cat_wait_time'] # 猫咪停留的时间    / s

        self._log = args['log']
    
    def isFeeding(self, name, time, feeding_times):
        last_t_fmt = self.formatTimestamp(float(self._r.get(f'{name}.feeding.last_t')))
        current_t_fmt = self.formatTimestamp(time)
        new_date = (current_t_fmt[0] - last_t_fmt[0]) + (current_t_fmt[1] - last_t_fmt[1]) + (current_t_fmt[2] - last_t_fmt[2])
        if new_date > 0:
            # 日期超过一天
            self._r.set(f'{name}.feeding.times', 0)

        times = int(self._r.get(f'{name}.feeding.times'))
        if ((current_t_fmt[3] - last_t_fmt[3]) >= self._preset_time or new_date) and (times < feeding_times):
            self._r.set(f'{name}.feeding.last_t', time)
            self._r.set(f'{name}.feeding.times', (times + 1))
            return True

        return False

    def formatTimestamp(self, _time):
        local_time = time.localtime(_time)
        year = int(time.strftime('%Y', local_time))
        month = int(time.strftime('%m', local_time))
        day = int(time.strftime('%d', local_time))
        hour = int(time.strftime('%H', local_time))
        timestamp = [year, month, day, hour]
        return timestamp

    def time_diff(self, _time_1, _time_2):
        c_minute = int(time.strftime('%M', time.localtime(_time_1)))
        c_second = int(time.strftime('%S', time.localtime(_time_1)))
        s_minute = int(time.strftime('%M', time.localtime(_time_2)))
        s_second = int(time.strftime('%S', time.localtime(_time_2)))
        t_diff = (c_minute - s_minute) * 60 + (c_second - s_second)
        return t_diff

    def exec(self):
        envelope = self.inp.recv()
        if envelope is None:
            self._cat.clear()
            return

        # 读取当前时间并对比上次喂食时间，判断时间间隔是否超过预设时间，控制喂食开关
        current_time = time.time()

        msg = envelope.msg

        # 当画面中有猫并且符合时间管理
        if 'tracks' in msg and self._is_feeding:
            tracks = msg['tracks']
            cats = msg['cats']
            # 保证只有一只猫时才喂食
            if len(tracks) < 2:
                for track in tracks:
                    tid = track['tid']
                    cat = cats[tid]
                    if (cat[0] == 'Danta') or (cat[0] == 'Tansuan'):
                        # 判断猫咪在猫粮机前停留的时间
                        if tid not in self._cat:
                            # 猫咪第一次出现的时间
                            self._cat[tid] = current_time
                        else:
                            start_time = float(self._cat[tid])
                            stay_time = self.time_diff(current_time, start_time)
                            if stay_time >= self._cat_wait_time:
                                # 猫咪停留超过预设时间，设置当前时间为上一次喂食的时间
                                if tid not in self._fed:
                                    self._fed[tid] = "fed"
                                    cat_name = cat[0]
                                    if self.isFeeding(cat[0], current_time, cat[2]):
                                        io_msg = dict()
                                        gpio_arg = [cat[1], cat[2]]
                                        io_msg['gpio_arg'] = gpio_arg
                                        self.food.send(Envelope.pack(io_msg))
                                        if self._log:
                                            logger.debug(f'Start feeding {cat[0]}')
                                else:
                                    if self._log:
                                        logger.debug(f'{cat[0]} has been fed')

        if 'failed_ids' in msg:
            fids = msg['failed_ids']
            if len(fids) > 0:
                for fid in fids:
                    if fid in self._cat:
                        self._cat.pop(fid)
                    if fid in self._fed:
                        self._fed.pop(fid)

        self.out.send(envelope)
