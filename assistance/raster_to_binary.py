from osgeo import gdal
from typing import Union
import numpy as np
from assistance.array_to_raster import array2Raster
from assistance.read_image import readImage


def raster2binary(image: str, threshold: float)->Union[list, np.ndarray]:
    """
    根据阈值将图像转换为二值影像
    :param image:
    :param threshold:
    :return:
    """
    if isinstance(image, str):
        im, im_width, im_height, im_bands = readImage(image, 1)

        temp = np.zeros((im_height, im_width), np.uint8)

        for i in range(0, im_height):
            for j in range(0, im_width):
                if im[i][j] >= threshold:
                    temp[i][j] = 1
                else:
                    temp[i][j] = 0

        return temp
    else:
        print('please provide the path of image!')
        return []


if __name__ == '__main__':
    import os
    os.chdir(r'F:\毕设\数据\第三次试验')
    binary_im = raster2binary('ndfi_0608_0620_0702_0714_0720.tif', 0.7)
    array2Raster(binary_im, 'binary_0.7_ndfi_0608_0620_0702_0714_0720.tif', refImg='ndfi_0608_0620_0702_0714_0720.tif')
