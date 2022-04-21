import os
import cellpose.plot
import matplotlib.pyplot as plt
import imagefunctions as imf
import skimage.io
from Cell import Cell
from AdherentCell import AdherentCell
import programrun_functions as prf
import json

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"     # Suppress warning when program is run on different computer

# load the config file
with open("config.json", "r") as jsonFile:
    config = json.load(jsonFile)
jsonFile.close()

# header with the current configuration
print("\n\n\nWelcome to 'celladhesion'! \n")
print("__________________________________________________________________________________________\n")
print("Current configuration: \n\n")
print("Cell detection parameters: ")
print(config["celldet"])
print("\nAdherent Cell detection parameters: ")
print(config["adhcelldet"])
print("\n__________________________________________________________________________________________\n")


# let user choose the program mode
print("Choose mode: \n")
print("1.) Create NEW masks/diameters \n2.) USE already created masks to run the program \n3.) Determine CONFLUENCE of \
a mask \n4.) Change CONFIGURATION \n")


while True:
    program_choice = input("Type the number and press enter:  ")
    print("\n__________________________________________________________________________________________\n")

    if program_choice == "1":
        print("Create NEW masks/diameters \n\n")
        path_input = list()
        imgs = list()
        while True:
            path_input_temp = input("Path of '.tif'-images or 'stop', if no more paths shall be read: ")
            if path_input_temp == "stop":
                break
            path_input.append(path_input_temp)
            imgs.append(imf.read_tifs(path_input_temp))
            print("\n")

        for data_nr in range(len(path_input)):
            # create new directory for the data with the selected 'cellprob_threshold' and 'flow_threshold'
            path_output_cells_diams = os.path.join(path_input[data_nr],
                                                   "celladhesion_" + 'cpt' + str(
                                                       config["celldet"]["cellprob_threshold"]) + 'ft' + str(
                                                       config["celldet"]["flow_threshold"]))
            os.mkdir(path_output_cells_diams)

            # run 'find_cells' method and save masks and diams (names: include 'cellprob_threshold' and 'flow_threshold')
            masks, diams = Cell.run_cellpose(imgs[data_nr], cellprob_threshold=config["celldet"]["cellprob_threshold"],
                                             flow_threshold=config["celldet"]["flow_threshold"])
            masks_name = 'masks_' + 'cpt' + str(config["celldet"]["cellprob_threshold"]) + 'ft' + str(config["celldet"]["flow_threshold"])
            Cell.safe_masks(masks, path_output_cells_diams, masks_name)
            diams_name = 'diams_' + 'cpt' + str(config["celldet"]["cellprob_threshold"]) + 'ft' + str(config["celldet"]["flow_threshold"])
            Cell.safe_diams(diams, path_output_cells_diams, diams_name)

        print("\n__________________________________________________________________________________________\n")
        print("All masks/diameters found and saved! ")
        print("\n__________________________________________________________________________________________\n")

    elif program_choice == "2":
        print("USE already created masks to run the program \n\n")
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

            # create new subdirectory for the data with the selected time and tolerance
            path_output_adherent = os.path.join(path_input, 'time' + str(config["adhcelldet"]["time_for_adherent[s]"]) +
                                                's_tolerance' + str(config["adhcelldet"]["tolerance"]))
            os.mkdir(path_output_adherent)

            # find cells and adherent cells
            cells = Cell.find_cells(masks)
            number_adherent_cells, number_cells_total, adherent_cells = AdherentCell.find_adherent_cells(cells, diams,
                                                                                                         config["adhcelldet"]["images_threshold"],
                                                                                                         config["adhcelldet"]["tolerance"])
            # find number of adherent cells on each image
            nr_adherent_cells_on_img = AdherentCell.nr_adherent_cells_on_img(adherent_cells, len(imgs))

            # create '.txt'-file to save the data
            txtfile = open(
                os.path.join(path_output_adherent, 'celladhesion_' + 'time'
                             + str(config["adhcelldet"]["time_for_adherent[s]"]) + 's_tolerance'
                             + str(config["adhcelldet"]["tolerance"]) + '.txt'), 'w+')

            # save the used masks, diams and parameters in the text file
            prf.save_config_in_txtfile(txtfile, masks_name, diams_name, config)

            # save the found information about the adherent cells in the text file
            txtfile.write("All cells: \n\n")
            prf.save_adh_in_txtfile(txtfile, number_adherent_cells, number_cells_total, adherent_cells, cells,
                                    nr_adherent_cells_on_img)

            # save number of adherent cells on image in a '.csv'-file
            prf.number_adh_on_image_to_csv(nr_adherent_cells_on_img,
                                           os.path.join(path_output_adherent, 'adh_on_img.csv'))

            # overlay outlines of the detected cells on the input images and mark the adherent cells
            overlay = imf.overlay_outlines(imgs, masks)
            # 'overlay_adherent_squares' can only be done if list contains 'adherent_cell'-objects
            if isinstance(adherent_cells[0], AdherentCell):
                overlay = imf.overlay_adherent_squares(overlay, adherent_cells, 30)

            # show created images and save them in the subdirectory
            prf.show_and_save_result_imgs(overlay, path_output_adherent, "celladhesion")

            # check if user wants to filter the cells for their position
            print("\n__________________________________________________________________________________________\n")
            filter_choice = input("Filter cells for their position on a background mask? [y / n]:  ")
            if filter_choice == "y":
                # get the background mask
                path_input_background_mask = input("Path where image with background masks is saved: ").replace('\\', '/')
                background_mask_name = str(
                    input("Name of '.png'-file with background masks (without ending): ")) + '.png'
                background_mask = imf.read_single_img(os.path.join(path_input_background_mask, background_mask_name))

                # filter the cells and find the new celladhesion data
                filtered_cells = list()
                for i in range(len(cells)):
                    filtered_cells.append(Cell.filter_for_position(cells[i], background_mask))
                number_adherent_cells_filtered, number_cells_total_filtered, adherent_cells_filtered = AdherentCell.find_adherent_cells(filtered_cells,
                                                                                                                 diams,
                                                                                                                 config["adhcelldet"][
                                                                                                                     "images_threshold"],
                                                                                                                 config["adhcelldet"][
                                                                                                                     "tolerance"])

                # find number of adherent cells (filtered) on each image
                nr_adherent_cells_on_img_filtered = AdherentCell.nr_adherent_cells_on_img(adherent_cells_filtered, len(imgs))

                # determine confluence of the background mask
                confluence = Cell.determine_confluence(background_mask)

                # save confluence to .txt file
                prf.save_confluence_in_txtfile(txtfile, background_mask_name, confluence)

                # save the found information about the filtered adherent cells in the text file
                txtfile.write("Filtered cells: \n\n")
                prf.save_adh_in_txtfile(txtfile, number_adherent_cells_filtered, number_cells_total_filtered,
                                        adherent_cells_filtered, filtered_cells,
                                        nr_adherent_cells_on_img_filtered)

                # save number of adherent cells on image in a '.csv'-file
                prf.number_adh_on_image_to_csv(nr_adherent_cells_on_img_filtered,
                                               os.path.join(path_output_adherent, 'adh_on_img_filtered.csv'))

            # check if user wants to overlay the adherent cells on an image of the call layer
            print("\n__________________________________________________________________________________________\n")
            cells_on_phc = input("\nOverlay adherent cells on image of the cell layer? [y / n]:  ")
            if cells_on_phc == "y":

                # get path and image of the cell layer
                path_phc = input("Path where image of cell layer is saved: ").replace('\\', '/')
                name_phc = str(input("Name of '.tif'-file of cell layer (without ending):  ")) + '.tif'
                img_phc = imf.read_single_img(os.path.join(path_phc, name_phc))

                # create new subdirectory for the overlayed images
                path_output_phc = os.path.join(path_output_adherent, 'celladhesion_overlayPhc')
                os.mkdir(path_output_phc)

                # overlay adherent cells on the image and save the result images in the directory
                adh_over_phc = imf.adherent_cells_over_phasecontrast(img_phc, masks, adherent_cells, [1.0, 0, 0])
                if filter_choice == "y":
                    adh_over_phc = imf.overlay_adherent_squares(adh_over_phc, adherent_cells_filtered, 30)
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

    elif program_choice == "4":
        print("Change CONFIGURATION: \n\n")

        change_celldet = input("Change Cell detection parameters? [y / n]:  ")
        if change_celldet == "y":
            print("\n")
            prf.change_celldet_params()

        change_adhcelldet = input("\nChange Adherent Cell detection parameters: [y / n]:  ")
        if change_adhcelldet == "y":
            print("\n")
            prf.change_adhcelldet_params()

        with open("config.json", "r") as jsonFile:
            config = json.load(jsonFile)
        jsonFile.close()

        print("__________________________________________________________________________________________\n")
        print("NEW configuration: \n\n")
        print("Cell detection parameters: ")
        print(config["celldet"])
        print("\nAdherent Cell detection parameters: ")
        print(config["adhcelldet"])
        print("\n__________________________________________________________________________________________\n")

    else:
        print("Invalid choice!\n")

    close = input("Close the program? [y / n]:  ")
    print("\n")
    if close == "y":
        break


