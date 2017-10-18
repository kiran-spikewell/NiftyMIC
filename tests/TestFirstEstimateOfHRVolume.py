## \file TestFirstEstimateOfHRVolume.py
#  \brief  Class containing unit tests for module FirstEstimateOfHRVolume
# 
#  \author Michael Ebner (michael.ebner.14@ucl.ac.uk)
#  \date December 2015


# Import libraries 
import SimpleITK as sitk
import numpy as np
import unittest
import sys

import pysitk.simple_itk_helper as sitkh

import niftymic.utilities.FirstEstimateOfHRVolume as efhrv
import niftymic.utilities.StackManager as sm
import niftymic.base.Slice as sl
import niftymic.base.Stack as st


## Concept of unit testing for python used in here is based on
#  http://pythontesting.net/framework/unittest/unittest-introduction/
#  Retrieved: Aug 6, 2015
class TestFirstEstimateOfHRVolume(unittest.TestCase):

    ## Specify input data
    dir_test_data = "../../../test-data/"

    accuracy = 7

    def setUp(self):
        pass

    ## Test whether private function _get_zero_framed_stack within FirstEstimateOfHRVolume
    #  works correctly
    def test_01_get_zero_framed_stack(self):

        ## Read stack
        stack = st.Stack.from_filename(
            os.path.join(self.dir_test_data, "fetal_brain_0.nii.gz"),
            os.path.join(self.dir_test_data, "fetal_brain_0_mask.nii.gz")
            )

        ## Isotropically resample stack (simulate HR volume for FirstEstimateOfHRVolume)
        #  Idea: Don't "merge" more stacks but only use one isotropic stack where ground
        #       truth is available then
        stack_resampled = stack.get_isotropically_resampled_stack(interpolator="Linear")
        # stack_resampled.show()

        ## Create FirstEstimateOfHRVolume in order to access _get_zero_framed_stack function
        stack_manager = sm.StackManager.from_stacks([stack])
        first_estimate_of_HR_volume = efhrv.FirstEstimateOfHRVolume(stack_manager, "bla", 0)
        stack_resampled_framed = first_estimate_of_HR_volume._get_zero_framed_stack(stack_resampled, 5)
        # stack_resampled_framed.show()

        ## Resample back to stack_resampled
        stack_resampled_frame_resampled_sitk = sitk.Resample(stack_resampled_framed.sitk, stack_resampled.sitk, sitk.Euler3DTransform(), sitk.sitkLinear, 0.0, stack_resampled_framed.sitk.GetPixelIDValue())

        ## Check alignment
        nda_diff = sitk.GetArrayFromImage(stack_resampled_frame_resampled_sitk - stack_resampled.sitk)
        self.assertEqual(np.round(
                np.linalg.norm(nda_diff)
                , decimals = self.accuracy), 0)

