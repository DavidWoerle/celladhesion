import os
import matplotlib.pyplot as plt
import imagefunctions as imf
import skimage.io
from Cell import Cell
from AdherentCell import AdherentCell
import programrun_functions as prf

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"     # Suppress warning when program is run on different computer

""" Run program for already created masks/diams, create new ones or run on test images to find parameters for cell 
detection? """
new_or_use_or_test = input("Create NEW masks, USE already created masks, run on TEST images, find masks/diams for \
MULTIPLE data or determine CONFLUENCE? \n[n / u / t / m / c]: ")

# Create new masks:
if new_or_use_or_test == "n":
    # get images from user
    path_input = input("Path of '.tif'-images: ")
    imgs = imf.read_tifs(path_input)

    # get parameters for cell detection from user
    cellprob_threshold, flow_threshold = prf.get_celldet_params()

    # create new directory for the data with the selected 'cellprob_threshold' and 'flow_threshold'
    path_output_cells_diams = os.path.join(path_input, "celladhesion_" + 'cpt' + str(cellprob_threshold) + 'ft' + str(flow_threshold))
    os.mkdir(path_output_cells_diams)

    # run 'find_cells' method and save masks and diams (names: include 'cellprob_threshold' and 'flow_threshold')
    cells, diams, masks = Cell.find_cells(imgs, cellprob_threshold=cellprob_threshold, flow_threshold=flow_threshold)
    masks_name = 'masks_' + 'cpt' + str(cellprob_threshold) + 'ft' + str(flow_threshold)
    Cell.safe_masks(masks, path_output_cells_diams, masks_name)
    diams_name = 'diams_' + 'cpt' + str(cellprob_threshold) + 'ft' + str(flow_threshold)
    Cell.safe_diams(diams, path_output_cells_diams, diams_name)

    # get parameters for adherent-cell detection from user
    time_for_adherent, delay, images_threshold, compare_threshold = prf.get_adhcelldet_parmas(diams)

    # search adherent cells
    number_adherent_cells, number_cells_total, adherent_cells = AdherentCell.find_adherent_cells(cells, diams,
                                                                                                 images_threshold,
                                                                                                 compare_threshold)
    # find number of adherent cells on each image
    nr_adherent_cells_on_img = AdherentCell.nr_adherent_cells_on_img(adherent_cells, len(imgs))

    # create new subdirectory for data with the selected time and tolerance
    path_output_adherent = os.path.join(path_output_cells_diams, 'time' + str(time_for_adherent) + 's_tolerance' + str(compare_threshold))
    os.mkdir(path_output_adherent)

    # create '.txt'-file to save data
    txtfile = open(os.path.join(path_output_adherent, 'celladhesion_' + 'time' + str(time_for_adherent) + 's_tolerance'
                                + str(compare_threshold) + '.txt'), 'w+')

    # save the used masks, diams and parameters in the text file
    prf.save_params_in_txtfile(txtfile, masks_name, diams_name, time_for_adherent, delay, images_threshold,
                               compare_threshold)

    # save the information found about the adherent cells in the text file
    prf.save_adh_in_txtfile(txtfile, number_adherent_cells, number_cells_total, adherent_cells, cells,
                            nr_adherent_cells_on_img)

    # overlay outlines of the detected cells on the input images and mark the adherent cells
    overlay = imf.overlay_outlines(imgs, masks)
    # 'overlay_adherent_squares' can only be done if list contains 'adherent_cell'-objects
    if isinstance(adherent_cells[0], AdherentCell):
        overlay = imf.overlay_adherent_squares(overlay, adherent_cells, 30)

    # show created images and save them in the subdirectory
    prf.show_and_save_result_imgs(overlay, path_output_adherent, "celladhesion")

