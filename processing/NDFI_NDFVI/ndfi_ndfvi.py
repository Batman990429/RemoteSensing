from osgeo import gdal
import numpy as np
from typing import Union
from assistance.array_to_raster import array2Raster
from assistance.raster_to_binary import raster2binary
import cv2
from assistance.read_image import readImage
from NDFI_NDFVI.contours import erase_small_area


def ndfi(pre_images: Union[str, list], post_images: Union[str, list])->Union[np.ndarray, list]:
    """
    有灾前灾后图像计算NDFI，要求所有数据在空间上是对齐的
    :param pre_images:
    :param post_images:
    :return:
    """

    # 存储灾前灾后影像的像素值
    pre_array = []
    post_array = []

    for img in pre_images:
        if isinstance(img, str):
            im, im_width, im_height, im_bands = readImage(img, 2)
        pre_array.append(im)

    for img in post_images:
        if isinstance(img, str):
            im, im_width, im_height, im_bands = readImage(img, 2)
        post_array.append(im)

    min_ref_flood = np.amin(pre_array + post_array, 0)
    mean_ref = np.mean(pre_array, 0)

    # 分析NDFI结果
    # 找出后向散射系数均值小于0.015
    # 最小值大于0.03的
    mean_it = np.ones((im_height, im_width), np.uint8)
    min_gt = np.ones((im_height, im_width), np.uint8)
    for i in range(0, im_height):
        for j in range(0, im_width):
            if mean_ref[i][j] <= 15e-3:
                mean_it[i][j] = 0
            else:
                mean_it[i][j] = 1

            if min_ref_flood[i][j] >= 3e-2:
                min_gt[i][j] = 0
            else:
                min_gt[i][j] = 1

    # 保存后向散射系数均值小于0.015和最小值大于0.03的为二值图像之后用作掩膜
    array2Raster(mean_it, '/home/Tuotianyu/数据/paper_based/mean_it_0.015_0608_0620_0714_0720.tif',
                 refImg='S1B_IW_GRDH_1SDV_20200608T101815_20200608T101851_021941_029A3A_7867.zip.tif')
    array2Raster(min_gt, '/home/Tuotianyu/数据/paper_based/min_gt_0.015_0608_0620_0714_0720.tif',
                 refImg='S1B_IW_GRDH_1SDV_20200608T101815_20200608T101851_021941_029A3A_7867.zip.tif')

    return (mean_ref - min_ref_flood) / (mean_ref + min_ref_flood)


def ndfvi(pre_images: Union[str, list], post_images: Union[str, list])->Union[np.ndarray, list]:
    """
    有灾前灾后图像计算NDFVI，要求所有数据在空间上是对齐的
    :param pre_images:
    :param post_images:
    :return:
    """

    # 存储灾前灾后影像的像素值
    pre_array = []
    post_array = []

    for img in pre_images:
        if isinstance(img, str):
            im, im_width, im_height, im_bands = readImage(img, 2)
        pre_array.append(im)

    for img in post_images:
        if isinstance(img, str):
            im, im_width, im_height, im_bands = readImage(img, 2)
        post_array.append(im)

    max_ref_flood = np.amax(pre_array + post_array, 0)
    mean_ref = np.mean(pre_array, 0)

    return (max_ref_flood - mean_ref) / (mean_ref + max_ref_flood)


