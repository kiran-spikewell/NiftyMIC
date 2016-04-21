#!/usr/bin/python

## \file ITK_Registration.py
#  \brief Figure out how to register two images within WrapITK
#
#  \author: Michael Ebner (michael.ebner.14@ucl.ac.uk)
#  \date: 

## import librarties
import itk
import SimpleITK as sitk
import numpy as np

import sys
sys.path.append("../src")

import SimpleITKHelper as sitkh
import Stack as st
import Slice as sl
import PSF as psf

pixel_type = itk.D
image_type = itk.Image[pixel_type, 3]

"""
Functions
"""
def read_itk_image(filename):
    # image_IO_type = itk.NiftiImageIO

    reader = itk.ImageFileReader[image_type].New()
    reader.SetFileName(filename)
    reader.Update()
    image_itk = reader.GetOutput()
    image_itk.DisconnectPipeline()

    return image_itk

def get_rigid_registration_transform_3D(fixed, moving):
    ## Look at http://www.itk.org/Doxygen/html/Examples_2RegistrationITKv3_2ImageRegistration8_8cxx-example.html#_a10

    registration = itk.ImageRegistrationMethod[image_type, image_type].New()

    ## Create Spatial Objects for masks so that they can be used within metric
    mask_object_type = itk.ImageMaskSpatialObject[3]
    fixed_mask_object = mask_object_type.New()
    moving_mask_object = mask_object_type.New()
    fixed_mask_object.SetImage(fixed.itk_mask)
    moving_mask_object.SetImage(moving.itk_mask)

    ## Initial transform: Variant A
    # transform_type = itk.VersorRigid3DTransform.D
    # initial_transform = transform_type.New()

    # initializer = itk.CenteredTransformInitializer[transform_type, image_type, image_type].New()
    # initializer.SetTransform(initial_transform)
    # initializer.SetFixedImage(fixed.itk)
    # initializer.SetMovingImage(moving.itk)
    # initializer.MomentsOn()
    # initializer.InitializeTransform()

    ## Initial transform: Variant B
    initial_transform = itk.Euler3DTransform.New()

    interpolator = itk.LinearInterpolateImageFunction[image_type, pixel_type].New()
    # interpolator = itk.OrientedGaussianInterpolateImageFunction[image_type, pixel_type].New()
    # Cov = np.eye(3)*1.1;
    # interpolator.SetCovariance(Cov.flatten())

    
    # metric = itk.MeanSquaresImageToImageMetric[image_type, image_type].New()
    # metric = itk.NormalizedMutualInformationHistogramImageToImageMetric[image_type, image_type].New()
    # metric = itk.MutualInformationImageToImageMetric[image_type, image_type].New()
    # metric = itk.NormalizedCorrelationImageToImageMetric[image_type, image_type].New()
    metric = itk.MattesMutualInformationImageToImageMetric[image_type, image_type].New()
    # metric.SetNumberOfHistogramBins(200)
    # metric.SetFixedImageMask(fixed_mask_object)
    # metric.SetMovingImageMask(moving_mask_object)

    # optimizer = itk.RegularStepGradientDescentOptimizer.New()
    optimizer = itk.ConjugateGradientOptimizer.New()
    # optimizer.SetMaximumStepLength(1.00)
    # optimizer.SetMinimumStepLength(0.01)
    # optimizer.SetNumberOfIterations(200)

    registration.SetInitialTransformParameters(initial_transform.GetParameters())
    registration.SetFixedImageRegion(fixed.itk.GetBufferedRegion())
    registration.SetOptimizer(optimizer)
    registration.SetTransform(initial_transform)
    # registration.SetTransform(transform_type.New())
    registration.SetInterpolator(interpolator)
    
    registration.SetMetric(metric)

    registration.SetMovingImage(moving.itk)
    registration.SetFixedImage(fixed.itk)

    ## Execute registration
    registration.Update()

    ## Get registration transform
    rigid_registration_3D = registration.GetOutput().Get()

    # final_parameters = registration.GetLastTransformParameters()
    # rigid_registration_3D = itk.Euler3DTransform.New()
    # rigid_registration_3D.SetParameters(final_parameters)

    return rigid_registration_3D


def get_resampled_image(fixed_itk, moving_itk, transformation):
    resampler = itk.ResampleImageFilter[image_type, image_type].New()

    resampler.SetInput(moving_itk)
    resampler.SetTransform(transformation)
    resampler.SetOutputParametersFromImage(fixed_itk)
    # resampler.SetSize(fixed_itk.GetLargestPossibleRegion().GetSize())
    # resampler.SetOutputOrigin(fixed_itk.GetOrigin())
    # resampler.SetOutputSpacing(fixed_itk.GetSpacing())
    # resampler.SetOutputDirection(fixed_itk.GetDirection())
    resampler.SetDefaultPixelValue(0.0)

    warped_itk = resampler.GetOutput()

    return warped_itk


"""
Main
"""
## define input data
dir_input = "data/"
dir_input = "../data/fetal_neck_mass_brain/"
dir_output = "results/"
filename = "fetal_brain_a"
filename = "0"

fixed = st.Stack.from_nifti(dir_input, filename)
# moving = st.Stack.from_nifti(dir_input, filename + "_rotated_angle_z")
moving = st.Stack.from_nifti(dir_input, "2")

# fixed_itk = read_itk_image(dir_input + filename + ".nii.gz")
# moving_itk = read_itk_image(dir_input + "2.nii.gz")
# moving_mask_itk = read_itk_image(dir_input + "2_mask.nii.gz")
# moving_mask_sitk = sitk.ReadImage(dir_input + "2_mask.nii.gz")
# moving_itk = read_itk_image(dir_input + filename + "_rotated_angle_z.nii.gz")

## Register images
rigid_transform_3D = get_rigid_registration_transform_3D(fixed, moving)

## Resample image
warped_itk = get_resampled_image(fixed.itk, moving.itk, rigid_transform_3D)
# warped_itk = get_resampled_image(fixed.itk, moving.itk, itk.Euler3DTransform.New())

# trafo = itk.Euler3DTransform.New()
# writer_transformation = itk.TransformFileWriterTemplate[itk.D].New()

sitkh.show_itk_image(warped_itk)

itk.OptimizerParameterScalesEstimatorTemplate.D


## Write warped image
# writer.SetFileName(dir_output + filename + "_test.nii.gz")
# writer.SetInput(warped_itk)
# writer.Update()

# sitkh.show_itk_image(fixed.itk,overlay=warped_itk)


# print fixed.sitk.GetPixelIDValue()