# use already created masks
elif new_or_use_or_test == "u":
    # get images from user
    path_imgs = input("Path of '.tif'-images: ").replace('\\', '/')
    imgs = imf.read_tifs(path_imgs)

    # get masks/diams from user
    path_input = input("Path where masks and diams are saved: ").replace('\\', '/')
    masks_name = str(input("Name of '.npy'-file with masks (without ending): ")) + '.npy'
    masks = imf.load_masks(os.path.join(path_input, masks_name))
    diams_name = str(input("Name of '.txt'-file with diameters (without ending): ")) + '.txt'
    diams = imf.load_diams(os.path.join(path_input, diams_name))


    while True:
        # get parameters from user
        time_for_adherent, delay, images_threshold, compare_threshold = prf.get_adhcelldet_parmas(diams)

        # create new subdirectory for the data with the selected time and tolerance
        path_output_adherent = os.path.join(path_input, 'time' + str(time_for_adherent) + 's_tolerance' + str(compare_threshold))
        os.mkdir(path_output_adherent)

        # find cells and adherent cells
        cells = Cell.find_cells_from_masks(masks)
        number_adherent_cells, number_cells_total, adherent_cells = AdherentCell.find_adherent_cells(cells, diams,
                                                                                                     images_threshold,
                                                                                                     compare_threshold)
        # find number of adherent cells on each image
        nr_adherent_cells_on_img = AdherentCell.nr_adherent_cells_on_img(adherent_cells, len(imgs))

        # create '.txt'-file to save the data
        txtfile = open(os.path.join(path_output_adherent, 'celladhesion_' + 'time' + str(time_for_adherent) + 's_tolerance'
                                    + str(compare_threshold) + '.txt'), 'w+')

        # save the used masks, diams and parameters in the text file
        prf.save_params_in_txtfile(txtfile, masks_name, diams_name, time_for_adherent, delay, images_threshold,
                                   compare_threshold)

        # save the found information about the adherent cells in the text file
        prf.save_adh_in_txtfile(txtfile, number_adherent_cells, number_cells_total, adherent_cells, cells,
                                nr_adherent_cells_on_img)

        # overlay outlines of the detected cells on the input images and mark the adherent cells
        overlay = imf.overlay_outlines(imgs, masks)
        # 'overlay_adherent_squares' can only be done if list contains 'adherent_cell'-objects
        if isinstance(adherent_cells[0], AdherentCell):
            overlay = imf.overlay_adherent_squares(overlay, adherent_cells, 30)

        # show created images and save them in the subdirectory
        prf.show_and_save_result_imgs(overlay, path_output_adherent, "celladhesion")

        # check if user wants to overlay the adherent cells on an image of the call layer
        cells_on_phc = input("\nOverlay adherent cells on image of the cell layer? [y / n]: ")
        if cells_on_phc == "y":

            # get path and image of the cell layer
            path_phc = input("Path where image of cell layer is saved: ").replace('\\', '/')
            name_phc = str(input("Name of '.tif'-file of cell layer (without ending): ")) + '.tif'
            img_phc = imf.read_single_tif(os.path.join(path_phc, name_phc))

            # create new subdirectory for the overlayed images
            path_output_phc = os.path.join(path_output_adherent, 'celladhesion_overlayPhc')
            os.mkdir(path_output_phc)

            # overlay adherent cells on the image and save the result images in the directory
            adh_over_phc, adherent_mask_numbers = imf.adherent_cells_over_phasecontrast(img_phc, masks, adherent_cells)
            prf.show_and_save_result_imgs(adh_over_phc, path_output_phc, "overlayPhc")


        # check if user wants to rerun or stop the program
        rerun = input("Rerun? [y / n]: ")
        # if no, break out of the loop to stop the program
        if rerun == "n":
            break
        else:
            # if yes, check if user wants to use the same masks as before or new ones
            new_or_same_masks = input("Use NEW or SAME masks? [n / s]: ")
            # if the user chooses new ones, get new images, masks and diameters
            if new_or_same_masks == "n":
                print("\n\n")
                # get images from user
                path_imgs = input("Path of '.tif'-images: ").replace('\\', '/')
                imgs = imf.read_tifs(path_imgs)

                # get masks/diams from user
                path_input = input("Path where masks and diams are saved: ").replace('\\', '/')
                masks_name = str(input("Name of '.npy'-file with masks (without ending): ")) + '.npy'
                masks = imf.load_masks(os.path.join(path_input, masks_name))
                diams_name = str(input("Name of '.txt'-file with diameters (without ending): ")) + '.txt'
                diams = imf.load_diams(os.path.join(path_input, diams_name))


# run on test images to find parameters for cell detection
elif new_or_use_or_test == "t":
    # get test-images from user
    path_imgs = input("Path of '.tif' test-images: ").replace('\\', '/')
    imgs = imf.read_tifs(path_imgs)

    while True:
        # get parameters for cell detection from user
        cellprob_threshold, flow_threshold = prf.get_celldet_params()

        # run 'find_cells' method, overlay cell outlines
        cells, diams, masks = Cell.find_cells(imgs, cellprob_threshold=cellprob_threshold, flow_threshold=flow_threshold)
        overlay = imf.overlay_outlines(imgs, masks)

        # show images
        for i in range(len(overlay)):
            skimage.io.imshow(overlay[i])
            plt.title("testimg{0},  cpt={1}, ft={2}          ".format(i, cellprob_threshold, flow_threshold))
            skimage.io.show()

        # check if user wants to rerun with different parameters
        rerun = input("Rerun? [y / n]: ")
        if rerun == "n":
            break
        else:
            print("Set new parameters.")

