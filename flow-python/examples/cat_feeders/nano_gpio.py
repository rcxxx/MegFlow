from logging import log
import time
from megflow import register, Envelope
from loguru import logger


@register(inputs=['inp'])
class NanoGPIO:
    def __init__(self, name, args):
        self.name = name
        
        self._nano = args['nano']
        self._gpio = args['gpio']
        self._log = args['log']

    def exec(self):
        #logger.debug(f'gpio in')
        envelope = self.inp.recv()
        
        if envelope is None:
            logger.debug('envelope is none')
            return
        
        msg = envelope.msg
        if 'gpio_arg' in msg:
            gpio_arg = msg['gpio_arg']
            if self._log:
                logger.debug(f'gpio in')
                logger.info(f'{gpio_arg}')
            if self._nano:
                import Jetson.GPIO as GPIO
                GPIO.setmode(GPIO.BOARD)
                GPIO.setup(self._gpio, GPIO.OUT)
                try:
                    GPIO.output(self._gpio, GPIO.HIGH)
                    time.sleep(gpio_arg[0]/5)
                    GPIO.output(self._gpio, GPIO.LOW)
                    time.sleep(2)
                finally:
                    # 清除设置
                    GPIO.cleanup()
                GPIO.cleanup()
        return
            
