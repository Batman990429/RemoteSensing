from osgeo import gdal
import numpy as np
from assistance.array_to_raster import array2Raster
from assistance.read_image import readImage


def threshold_segmentation(sar_im: str, threshold: float, output: str)->None:
    """
    阈值法提取SAR图像水体
    :param sar_im:
    :param threshold:
    :param output
    :return:
    """
    if isinstance(sar_im, str):
        im, im_width, im_height, im_bands = readImage(sar_im, 2)

        temp = np.zeros((im_height, im_width), np.uint8)

        for i in range(0, im_height):
            for j in range(0, im_width):
                if im[i][j] < threshold:
                    temp[i][j] = 0
                else:
                    temp[i][j] = 1

        array2Raster(temp, output, refImg=sar_im)


if __name__ == '__main__':
    import os
    os.chdir(r'/home/Tuotianyu/NDFI_NDFVI/第三五七九次试验预处理数据/home/Tuotianyu/未预处理S1数据')
    threshold_segmentation('S1B_IW_GRDH_1SDV_20200620T101816_20200620T101851_022116_029F8B_298B.zip.tif', 0.04,
                           '/home/Tuotianyu/数据/最终结果1/thresholdsegmentation_0620.tif')