# Run Code to find masks and diams for multiple data inputs
elif new_or_use_or_test == "m":
    path_input = list()
    imgs = list()
    cellprob_threshold = list()
    flow_threshold = list()
    while True:
        path_input_temp = input("Path of '.tif'-images or 'stop', if no more paths shall be read: ")
        if path_input_temp == "stop":
            break
        path_input.append(path_input_temp)
        imgs.append(imf.read_tifs(path_input_temp))
        cellprob_threshold_temp, flow_threshold_temp = prf.get_celldet_params()
        cellprob_threshold.append(cellprob_threshold_temp)
        flow_threshold.append(flow_threshold_temp)
        print("\n")

    for data_nr in range(len(path_input)):
        # create new directory for the data with the selected 'cellprob_threshold' and 'flow_threshold'
        path_output_cells_diams = os.path.join(path_input[data_nr],
                                               "celladhesion_" + 'cpt' + str(cellprob_threshold[data_nr]) + 'ft' + str(
                                                   flow_threshold[data_nr]))
        os.mkdir(path_output_cells_diams)

        # run 'find_cells' method and save masks and diams (names: include 'cellprob_threshold' and 'flow_threshold')
        cells, diams, masks = Cell.find_cells(imgs[data_nr], cellprob_threshold=cellprob_threshold[data_nr],
                                              flow_threshold=flow_threshold[data_nr])
        masks_name = 'masks_' + 'cpt' + str(cellprob_threshold[data_nr]) + 'ft' + str(flow_threshold[data_nr])
        Cell.safe_masks(masks, path_output_cells_diams, masks_name)
        diams_name = 'diams_' + 'cpt' + str(cellprob_threshold[data_nr]) + 'ft' + str(flow_threshold[data_nr])
        Cell.safe_diams(diams, path_output_cells_diams, diams_name)

elif new_or_use_or_test == "c":
    # get images from user
    path_imgs = "C:/Users/woerl/Desktop/Test/Phc"
    imgs = imf.read_tifs(path_imgs)

    # get masks/diams from user
    path_input = "C:/Users/woerl/Desktop/Test/Phc/celladhesion_cpt0.8ft0.2"
    masks_name = 'm' + '.npy'
    masks = imf.load_masks(os.path.join(path_input, masks_name))
    diams_name = 'd' + '.txt'
    diams = imf.load_diams(os.path.join(path_input, diams_name))


    # get parameters from user
    time_for_adherent = 60
    delay = 30
    images_threshold = 3
    compare_threshold = 10

    """"# create new subdirectory for the data with the selected time and tolerance
    path_output_adherent = os.path.join(path_input,
                                        'time' + str(time_for_adherent) + 's_tolerance' + str(compare_threshold))
    os.mkdir(path_output_adherent)"""

    # find cells and adherent cells
    cells = Cell.find_cells_from_masks(masks)
    number_adherent_cells, number_cells_total, adherent_cells = AdherentCell.find_adherent_cells(cells, diams,
                                                                                                 images_threshold,
                                                                                               compare_threshold)
    """"# find number of adherent cells on each image
    nr_adherent_cells_on_img = AdherentCell.nr_adherent_cells_on_img(adherent_cells, len(imgs))

    # create '.txt'-file to save the data
    txtfile = open(
        os.path.join(path_output_adherent, 'celladhesion_' + 'time' + str(time_for_adherent) + 's_tolerance'
                     + str(compare_threshold) + '.txt'), 'w+')

    # save the used masks, diams and parameters in the text file
    prf.save_params_in_txtfile(txtfile, masks_name, diams_name, time_for_adherent, delay, images_threshold,
                               compare_threshold)

    # save the found information about the adherent cells in the text file
    prf.save_adh_in_txtfile(txtfile, number_adherent_cells, number_cells_total, adherent_cells, cells,
                            nr_adherent_cells_on_img)

    # overlay outlines of the detected cells on the input images and mark the adherent cells
    overlay = imf.overlay_outlines(imgs, masks)
    # 'overlay_adherent_squares' can only be done if list contains 'adherent_cell'-objects
    if isinstance(adherent_cells[0], AdherentCell):
        overlay = imf.overlay_adherent_squares(overlay, adherent_cells, 30)

    # show created images and save them in the subdirectory
    prf.show_and_save_result_imgs(overlay, path_output_adherent, "celladhesion")

    # check if user wants to overlay the adherent cells on an image of the call layer
    cells_on_phc = input("\nOverlay adherent cells on image of the cell layer? [y / n]: ")
    if cells_on_phc == "y": """

    # get path and image of the cell layer
    path_phc = "C:/Users/woerl/Desktop/Test"
    name_phc = "Rasen" + '.tif'
    img_phc = imf.read_single_tif(os.path.join(path_phc, name_phc))

    """# create new subdirectory for the overlayed images
    path_output_phc = os.path.join(path_output_adherent, 'celladhesion_overlayPhc')
    os.mkdir(path_output_phc)"""

    # overlay adherent cells on the image and save the result images in the directory
    adh_over_phc, adherent_mask_numbers = imf.adherent_cells_over_phasecontrast(img_phc, masks, adherent_cells)
    #prf.show_and_save_result_imgs(adh_over_phc, path_output_phc, "overlayPhc")
    print(adherent_mask_numbers[0])
    print(adherent_mask_numbers[1])
    print(len(adherent_mask_numbers[0]))
    print(len(adherent_mask_numbers))














