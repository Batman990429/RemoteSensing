import snappy
from typing import Union


def subset(s1_read, subsetx, subsety, subsetw, subseth):
    """
    裁剪
    :param s1_read:
    :param subsetx:
    :param subsety:
    :param subsetw:
    :param subseth:
    :return:
    """

    parameters = snappy.HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('region', '%s, %s, %s, %s' % (subsetx, subsety, subsetw, subseth))
    s1_read = snappy.GPF.createProduct('Subset', parameters, s1_read)
    print('Subset succeed！')

    return s1_read


def apply_orbit_file(s1_read):
    """
    精密轨道校正
    :param s1_read:
    :return:
    """
    parameters = snappy.HashMap()
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', '3')
    parameters.put('continueOnFail', 'false')
    s1_read = snappy.GPF.createProduct('Apply-Orbit-File', parameters, s1_read)
    print('Apply Orbit File succeed!')

    return s1_read


def border_noise_removal(s1_read):
    """
    GRD border noise removal
    :param s1_read:
    :return:
    """
    parameters = snappy.HashMap()
    parameters.put('selectedPolarisations', 'VH,VV')
    s1_read = snappy.GPF.createProduct('Remove-GRD-Border-Noise', parameters, s1_read)
    print('GRD border noise removal succeed!')

    return s1_read


def thermal_noise_removal(s1_read):
    """
    热噪声去除
    :param s1_read:
    :return:
    """
    parameters = snappy.HashMap()
    parameters.put('removeThermalNoise', True)
    s1_read = snappy.GPF.createProduct('ThermalNoiseRemoval', parameters, s1_read)
    print('Thermal Noise Removal succeed!')

    return s1_read


def calibration(s1_read):
    """
    辐射校正
    :param s1_read:
    :return:
    """
    parameters = snappy.HashMap()
    # 以标准后向散射系数sigma0的方式定标
    parameters.put('outputSigmaBand', True)
    parameters.put('sourceBands', 'Intensity_VH,Intensity_VV')
    parameters.put('selectedPolarisations', 'VH,VV')
    # 没有分贝化
    parameters.put('outputImageScaleInDb', False)
    s1_read = snappy.GPF.createProduct('Calibration', parameters, s1_read)
    print('Calibration succeed!')

    return s1_read


def speckle_filter(s1_read):
    """
    斑点噪声去除
    :param s1_read:
    :return:
    """
    parameters = snappy.HashMap()
    # 使用改进型Lee滤波器
    parameters.put('filter', 'Refined Lee')
    parameters.put('filterSizeX', 5)
    parameters.put('filterSizeY', 5)
    s1_read = snappy.GPF.createProduct('Speckle-Filter', parameters, s1_read)
    print('Speckle Filter succeed!')

    return s1_read


def terrain_correction(s1_read):
    """
    地形校正
    :param s1_read:
    :return:
    """
    # 地形校正需要获取投影参数WKT文本表示
    proj = """GEOGCS["WGS84(DD)", 
                  DATUM["WGS84", 
                    SPHEROID["WGS84", 6378137.0, 298.257223563]], 
                  PRIMEM["Greenwich", 0.0], 
                  UNIT["degree", 0.017453292519943295], 
                  AXIS["Geodetic longitude", EAST], 
                  AXIS["Geodetic latitude", NORTH]]"""
    parameters = snappy.HashMap()
    # 使用‘SRTM 3Sec’DEM
    parameters.put('deName', 'SRTM 3Sec')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    # 设置分辨率
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('mapProjection', proj)
    # 对海域无高程部分不使用掩膜
    parameters.put('nodataValueAtSea', False)
    parameters.put('saveSelectedSourceBand', True)
    s1_read = snappy.GPF.createProduct('Terrain-Correction', parameters, s1_read)
    print('Terrain Correction succeed!')

    return s1_read


def linear_to_db(s1_read):
    """
    分贝化
    :param s1_read:
    :return:
    """
    parameters = snappy.HashMap()
    s1_read = snappy.GPF.createProduct('LinearToFromdB', parameters, s1_read)
    print('LinearTo/FromdB succeed!')

    return s1_read


