import cv2
import numpy as np
from typing import Union
from assistance.array_to_raster import array2Raster
from assistance.read_image import readImage


def closing(im: Union[list, np.ndarray], it: int)->Union[list, np.ndarray]:
    """
    闭运算，先膨胀后腐蚀
    :param im: 读入的影像
    :param it: 迭代的次数
    :return:
    """
    binary_im, im_width, im_height, im_bands = readImage(im, 1)

    # 使用3×3的滤波器
    kernel = np.ones((3, 3), np.uint8)
    # 迭代次数
    count = it
    # 闭运算
    closing_im = cv2.morphologyEx(binary_im, cv2.MORPH_CLOSE, kernel, iterations=count)

    return closing_im


def opening(im: Union[list, np.ndarray], it: int)->Union[list, np.ndarray]:
    """
    开运算，先腐蚀后膨胀
    :param im:读入的影像
    :return:
    """
    binary_im, im_width, im_height, im_bands = readImage(im, 1)

    # 使用3×3的滤波器
    kernel = np.ones((3, 3), np.uint8)
    # 迭代次数
    count = it
    # 开运算
    opening_im = cv2.morphologyEx(binary_im, cv2.MORPH_OPEN, kernel, iterations=count)

    return opening_im


if __name__ == '__main__':
    import os
    os.chdir(r'F:\毕设\数据\Sentinel-2\第一次试验')

    closing_im = closing('binary_0.2_s2_water_0715.tif')
    array2Raster(closing_im, 'closing_binary_0.2_s2_water_0715.tif', refImg='binary_0.2_s2_water_0715.tif')


