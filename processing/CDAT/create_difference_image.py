from osgeo import gdal
from assistance.array_to_raster import array2Raster
import numpy as np
from typing import Union
from assistance.read_image import readImage


def create_d(reference_im: str, flooded_img: str)-> Union[list, np.ndarray]:
    """
    create difference image
    :param reference_im: 灾前影像
    :param flooded_img: 灾后影像
    :return:
    """

    if isinstance(reference_im, str):
        # 使用VV的极化方式
        r_im, w1, h1, b1 = readImage(reference_im, 2)
    else:
        print('Please provide the path of image!')
        return []

    if isinstance(flooded_img, str):
        f_im, w2, h2, b2 = readImage(flooded_img, 2)
    else:
        print('Please provide the path of image!')
        return []

    d_img = abs(f_im) - abs(r_im)

    return d_img


if __name__ == '__main__':
    import os
    os.chdir(r'/home/Tuotianyu/NDFI_NDFVI/第八次试验预处理数据/home/Tuotianyu/未预处理S1数据')
    difference_im = create_d('S1B_IW_GRDH_1SDV_20200620T101816_20200620T101851_022116_029F8B_298B.zip.tif',
                             'S1B_IW_GRDH_1SDV_20200714T101817_20200714T101852_022466_02AA36_A270.zip.tif')
    array2Raster(difference_im, '0620_0714_difference_image.tif',
                 refImg='S1B_IW_GRDH_1SDV_20200714T101817_20200714T101852_022466_02AA36_A270.zip.tif')