def add_land_cover(s1_read):
    """
    使用AddLandCover GPF module自动下载GlobCover
    :param s1_read:
    :return:
    """
    parameters = snappy.HashMap()
    parameters.put("landCoverNames", "GlobCover")
    mask_with_land_cover = snappy.GPF.createProduct('AddLandCover', parameters, s1_read)

    return mask_with_land_cover


def generate_binary_water(s1_read):
    """
    依靠GlobCover的分类来生成水体
    :param s1_read:
    :return:
    """
    BandDescriptor = snappy.jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    parameters = snappy.HashMap()
    targetBand = BandDescriptor()
    targetBand.name = 'BinaryWater'
    targetBand.type = 'uint8'
    targetBand.expression = '(land_cover_GlobCover == 210) ? 0 : 1'
    targetBands = snappy.jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    targetBands[0] = targetBand
    parameters.put('targetBands', targetBands)
    water_mask = snappy.GPF.createProduct('BandMaths', parameters, s1_read)

    return water_mask


def sentinel_1_prerprocess(input_s1_files: Union[str, list], output_directory: str,
                           sub=True, subsetx=10000, subsety=7000, subsetw=10000, subseth=10000,
                           applyOF=True, bnr=True, removeTN=True, cal=True,speckleFl=True,
                           terrainC=True, L2dB=True, saveFormat='GeoTIFF', waterMask=False)->None:
    """
    使用snappy对Sentient-1GRD数据进行预处理
    :param input_s1_files: 读入文件路径
    :param output_directory: 输出文件目录
    :param sub: 是否进行裁剪，默认为是
    :param subsetx: 裁剪起始的x坐标
    :param subsety: 裁剪起始的y坐标
    :param subsetw: 裁剪的宽度
    :param subseth: 裁剪的高度
    :param applyOF: 是否进行精密轨道校正，默认为是
    :param bnr: 是否进行边缘噪声消除，默认为是
    :param removeTN: 是否去除热噪声，默认为是
    :param cal: 是否进行辐射校正，默认为是
    :param speckleFl: 是否进行斑点噪声去除，默认为是
    :param terrainC: 是否进行地形校正，默认为是
    :param L2dB: 对否分贝化，默认为是
    :param saveFormat: 存储的格式，默认为GeoTiff
    :return:
    """

    for i in input_s1_files:
        # read with snappy
        s1_read = snappy.ProductIO.readProduct(i)

        # 裁剪
        if sub:
            s1_read = subset(s1_read, subsetx, subsety, subsetw, subseth)

        # 轨道校正操作
        if applyOF:
            s1_read = apply_orbit_file(s1_read)

        # GRD border noise removal
        if bnr:
            s1_read = border_noise_removal(s1_read)

        # 热噪声去除
        if removeTN:
            s1_read = thermal_noise_removal(s1_read)

        # 辐射定标操作
        if cal:
            s1_read = calibration(s1_read)

        # 斑点滤波
        if speckleFl:
            s1_read = speckle_filter(s1_read)

        # 地形校正操作
        if terrainC:
            s1_read = terrain_correction(s1_read)

        # 分贝化
        if L2dB:
            s1_read = linear_to_db(s1_read)

        if waterMask:
            s1_read = add_land_cover(s1_read)
            s1_read = generate_binary_water(s1_read)

        # 保存为GeoTIFF格式
        saveF = saveFormat
        output_name = output_directory + i
        # 不支持数据更新
        incremental = False
        snappy.GPF.writeProduct(s1_read, snappy.File(output_name), saveF, incremental, snappy.ProgressMonitor.NULL)
        print('Get ARD!')


if __name__ == '__main__':
    import os
    from glob import iglob

    # 获取未预处理数据路径
    product_path = r'/home/Tuotianyu/未预处理S1数据'
    input_s1_files = sorted(list(iglob(os.path.join(product_path, '**', '*S1*.zip'), recursive=True)))

    # 只进行地形校正和辐射校正
    sentinel_1_prerprocess(input_s1_files, '/home/Tuotianyu/S1_ARD/add_water_mask',
                           applyOF=False, bnr=False, removeTN=False, speckleFl=False, L2dB=False, waterMask=True)


