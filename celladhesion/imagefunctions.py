import skimage.io
import skimage.segmentation
import os
import numpy as np
import cv2
import glob
from natsort import os_sorted


"""def read_tifs(folder):
    
    Reads '.tif'-files from the given folder
    :param folder: folder directory (...:/.../.../)
    :return: list containing ndarray of each '.tif'-file in the folder
    
    files = [os.path.join(root, filename)   # creates list of every filename
             for root, dirs, files in os.walk(folder)
             for filename in files
             if filename.lower().endswith('.tif')]

    imgs = [skimage.io.imread(f) for f in files]

    return imgs"""


def read_tifs(folder):
    """
    Reads '.tif'-files from the given folder
    :param folder: folder directory (...:/.../.../)
    :return: list containing ndarray of each '.tif'-file in the folder
    """

    # read the images and make sure the reading order is the same es the one in the windows explorer ('os_sorted()')
    imgs = [skimage.io.imread(file) for file in os_sorted(glob.glob(os.path.join(folder, "*.tif")))]

    return imgs


def read_pngs(folder):
    """
     Reads '.png'-files from the given folder
    :param folder: folder directory (...:/.../.../)
    :return: list containing ndarray of each '.png'-file in the folder
    """
    # read the images and make sure the reading order is the same es the one in the windows explorer ('os_sorted()')
    imgs = [skimage.io.imread(file) for file in os_sorted(glob.glob(os.path.join(folder, "*.png")), key=os.path.getmtime)]

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


def read_single_img(path):
    # Read a single image from given path
    img = skimage.io.imread(path)
    return img


