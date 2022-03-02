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
    files = [os.path.join(root, filename)   # creates list of every filename
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

def read_single_tif(path):
    # Read a single '.tif' image from given path
    img = skimage.io.imread(path)
    return img

def load_masks(path):
    # load '.npy' masks from given path
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
    if isinstance(imgs, list):
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

    else:
        outlines = skimage.segmentation.find_boundaries(masks, mode='outer').astype(np.uint8)
        # Check if image is already RGB
        if len(imgs.shape) != 3:
            # convert image to RGB, divide by maximum value to show image in full range:
            img_rgb = np.stack((imgs / imgs.max(),) * 3, axis=-1)
        else:
            img_rgb = imgs / imgs.max()
        # iterate over every pixel and set colour of image to red, if pixel is part of an outline:
        for y in range(masks.shape[0]):
            for x in range(masks.shape[1]):
                if outlines[y][x] == 1:
                    img_rgb[y][x] = [1.0, 0, 0]
        overlay = img_rgb  # add new image with outlines to list
    return overlay


def overlay_adherent_squares(imgs, adherent_cells, square_length):
    length = int(square_length / 2)
    imgs_rgb = list()
    for img_number in range(len(imgs)):
        # Check if image is already RGB
        if len(imgs[img_number].shape) != 3:
            # convert image to RGB, divide by maximum value to show image in full range:
            # imgs_rgb.append(np.stack((imgs[img_number] / imgs[img_number].max(),) * 3, axis=-1))
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
            # imgs_rgb[first_appearance + consecutive_img_number] = cv2.rectangle(imgs_rgb[first_appearance + consecutive_img_number], pos_top, pos_bottom, color)
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


def filter_masks(masks, adherent_cells):
    """
    Filters the given masks for the adherent cells -> deletes all masks that do not belong to an adherent cell

    :param masks: list of 2D arrays
                labelled image, where 0=no masks; 1,2,...=mask labels
    :param adherent_cells: list
                list of 'AdherentCell' objects
    :return: filtered_masks: list of 2D arrays
                same as masks, but only contains the masks that belong to adherent cells
    """

    """for img_nr in range(len(masks)):
        if adherent_cells[img_nr]:
            pos = adherent_cells[img_nr][0].get_position()
            mask_number = masks[img_nr][pos[0]][pos[1]]
            adherent_mask_numbers[0] = mask_number
            for cell_nr in range(1, len(adherent_cells[img_nr])):
                pos = adherent_cells[img_nr][cell_nr].get_position()
                mask_number = masks[img_nr][pos[0]][pos[1]]
                adherent_mask_numbers.append(mask_number)
        for y in range(masks[img_nr].shape[0]):
            for x in range(masks[img_nr].shape[1]):
                if masks[img_nr][y][x] not in adherent_mask_numbers:
                    masks[img_nr][y][x] = 0
    filtered_masks = masks"""

    """zero_list = [0]
    adherent_mask_numbers = list()
    for i in range(len(masks)):
        adherent_mask_numbers.append(zero_list)
    print(adherent_mask_numbers)

    for cell_number in range(len(adherent_cells)):
        cell = adherent_cells[cell_number]
        first_app = adherent_cells[cell_number].get_first_appearance()
        pos = adherent_cells[cell_number].get_position()
        for consecutive_img_number in range(cell.get_number_appearances()):
            mask_nr = masks[first_app + consecutive_img_number][pos[1]][pos[0]]
            adherent_mask_numbers[first_app + consecutive_img_number].append(mask_nr)"""

    # create list where the mask numbers belonging to adherent cells for each image will be safed
    adherent_mask_numbers = list()

    # create copy of masks that will be edited
    filtered_masks = masks

    for img_nr in range(len(masks)):    # iterate all images/masks of all images
        temp_list = [0]                 # temporary list to safe adherent mask numbers for one image
        for cell_nr in range(len(adherent_cells)):  # iterate all adherent cells
            cell = adherent_cells[cell_nr]
            first_app = cell.get_first_appearance()
            # iterate all appearances of an adherent cell
            for consecutive_img_number in range(cell.get_number_appearances()):
                # check, if the image number of the current appearance equals the image number (outer iteration)
                if img_nr == first_app + consecutive_img_number:
                    # if yes, get position of the adherent cell
                    pos = cell.get_position()
                    # get number (pixel value) of the related mask
                    mask_nr = masks[first_app + consecutive_img_number][pos[1]][pos[0]]
                    # add number to the temporary list
                    temp_list.append(mask_nr)
        # add temporary list to adherent_mask_numbers list
        adherent_mask_numbers.append(temp_list)

    # iterate all images
    for img_nr in range(len(filtered_masks)):
        # iterate all pixels on image
        for y in range(filtered_masks[img_nr].shape[0]):
            for x in range(filtered_masks[img_nr].shape[1]):
                # if value at pixel (mask) does not belong to an adherent mask, delete the mask pixel (set value to 0)
                if filtered_masks[img_nr][y][x] not in adherent_mask_numbers[img_nr]:
                    filtered_masks[img_nr][y][x] = 0

    return filtered_masks


def adherent_cells_over_phasecontrast(phc_img, masks, adherent_cells):
    """
    Overlays outlines only of the adherent cells on one single image

    :param phc_img: ndarray
                Image on which the outlines of the adherent cells will be plotted
    :param masks: list of 2D arrays
                labelled image, where 0=no masks; 1,2,...=mask labels
    :param adherent_cells: list
                list of 'AdherentCell' objects
    :return: adh_over_phc: list of RGB images
                RGB images with red outline where adherent cells are located
    """

    adherent_masks = filter_masks(masks, adherent_cells)
    imgs = list()
    for i in range(len(masks)):
        imgs.append(phc_img)
    adh_over_phc = overlay_outlines(imgs, adherent_masks)

    return adh_over_phc

        










