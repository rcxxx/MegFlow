import cv2
from loguru import logger
from os import path

cap = cv2.VideoCapture(0)
num = 0
name = 'danta'

while True:
    ret, src = cap.read()
    dst = src
    cv2.imshow('dst', dst)
    key = cv2.waitKey(1)

    if key == 27:
        break
    elif key == 49:
        _p = path.dirname(__file__)
        img_name = '{}/img/'.format(_p) + name + '_{}'.format(num) + '.jpg'
        cv2.imwrite(img_name, dst)
        num += 1
        logger.debug(f'save img to {img_name}')
        logger.info(f' save:"1"  danta:"2  tansuan:"3"' )
    elif key == 50:
        name = 'danta'
        num = 0
        logger.debug(f'change cat name {name}')
        logger.info(f' save:"1"  danta:"2  tansuan:"3"' )
    elif key == 51:
        name = 'tansuan'
        num = 0
        logger.debug(f'change cat name {name}')
        logger.info(f' save:"1"  danta:"2  tansuan:"3"' )

cv2.destroyAllWindows()
