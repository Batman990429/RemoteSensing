import cv2
import os
from osgeo import gdal
import sys
from assistance.array_to_raster import array2Raster


def erase_small_area(img: str, threshold: int, output: str)-> None:
    """
    消除NDFI提取洪涝区域中像素个数较小的像素族
    :param img: 洪涝提取结果
    :param threshold: 个数小于阈值的像素族将会被清楚
    :param output: 输出路径
    :return:
    """

    data_set = gdal.Open(img)
    im = data_set.GetRasterBand(1).ReadAsArray()
    print('height:', len(im), 'width:', len(im[0]))
    ret, thresh = cv2.threshold(
        im, 0, 255, cv2.THRESH_BINARY)

    cv2.namedWindow('im', cv2.WINDOW_NORMAL)
    cv2.imshow('im', thresh)
    cv2.waitKey(0)

    # 寻找二值图像中的轮廓
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    n = len(contours)
    print("'Contours' number:", n)

    for i in range(0, n):
        if cv2.contourArea(contours[i]) < threshold:
            # 初始化，记录消除区域的范围
            r_min, r_max, c_min, c_max = sys.maxsize, -1, sys.maxsize, -1
            for j in range(0, len(contours[i])):
                if contours[i][j][0][1] < r_min:
                    r_min = contours[i][j][0][1]
                if contours[i][j][0][1] > r_max:
                    r_max = contours[i][j][0][1]
                if contours[i][j][0][0] < c_min:
                    c_min = contours[i][j][0][0]
                if contours[i][j][0][0] > c_max:
                    c_max = contours[i][j][0][0]
            for j in range(r_min, r_max + 1):
                for k in range(c_min, c_max + 1):
                    im[j][k] = 0

    array2Raster(im, output, refImg=img)
    # 绘制轮廓
    cv2.drawContours(im, contours, -1, (255, 255, 255), 2)

    cv2.namedWindow('contours', cv2.WINDOW_NORMAL)
    cv2.imshow('contours', im)
    cv2.waitKey(0)


if __name__ == '__main__':
    os.chdir(r'F:\毕设\数据\最终结果2')
    erase_small_area('1_post_process_ndfi_2.tif', 10, '3_10_post_process_ndfi_2.tif')
