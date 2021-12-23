import serial

from megflow import register, Envelope
from loguru import logger

@register(inputs=['inp'], outputs=['out'])
class SerialPort:
    def __init__(self, name, args):
        self.name = name
        self._feeding = [5, 5, 15, 5]
        self._serial_on = args['serial_on']
        if self._serial_on:
            self._serial = serial.Serial(args['port'], baudrate=args['baudrate'], timeout=args['timeout'])
            logger.info(self._serial)
        self._log = args['log']

    def exec(self):
        #     msg['data']       -- frame
        # add msg['feeding']    -- feeding args
        envelope = self.inp.recv()
        if envelope is None:
            return
        
        if self._serial_on:
            str = self._serial.read(6).hex()
            print(str)
            if str is not None:
                if str[0:2] == 'aa' and str[10:12] == 'ff':
                    feeding = []
                    temp = str[2:10]
                    for i in range(0, len(temp), 2):
                        feeding.append(int(temp[i:i+2], 16))
                    self._feeding = feeding

        msg = envelope.msg
        msg['feeding'] = self._feeding
        if self._log:
            logger.info(f'---- {self._feeding} ----')
        self.out.send(envelope)
