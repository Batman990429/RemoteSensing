from osgeo import gdal
from typing import Union
import numpy as np
from assistance.array_to_raster import array2Raster
from assistance.raster_to_binary import raster2binary


def ndwi(image: str)->Union[list, np.ndarray]:
    """
    用哨兵二号数据计算NDWI，识别水体
    :param image:
    :return:
    """
    if isinstance(image, str):
        data_set = gdal.Open(image)

        im_width = data_set.RasterXSize
        im_height = data_set.RasterYSize
        im_bands = data_set.RasterCount
        print('im_width:', im_width, 'im_height:', im_height, 'bands_num:', im_bands)

        # 绿色波段
        g = data_set.GetRasterBand(3).ReadAsArray()
        # 近红外波段
        nir = data_set.GetRasterBand(8).ReadAsArray()

        return (g - nir) / (g + nir)
    else:
        print('please provide the path of image')

        return []


if __name__ == '__main__':
    import os
    os.chdir(r'/home/Tuotianyu/数据/水体提取/Sentinel-2/第一次试验')
    image = 'S2A_MSIL2A_20200715T024551_N0214_R132_T50RMT_20200715T084024_s2resampled.tif'
    ndwi = ndwi(image)
    array2Raster(ndwi, 's2_water_0715', refImg='S2A_MSIL2A_20200715T024551_N0214_R132_T50RMT_20200715T084024_s2resampled.tif')
    # 根据阈值将其转换为二值图像
    raster2binary('s2_water_0715', 0.2)










