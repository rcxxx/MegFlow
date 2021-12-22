from logging import log
from megflow import register, Envelope
from loguru import logger
from threading import Timer
import Jetson.GPIO as GPIO
                

@register(inputs=['inp'])
class NanoGPIO:
    def __init__(self, name, args):
        self.name = name
        self._gpio = args['gpio']
        self._log = args['log']
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._gpio, GPIO.OUT)

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
            try:
                GPIO.output(self._gpio, GPIO.HIGH)
                def gpio_low(gpio):
                    GPIO.output(gpio, GPIO.LOW)
                t = Timer(gpio_arg[0]/5, gpio_low, (self._gpio))
                t.start()
            finally:
                # 清除设置
                GPIO.cleanup()
        return
            
