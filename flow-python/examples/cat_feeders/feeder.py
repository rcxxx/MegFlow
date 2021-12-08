import time
import redis
from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class Feeder:
    def __init__(self, name, args):
        self.name = name
        self._pool = redis.ConnectionPool(host=args['ip'], port=args['port'], decode_responses=False)
        self._r = redis.Redis(connection_pool=self._pool)
        self._last_feeding_time = self.formatTimestamp(float(self._r.get('time')))
        logger.info("init Feeder")
        logger.info(f'last feeding time: {self._last_feeding_time}')

        self._cat = dict()
        self._is_feeding = True
        self._preset_time = args['preset_time']     # 每次投喂的时间间隔 / h
        self._cat_wait_time = args['cat_wait_time'] # 猫咪停留的时间    / s

        self._amount_dt = args['amount_dt']         # 蛋挞 每次投喂量   / g
        self._times_dt = args['times_dt']           # 蛋挞 每天投喂次数 / 次
        self._amount_ts = args['amount_ts']         # 碳酸 每次投喂量   / g
        self._times_ts = args['times_ts']           # 碳酸 每天投喂次数 / 次

        self._log = args['log']


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
        current_timestamp = self.formatTimestamp(current_time)
        new_date = (current_timestamp[0] - self._last_feeding_time[0]) \
            + (current_timestamp[1] - self._last_feeding_time[1]) \
            + (current_timestamp[2] - self._last_feeding_time[2])

        # 当前时间减去上次喂食时间，如果日期间隔一天以上，则重置所有与喂食限制有关的参数
        if new_date > 0:
            pass
            # reset args
        else:
            # 时间在同一天，则判断间隔多少小时
            if (current_timestamp[3] - self._last_feeding_time[3]) >= self._preset_time:
                # 超过预设时间间隔，可以喂食
                self._is_feeding = True
            else:
                self._is_feeding = False

        msg = envelope.msg

        # 当画面中有猫并且符合时间管理
        if 'tacks' in msg and self._is_feeding:
            tracks = msg['tracks']
            cats = msg['cats']
            # 保证只有一只猫时才喂食
            if len(tracks) < 2:
                for track in tracks:
                    tid = track['tid']
                    cat = cats[tid]
                    # 判断猫咪在猫粮机前停留的时间
                    if tid not in self._cat:
                        self._cat[tid] = current_time       # 猫咪第一次出现的时间
                    else:
                        start_time = float(self._cat[tid])
                        stay_time = self.time_diff(current_time, start_time)

                        if stay_time >= self._cat_wait_time:
                            # 猫咪停留超过预设时间，设置当前时间为上一次喂食的时间
                            # self._r.set('time', current_time)
                            self._last_feeding_time = self.formatTimestamp(current_time)

        if 'failed_ids' in msg:
            fids = msg['failed_ids']
            if len(fids) > 0:
                for fid in fids:
                    if fid in self._cat:
                        self._cat.pop(fid)

        self.out.send(envelope)
