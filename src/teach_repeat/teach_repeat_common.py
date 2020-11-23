
# IMPORT MODULES
import os
import sys
# import cv2 as cv
import numpy as np
from . import transform_tools

# In order to import OpenCV when using Python 3, need to remove ROS python2.7 dist packages.
if sys.version_info[0] == 3 and '/opt/ros/kinetic/lib/python2.7/dist-packages' in sys.path:
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages') # so can import opencv for python3, silly ROS
import cv2 as cv

# Reads in a dataset file
def ReadDatasetFile(dataset_file_path):
    dataset = np.genfromtxt(dataset_file_path, delimiter=', ', skip_header=1)
    if len(dataset.shape) == 1: # will occur if there is a single teach in the dataset
        dataset = np.reshape(dataset, (1,dataset.shape[0]))
    dataset[:,0] = np.arange(0, dataset.shape[0]) # add in frame IDs to column 1, else will be NAN

    return dataset


# Calculate Transform Between Two Pose Messages
def CalculateTransformBetweenPoseMessages(pose_at_current_frame, pose_at_previous_frame):
    # Check if either argument is none
    if pose_at_current_frame == None or pose_at_previous_frame == None:
        # can't calculate
        return np.array([])
    
    # Turn the pose at current frame and previous frame into transformation matrices
    current_frame_trans = transform_tools.pose_msg_to_trans(pose_at_current_frame)
    previous_frame_trans = transform_tools.pose_msg_to_trans(pose_at_previous_frame)

    # Deterimine relative transform
    relative_trans = transform_tools.diff_trans(previous_frame_trans, current_frame_trans)

    return relative_trans

# Write Data to a Dataset File
def WriteDataToDatasetFile(img, frame_id, save_path, relative_odom_trans, relative_pose_trans, dataset_file, parameters = {'SAVE_IMAGE_RESIZE': (640,480)}):
    # Resize image
    img_save = cv.resize(img, parameters['SAVE_IMAGE_RESIZE'])

    # Save Image and Relative Odometry
    frame_name = "frame_%06d.png" % frame_id
    try:
        cv.imwrite(os.path.join(save_path, frame_name), img_save)
    except Exception as e:
        return -1

    # Write to dataset file
    if relative_odom_trans.size != 0:
        odom_yaw = transform_tools.yaw_from_trans(relative_odom_trans)
        pose_yaw = transform_tools.yaw_from_trans(relative_pose_trans)
        dataset_file.write('%s, %0.4f, %0.4f, %0.4f, %0.4f, %0.4f, %0.4f\n'%(frame_name, relative_odom_trans[0,-1], relative_odom_trans[1,-1], odom_yaw, relative_pose_trans[0,-1], relative_pose_trans[1,-1], pose_yaw))
    else:
        dataset_file.write('%s, Nan, Nan, Nan, Nan, Nan, Nan\n'%(frame_name))

    return 0

# Crop an image from its center based on a portion
def ImageCropCenter(img, x_portion, y_portion = None):
    if y_portion == None:
        y_portion = x_portion

    if len(img.shape) == 2:
        img_height, img_width = img.shape
        channels = 1
    else:
        img_height, img_width, channels = img.shape

    # portion is from from 0 to 1 
    patch_width = int(min(max(round(img_width * x_portion), 1), img_width))
    patch_height = int(min(max(round(img_height * y_portion), 1), img_height))

    startx = int(img_width//2-(patch_width//2))
    starty = int(img_height//2-(patch_height//2))

    if channels == 1:
        return img[starty:starty+patch_height,startx:startx+patch_width]
    else:
        return img[starty:starty+patch_height,startx:startx+patch_width, :]

# Crop an image from its center based on a portion
def ImageCrop(img, xStart, x_portion, y_portion = None):
    if y_portion == None:
        y_portion = x_portion

    if len(img.shape) == 2:
        img_height, img_width = img.shape
        channels = 1
    else:
        img_height, img_width, channels = img.shape

    # portion is from from 0 to 1 
    patch_width = int(min(max(round(img_width * x_portion), 1), img_width))
    patch_height = int(min(max(round(img_height * y_portion), 1), img_height))

    startx = int(xStart-(patch_width//2))
    starty = int(img_height//2-(patch_height//2))

    if channels == 1:
        return img[starty:starty+patch_height,startx:startx+patch_width]
    else:
        return img[starty:starty+patch_height,startx:startx+patch_width, :]
        
# Draws a rectangle on image
def DrawCropPatchOnImage(img, x_portion, y_portion = None, center=np.array([])):
    if y_portion == None:
        y_portion = x_portion

    if len(img.shape) == 2:
        img_height, img_width = img.shape
    else:
        img_height, img_width, channels = img.shape


    # portion is from from 0 to 1 
    patch_width = int(min(max(round(img.shape[1] * x_portion), 1), img_width))
    patch_height = int(min(max(round(img.shape[0] * y_portion), 1), img_height))

    if center.size == 0:
        startx = int(img_width//2-(patch_width//2))
        starty = int(img_height//2-(patch_height//2))

        # draw rectangle
        cv.rectangle(img,(startx,starty),(startx+patch_width, starty+patch_height), (0,0,255), 3)
    
    else:
        print(center)
        print(patch_width, patch_height)
        startx = int(center[0] - (patch_width//2))
        starty = int(center[1] - (patch_height//2))

        cv.rectangle(img,(startx,starty),(startx+patch_width, starty+patch_height), (0,0,255), 3)