def load_masks(path):
    # load '.npy' masks from given path
    masks = np.load(path, allow_pickle=True)
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
    :param colour: array
                Float array with values from 0.0 to 1.0 for the three RGB channels
    :return overlay: list of RGB images
                RGB images with coloured outlines
    """
    if isinstance(imgs, list):
        overlay = list()

        for img_number in range(len(imgs)):     # iterate all images in 'imgs'
            # Create outlines of the masks with 'find_boundaries' function from 'skimage' package:
            outlines = skimage.segmentation.find_boundaries(masks[img_number], mode='outer').astype(np.uint8)
            # Check if image is already RGB
            if len(imgs[img_number].shape) != 3:
                # convert image to RGB, divide by maximum value to show image in full range:
                # img_rgb = np.stack((imgs[img_number] / imgs[img_number].max(),)*3, axis=-1)
                img_rgb = np.stack((imgs[img_number],)*3, axis=-1)
            else:
                # img_rgb = imgs[img_number] / imgs[img_number].max()
                img_rgb = imgs[img_number]
            # iterate over every pixel and set colour of image to red, if pixel is part of an outline:
            for y in range(masks[img_number].shape[0]):
                for x in range(masks[img_number].shape[1]):
                    if outlines[y][x] == 1:
                        img_rgb[y][x] = [imgs[img_number].max(), 0, 0]
                        if x > masks[img_number].shape[1] / 2:
                            img_rgb[y][x-1] = [imgs[img_number].max(), 0, 0]
                        else:
                            img_rgb[y][x+1] = [imgs[img_number].max(), 0, 0]
                        if y > masks[img_number].shape[0] / 2:
                            img_rgb[y-1][x] = [imgs[img_number].max(), 0, 0]
                        else:
                            img_rgb[y+1][x] = [imgs[img_number].max(), 0, 0]


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


def overlay_adherent_squares(imgs, adherent_cells, square_length, colour=[0, 0.54, 0.27]):
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
        try:
            pos = cell.get_position()
            pos_top = [pos[0] - length, pos[1] - length]
            pos_bottom = [pos[0] + length, pos[1] + length]
            first_appearance = cell.get_first_appearance()
            for consecutive_img_number in range(cell.get_number_appearances()):
                # imgs_rgb[first_appearance + consecutive_img_number] = cv2.rectangle(imgs_rgb[first_appearance + consecutive_img_number], pos_top, pos_bottom, color)
                imgs_rgb[first_appearance + consecutive_img_number] = cv2.circle(imgs_rgb[first_appearance + consecutive_img_number], pos, 40, colour, 2)
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
        except:
            print("No adherent cells")

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

    # create list where the mask numbers belonging to adherent cells for each image will be saved
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


def adherent_cells_over_phasecontrast(phc_img, masks, adherent_cells, colour):
    """
    Overlays outlines only of the adherent cells on one single image

    :param phc_img: ndarray
                Image on which the outlines of the adherent cells will be plotted
    :param masks: list of 2D arrays
                labelled image, where 0=no masks; 1,2,...=mask labels
    :param adherent_cells: list
                list of 'AdherentCell' objects
    :param colour: array
                Float array with values from 0.0 to 1.0 for the three RGB channels
    :return: adh_over_phc: list of RGB images
                RGB images with red outline where adherent cells are located
    """
    phc_img = phc_img / phc_img.max()
    adherent_masks = filter_masks(masks, adherent_cells)
    imgs = list()
    for i in range(len(masks)):
        imgs.append(phc_img)
    adh_over_phc = overlay_outlines(imgs, adherent_masks)

    return adh_over_phc


def background_mask_over_img(imgs, background_masks):
    """
    Overlays outlines of the background mask over the images

    :param imgs: list
                list of 2D images
    :param background_masks: 2D array or list of 2d arrays
                labelled image, where 0=no masks; 1,2,...=mask labels
    :param colour: array
                Float array with values from 0.0 to 1.0 for the three RGB channels
    :return: background_over_img: list of RGB images
                RGB images with coloured outlines
    """
    masks = list()
    # if background mask is a list with more than one image
    if (isinstance(background_masks, list)) and (len(background_masks) > 1):
        masks = background_masks
    # if background mask is a list with just one image
    elif isinstance(background_masks, list):
        for i in range(len(imgs)):
            masks.append(background_masks[0])
    # if background mask is a single image
    else:
        for i in range(len(imgs)):
            masks.append(background_masks)

    background_over_img = overlay_outlines(imgs, masks)

    return background_over_img


def find_intensity_complete(img):
    """
    Determines the intensity of all pixel values of an given image

    :param img: ndarray
            image of which the intensity shall be determined
    :return: intensity: float
            intensity of the picture
    """
    pixels = 0  # total number of pixels
    intensity_counter = np.float64(0)   # total intensity of all pixels

    for y in range(img.shape[0]):   # iterate image
        for x in range(img.shape[1]):
            intensity_counter += img[y][x]  # raise value of the intensity by the value of the pixel
            pixels += 1     # raise pixel counter

    intensity = round(intensity_counter / pixels, 2)   # calculate intensity, normalized with the total number of pixels
    return intensity


def find_intensity_mask(img, background_mask):
    """
    Determines the intensities of those pixels on an image, that match with the pixels of an background mask
    :param img: ndarray
            image of which the intensity shall be determined
    :param background_mask: 2D array
            labelled image, where 0=no masks; 1,2,...=mask labels
    :return: intensities: dictionary
            dictionary that contains the intensity (float) of all pixels matching a mask, the intensity of all the other pixels
            and the confluence (percentage of the image surface covered by masks). Key words: "mask", "rest",
            "confluence"
    """

    pixels_mask = 0     # variable to count the number of mask pixels
    pixels_rest = 0     # variable to count all other pixels
    intensity_mask_counter = np.float64(0)  # total intensity of mask pixels
    intensity_rest_counter = np.float64(0)  # total intensity of other pixels

    for y in range(img.shape[0]):   # iterate image
        for x in range(img.shape[1]):
            if background_mask[y][x] != 0:  # mask pixel, if value is not zero
                intensity_mask_counter += img[y][x]     # -> raise total mask intensity
                pixels_mask += 1    # -> raise mask pixel counter
            else:   # else: no mask pixel
                intensity_rest_counter += img[y][x]     # -> raise rest mask intensity
                pixels_rest += 1    # -> raise rest pixel counter

    # calculate intensity (normalized with the total number of pixels) of the mask and rest pixels
    intensity_mask = round(intensity_mask_counter / pixels_mask, 2)
    intensity_rest = round(intensity_rest_counter / pixels_rest, 2)
    # calculate confluence of the background mask
    confluence = round((pixels_mask / (pixels_mask + pixels_rest)) * 100)

    # save values in a dictionary
    intensities = {"mask": intensity_mask, "rest": intensity_rest, "confluence": confluence}

    return intensities


def find_intensity(imgs, background_mask=None):
    """
    Determines the intensities of one or more images. If an image with a background mask is handed over, the intensities
    of those pixels on the images, that match with the pixels of the background mask, are calculated separately.
    The function uses 'find_intensity_complete' and 'find_intensity_mask' functions to do so.

    :param imgs: list or ndarray
            list containing 'ndarray' of each image ore one single ndarray
    :param background_mask: 2D array or list of 2d arrays
            labelled image, where 0=no masks; 1,2,...=mask labels
    :return: intensity: float or dictionary
            intensity value (for single image input) or list of intensity values (for multiple image input)
            If a background mask is used, the intensity is a dictionary that contains the intensity (float) of all
            pixels matching a mask, the intensity of all the other pixels and the confluence (percentage of the image
            surface covered by masks). Key words: "mask", "rest", "confluence".
            Otherwise, the intensity is a single float value.
    """
    # version without background mask
    if background_mask is None:
        # multiple images
        if isinstance(imgs, list):
            intensities = list()    # list needed for multiple images
            for img_nr in range(len(imgs)):     # find intensity for every image
                intensities.append(find_intensity_complete(imgs[img_nr]))
            return intensities
        # single image
        else:
            intensity = find_intensity_complete(imgs)   # find intensity for single image
            return intensity
    # version with background mask
    else:
        # multiple images
        if isinstance(imgs, list):
            intensities = list()    # list needed for multiple images
            for img_nr in range(len(imgs)):
                # if function gets a list of background_masks (one for every image): use the specific background_mask[img_nr]
                if (isinstance(background_mask, list)) and (len(background_mask) > 1):
                    intensities.append(find_intensity_mask(imgs[img_nr], background_mask[img_nr]))
                # otherwise use the same background mask for every image
                else:
                    intensities.append(find_intensity_mask(imgs[img_nr], background_mask[0]))
            return intensities
        # single image
        else:
            intensity = find_intensity_mask(imgs, background_mask)
            return intensity



        










