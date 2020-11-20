from osgeo import gdal
import numpy as np
import math


def cal_ndfi_threshold(ndfi_im: str)->float:
    """
    计算NDFI图像的阈值
    :param ndfi_im:
    :return:
    """

    if isinstance(ndfi_im, str):
        data_set = gdal.Open(ndfi_im)
    else:
        print('You should provide the path of NDFI')
        return 0.0

    # 读取NDFI图像的行列数和波段数
    im_width = data_set.RasterXSize
    im_height = data_set.RasterYSize
    im_bands = data_set.RasterCount
    print('width:', im_width, 'height:', im_height, 'bands_num:', im_bands)

    # 存储像素值
    im_array = []
    if im_bands == 1:
        im = data_set.ReadAsArray()
    else:
        band = data_set.GetRasterBand(1)
        im = band.ReadAsArray()
        del band

    del data_set

    im_array.append(im)

    # 求平均值和标准差的时候要去除掉倾斜像素和0值像素
    # 求ndfi图像的平均值
    total = 0
    count1 = 0
    for i in range(0, im_height):
        for j in range(0, im_width):
            if im_array[0][i][j] != 0:
                total = total + im_array[0][i][j]
                count1 = count1 + 1

    print('count1:', count1)
    mean = total / count1

    print("mean:", mean)

    # 求标准差
    temp = 0
    count2 = 0
    for i in range(0, im_height):
        for j in range(0, im_width):
            if im_array[0][i][j] != 0:
                temp = temp + (im_array[0][i][j] - mean) * (im_array[0][i][j] - mean)
                count2 = count2 + 1

    print('count:', count2)
    std = math.sqrt(temp / count2)
    print(std)

    return mean - 1.5 * std


def cal_ndfvi_threshold(ndfvi_im: str)->float:
    """
        计算NDFI图像的阈值
        :param ndfi_im:
        :return:
        """

    if isinstance(ndfvi_im, str):
        data_set = gdal.Open(ndfvi_im)
    else:
        print('You should provide the path of NDFI')
        return 0.0

    # 读取NDFI图像的行列数和波段数
    im_width = data_set.RasterXSize
    im_height = data_set.RasterYSize
    im_bands = data_set.RasterCount
    print('width:', im_width, 'height:', im_height, 'bands_num:', im_bands)

    # 存储像素值
    im_array = []
    if im_bands == 1:
        im = data_set.ReadAsArray()
    else:
        band = data_set.GetRasterBand(1)
        im = band.ReadAsArray()
        del band

    del data_set

    im_array.append(im)

    # 求ndfi图像的平均值
    total = 0
    count1 = 0
    for i in range(0, im_height):
        for j in range(0, im_width):
            if im_array[0][i][j] != 0:
                total = total + im_array[0][i][j]
                count1 = count1 + 1

    print('count1:', count1)
    mean = total / count1

    print("mean:", mean)

    # 求标准差
    temp = 0
    count2 = 0
    for i in range(0, im_height):
        for j in range(0, im_width):
            if im_array[0][i][j] != 0:
                temp = temp + (im_array[0][i][j] - mean) * (im_array[0][i][j] - mean)
                count2 = count2 + 1

    print('count:', count2)
    std = math.sqrt(temp / count2)
    print(std)

    return mean + 1.5 * std


if __name__ == '__main__':
    import os
    os.chdir(r'/home/Tuotianyu/数据/CDAT/第一次试验')
    ndfvi = '0620_0714_difference_image.tif'
    print('threshold:', cal_ndfvi_threshold(ndfvi))