def ndfi_post_process(im: str, mean_it: str, min_gt: str, output: str)->None:
    """
    对的得到的ndfi经阈值划分后的二值图像进行后处理
    通过得到的掩膜图像去除后向散射系数均值小于0.015的和最小值大于0.03的
    再进行开运算
    :param im:
    :param mean_it:
    :param min_gt:
    :param output
    :return:
    """
    ndfi, im_width, im_height, im_bands = readImage(im, 1)

    mean_it, mean_width, mean_height, mean_bands = readImage(mean_it, 1)

    min_gt, min_width, min_height, min_bands = readImage(min_gt, 1)

    # 去除后向散射均值小于0.015（可认定为永久水体的部分）
    # 去除后向散射最小值大于0.3（在洪涝中发生了什么，但没有达到受灾的水平）
    temp = np.zeros((im_height, im_width), np.uint8)
    for i in range(0, im_height):
        for j in range(0, im_width):
            if ndfi[i][j] == 1 and mean_it[i][j] == 1 and min_gt[i][j] == 1:
                temp[i][j] = 1
            else:
                temp[i][j] = 0

    array2Raster(temp, output, refImg=im)


def ndfi_post_process2(im: str, output: str, it=1)->None:
    """
    使用形态学处理
    :param im:
    :param it： 迭代的次数
    :param output:
    :return:
    """
    ndfi, im_width, im_height, im_bands = readImage(im, 1)

    # 使用3×3的滤波器
    kernel = np.ones((3, 3), np.uint8)
    # 迭代次数
    count = it
    # 先膨胀
    dilation = cv2.dilate(ndfi, kernel)
    # 闭运算
    closing_im = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations=count)

    array2Raster(closing_im, output, refImg=im)


def ndfi_post_process3(im: str, water: str, output: str)->None:
    """
    使用阈值分割提取的水体对NDFI提取的洪涝结果进行掩膜
    :param im:
    :param water:
    :param output
    :return:
    """

    ndfi, im_width, im_height, im_bands = readImage(im, 1)

    water, im_width2, im_height2, im_bands2 = readImage(water, 1)

    temp = np.zeros((im_height, im_width), np.uint8)
    for i in range(0, im_height):
        for j in range(0, im_width):
            if ndfi[i][j] == 1 and water[i][j] == 1:
                temp[i][j] = 1

    array2Raster(temp, output, refImg=im)


if __name__ == '__main__':
    import os
    os.chdir(r'/home/Tuotianyu/S1_ARD/paper_based_method/home/Tuotianyu/未预处理S1数据')
    pre_image = ['S1B_IW_GRDH_1SDV_20200608T101815_20200608T101851_021941_029A3A_7867.zip.tif',
                 'S1B_IW_GRDH_1SDV_20200620T101816_20200620T101851_022116_029F8B_298B.zip.tif']
    post_image = ['S1B_IW_GRDH_1SDV_20200714T101817_20200714T101852_022466_02AA36_A270.zip.tif',
                  'S1B_IW_GRDH_1SDV_20200726T101818_20200726T101853_022641_02AF8A_BF3A.zip.tif']
    ndfi = ndfi(pre_image, post_image)
    array2Raster(ndfi, '/home/Tuotianyu/数据/paper_based/ndfi_0608_0620_0714_0726_VV.tif',
                 refImg='S1B_IW_GRDH_1SDV_20200608T101815_20200608T101851_021941_029A3A_7867.zip.tif')
    # 以0.7位阈值将NDFI转换为二值图像
    binary_im = raster2binary('/home/Tuotianyu/数据/paper_based/ndfi_0608_0620_0714_0726_VV.tif', 0.7)
    array2Raster(binary_im, '/home/Tuotianyu/数据/paper_based/binary_ndfi_0608_0620_0714_0726_VV.tif',
                 refImg='/home/Tuotianyu/数据/paper_based/ndfi_0608_0620_0714_0726_VV.tif')

    ndfi_post_process2('/home/Tuotianyu/数据/paper_based/binary_ndfi_0608_0620_0714_0726_VV.tif',
                       '/home/Tuotianyu/数据/paper_based/2_post_process_ndfi_0608_0620_0714_0726_VV.tif')
    erase_small_area('/home/Tuotianyu/数据/paper_based/2_post_process_ndfi_0608_0620_0714_0726_VV.tif', 10,
                     '/home/Tuotianyu/数据/paper_based/3_post_process_ndfi_0608_0620_0714_0726_VV.tif')


