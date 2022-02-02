#!/usr/bin/env python
# coding: utf8
#
# Copyright (c) 2021 Centre National d'Etudes Spatiales (CNES).
#
# This file is part of Shareloc
# (see https://github.com/CNES/shareloc).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Test module for image class shareloc/image/image.py
"""

import os
import pytest
import numpy as np
from helpers import data_path
from shareloc.image.image import Image
from shareloc.image.dtm_image import DTMImage

# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    "image_name, row,col, origin_row, origin_col, pixel_size_row, pixel_size_col, "
    "pixel_rotation_row, pixel_rotation_col",
    [
        ("right_image.tif", 100, 200.5, 5162, 4915.0, 1.0, 1.0, 0.0, 0.0),
        ("right_image_resample.tif", 100.0, 200.0, 5162.0, 4915.0, 2.0, 0.5, 0.0, 0.0),
        ("left_image_shear.tif", 100.0, 200.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.36397023426620234),
    ],
)
@pytest.mark.unit_tests
def test_image_metadata(
    image_name, row, col, origin_row, origin_col, pixel_size_row, pixel_size_col, pixel_rotation_row, pixel_rotation_col
):
    """
    Test image class
    """
    data_folder = data_path()
    image_filename = os.path.join(data_folder, "image/phr_ventoux/", image_name)

    my_image = Image(image_filename)
    assert my_image.origin_row == origin_row
    assert my_image.origin_col == origin_col
    assert my_image.pixel_size_row == pixel_size_row
    assert my_image.pixel_size_col == pixel_size_col
    assert my_image.pixel_rotation_row == pixel_rotation_row
    assert my_image.pixel_rotation_col == pixel_rotation_col

    [phys_row, phys_col] = my_image.transform_index_to_physical_point(row, col)
    assert phys_row == origin_row + (row + 0.5) * pixel_size_row + (col + 0.5) * pixel_rotation_row
    assert phys_col == origin_col + (col + 0.5) * pixel_size_col + (row + 0.5) * pixel_rotation_col

    row_index, col_index = my_image.transform_physical_point_to_index(phys_row, phys_col)
    assert row == row_index
    assert col == col_index


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    "image_name, row,col, origin_row, origin_col, pixel_size_row, pixel_size_col, "
    "pixel_rotation_row, pixel_rotation_col",
    [
        ("right_image.tif", 100, 200.5, 5162, 4915.0, 1.0, 1.0, 0.0, 0.0),
        ("right_image_resample.tif", 100.0, 200.0, 5162.0, 4915.0, 2.0, 0.5, 0.0, 0.0),
        ("left_image_shear.tif", 100.0, 200.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.36397023426620234),
    ],
)
@pytest.mark.unit_tests
def test_image_metadata_roi(
    image_name, row, col, origin_row, origin_col, pixel_size_row, pixel_size_col, pixel_rotation_row, pixel_rotation_col
):
    """
    Test image class with roi
    """

    data_folder = data_path()
    image_filename = os.path.join(data_folder, "image/phr_ventoux/", image_name)

    # roi in index
    start_row = 10
    start_col = 20
    end_row = 310
    end_col = 320
    my_image_roi = Image(image_filename, roi=[start_row, start_col, end_row, end_col])
    assert my_image_roi.pixel_size_row == pixel_size_row
    assert my_image_roi.pixel_size_col == pixel_size_col
    assert my_image_roi.pixel_rotation_row == pixel_rotation_row
    assert my_image_roi.pixel_rotation_col == pixel_rotation_col

    phy_valid_row = origin_row + (row + 0.5) * pixel_size_row + (col + 0.5) * pixel_rotation_row
    phy_valid_col = origin_col + (col + 0.5) * pixel_size_col + (row + 0.5) * pixel_rotation_col
    [phys_row, phys_col] = my_image_roi.transform_index_to_physical_point(row - start_row, col - start_col)
    assert phys_row == phy_valid_row
    assert phys_col == phy_valid_col

    row_index, col_index = my_image_roi.transform_physical_point_to_index(phys_row, phys_col)
    assert row == row_index + start_row
    assert col == col_index + start_col

    ## roi in physical space
    start_phys_row = origin_row + start_row * pixel_size_row + start_col * pixel_rotation_row
    start_phys_col = origin_col + start_col * pixel_size_col + start_row * pixel_rotation_col
    end_phys_row = origin_row + end_row * pixel_size_row + end_col * pixel_rotation_row
    end_phys_col = origin_col + end_col * pixel_size_col + end_row * pixel_rotation_col
    roi = [start_phys_row, start_phys_col, end_phys_row, end_phys_col]
    my_image_roi_phys = Image(image_filename, roi=roi, roi_is_in_physical_space=True)
    [phys_row, phys_col] = my_image_roi_phys.transform_index_to_physical_point(row - start_row, col - start_col)
    assert phys_row == phy_valid_row
    assert phys_col == phy_valid_col


def test_dtm_fillnodata():
    """
    Test dtm image fillnodata
    """
    dtm_file = os.path.join(data_path(), "dtm", "srtm_ventoux", "srtm90_non_void_filled", "N44E005.hgt")
    my_image_with_nodata = DTMImage(dtm_file, read_data=True, fill_nodata=None)
    nodata_index = np.argwhere(my_image_with_nodata.mask == 0)[0]
    assert my_image_with_nodata.data[nodata_index[0], nodata_index[1]] == -32768
    my_image_rio_fillnodata = DTMImage(dtm_file, read_data=True, fill_nodata="rio_fillnodata")
    assert my_image_rio_fillnodata.data[nodata_index[0], nodata_index[1]] == 783
    my_image_mean = DTMImage(dtm_file, read_data=True, fill_nodata="mean")
    assert my_image_mean.data[nodata_index[0], nodata_index[1]] == 872
    my_image_min = DTMImage(dtm_file, read_data=True, fill_nodata="min")
    assert my_image_min.data[nodata_index[0], nodata_index[1]] == 32
    my_image_max = DTMImage(dtm_file, read_data=True, fill_nodata="max")
    assert my_image_max.data[nodata_index[0], nodata_index[1]] == 2757
    my_image_median = DTMImage(dtm_file, read_data=True, fill_nodata="median")
    assert my_image_median.data[nodata_index[0], nodata_index[1]] == 840
    my_image_constant = DTMImage(dtm_file, read_data=True, fill_nodata="constant", fill_value=100.0)
    assert my_image_constant.data[nodata_index[0], nodata_index[1]] == 100.0

    dtm_file_srtm_hole = os.path.join(data_path(), "dtm", "srtm_ventoux", "N44E005_big_hole.tif")
    my_image_fill_hole = DTMImage(dtm_file_srtm_hole, read_data=True, fill_nodata="rio_fillnodata")
    assert my_image_fill_hole.data[403, 1119] == 32
