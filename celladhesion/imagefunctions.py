import skimage.io
import skimage.segmentation
import os
import numpy as np
import cv2



def read_tifs(folder):
    """
    Reads '.tif'-files from the given folder
    :param folder: folder directory (...:/.../.../)
    :return: list containing ndarray of each '.tif'-file in the folder
    """
    files = [os.path.join(root, filename)   #creates list of every filename
             for root, dirs, files in os.walk(folder)
             for filename in files
             if filename.lower().endswith('.tif')]

    imgs = [skimage.io.imread(f) for f in files]

    return imgs


def read_test_tifs():
    """
    Reads '.tif'-test-files from the test-folder
    :return: list containing ndarray of each .'tif'-test-file in the folder
    """
    folder = 'C:/Users/woerl/Documents/Physik/WS 21-22/Bachelorarbeit/Python/celladheison/celladhesion/testimages'
    files = [os.path.join(root, filename)
             for root, dirs, files in os.walk(folder)
             for filename in files
             if filename.lower().endswith('.tif')]

    imgs = [skimage.io.imread(f) for f in files]

    return imgs

def load_masks(path):
    #load '.npy' masks from given path
    masks = np.load(path)
    return masks

def load_test_masks():
    testmasks = np.load('testmasks.npy')
    return testmasks

def load_diams(path):
    # load diameters from '.txt' file at given path
    with open(path, 'r') as filehandle:
        diams = [current_diam.rstrip() for current_diam in filehandle.readlines()]
    return list(np.float_(diams))

def load_test_diams():
    # open file and read the content in a list
    with open('testdiams.txt', 'r') as filehandle:
        diams = [current_diam.rstrip() for current_diam in filehandle.readlines()]
    return list(np.float_(diams))


def overlay_outlines(imgs, masks):
    """
    Generates red outline overlay in 'imgs'

    :param imgs: list
                containing 'ndarray' of each image
    :param masks: list of 2D arrays; labelled
                image, where 0=no masks; 1,2,...=mask labels
    :return overlay: list of RGB images
                RGB images with red outlines
    """

    overlay = list()

    for img_number in range(len(imgs)):     # iterate all images in 'imgs'
        # Create outlines of the masks with 'find_boundaries' function from 'skimage' package:
        outlines = skimage.segmentation.find_boundaries(masks[img_number], mode='outer').astype(np.uint8)
        # Check if image is already RGB
        if len(imgs[img_number].shape) != 3:
            # convert image to RGB, divide by maximum value to show image in full range:
            img_rgb = np.stack((imgs[img_number] / imgs[img_number].max(),)*3, axis=-1)
        else:
            img_rgb = imgs[img_number] / imgs[img_number].max()
        # iterate over every pixel and set colour of image to red, if pixel is part of an outline:
        for y in range(masks[img_number].shape[0]):
            for x in range(masks[img_number].shape[1]):
                if outlines[y][x] == 1:
                    img_rgb[y][x] = [1.0, 0, 0]
        overlay.append(img_rgb)     # add new image with outlines to list
    return overlay


def overlay_adherent_squares(imgs, adherent_cells, square_length):
    length = int(square_length / 2)
    imgs_rgb = list()
    for img_number in range(len(imgs)):
        # Check if image is already RGB
        if len(imgs[img_number].shape) != 3:
            # convert image to RGB, divide by maximum value to show image in full range:
            #imgs_rgb.append(np.stack((imgs[img_number] / imgs[img_number].max(),) * 3, axis=-1))
            imgs_rgb.append(np.stack((imgs[img_number],) * 3, axis=-1))
        else:
            imgs_rgb.append(imgs[img_number] / imgs[img_number].max())

    for cell_number in range(len(adherent_cells)):
        cell = adherent_cells[cell_number]
        pos = cell.get_position()
        pos_top = [pos[0] - length, pos[1] - length]
        pos_bottom = [pos[0] + length, pos[1] + length]
        first_appearance = cell.get_first_appearance()
        color = [0, 0.54, 0.27]
        for consecutive_img_number in range(cell.get_number_appearances()):
            #imgs_rgb[first_appearance + consecutive_img_number] = cv2.rectangle(imgs_rgb[first_appearance + consecutive_img_number], pos_top, pos_bottom, color)
            imgs_rgb[first_appearance + consecutive_img_number] = cv2.circle(imgs_rgb[first_appearance + consecutive_img_number], pos, 40, color)
            """
            for x_top in range(-length, length):
                imgs_rgb[first_appearance + concsecutive_img_number][pos[1] + length][pos[0] + x_top] = [0, 0.54, 0.27]
            for x_bottom in range(-length, length):
                imgs_rgb[first_appearance + concsecutive_img_number][pos[1] - length][pos[0] + x_bottom] = [0, 0.54, 0.27]
            for y in range(-length, length):
                imgs_rgb[first_appearance + concsecutive_img_number][pos[1] + y][pos[0] + length] = [0, 0.54, 0.27]
                
            for y in range(-length, length):
                imgs_rgb[first_appearance + concsecutive_img_number][pos[1] + y][pos[0] - length] = [0, 0.54, 0.27]
            """


            """
            for y in range(-5, 5):
                for x in range(-5, 5):
                    imgs_rgb[first_appearance + concsecutive_img_number][pos[1] + y][pos[0] + x] = [0, 0.54, 0.27]
                    """

    return imgs_rgb


def time_to_nrimgs(time, delay):
    return 1 + int(round(time/delay, 0))









