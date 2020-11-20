from osgeo import gdal


def readImage(image: str, bandNum: int):
    """
    读取图像的一个波段，同时返回及其行列数和波段数
    :param image:
    :param bandNum:
    :return:
    """
    data_set = gdal.Open(image)

    im_width = data_set.RasterXSize
    im_height = data_set.RasterYSize
    im_bands = data_set.RasterCount
    print('im_width:', im_width, 'im_height:', im_height, 'bands_num:', im_bands)

    im = data_set.GetRasterBand(bandNum).ReadAsArray()

    del data_set

    return im, im_width, im_height, im_bands
