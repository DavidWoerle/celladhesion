import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"     # Suppress warning when program is run on different computer
import cellpose.plot
import matplotlib.pyplot as plt
import imagefunctions as imf
import skimage.io
from Cell import Cell
from AdherentCell import AdherentCell
import programrun_functions as prf
import json


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
print("\nProgram parameters: ")
print(config["program"])
print("\n__________________________________________________________________________________________\n")


while True:

    # let user choose the program mode
    print("Choose mode: \n")
    print("1.) Create NEW masks/diameters \n2.) USE already created masks to run the program \n3.) Determine CONFLUENCE"
          " of a mask \n4.) Determine INTENSITY of images \n5.) Change CONFIGURATION \n")

    program_choice = input("Type the mode number and press enter:  ")
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
        # get images from user, if overlay is required
        if config["program"]["overlay_outlines"] == 'y':
            path_imgs = input("Path of '.tif'-images: ").replace('\\', '/')
            imgs = imf.read_tifs(path_imgs)

        # get masks/diams from user
        path_input = input("Path where masks and diams are saved: ").replace('\\', '/')
        if config["program"]["auto_load_masks_and_diams"] == 'y':
            masks, masks_name = imf.auto_load_masks(path_input)
            diams, diams_name = imf.auto_load_diams(path_input)
        else:
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
            number_adherent_cells, number_cells_total, adherent_cells, non_adherent_cells = AdherentCell.find_adherent_cells(cells, diams,
                                                                                                         config["adhcelldet"]["images_threshold"],
                                                                                                         config["adhcelldet"]["tolerance"])
            # find number of adherent cells on each image
            nr_adherent_cells_on_img = AdherentCell.nr_adherent_cells_on_img(adherent_cells, len(masks))

            # Create Boxplot to show the size distribution and save the sizes
            prf.boxplot(non_adherent_cells, adherent_cells, path_output_adherent, 'sizes')

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

            # check if user wants to overlay outlines
            if config["program"]["overlay_outlines"] == 'y':
                # overlay outlines of the detected cells on the input images and mark the adherent cells
                overlay = imf.overlay_outlines(imgs, masks)
                # 'overlay_adherent_squares' can only be done if list contains 'adherent_cell'-objects
                if isinstance(adherent_cells[0], AdherentCell):
                    overlay = imf.overlay_adherent_squares(overlay, adherent_cells, 30)

                # show created images and save them in the subdirectory
                prf.show_and_save_result_imgs(overlay, path_output_adherent, "celladhesion")

            # check if user wants to filter the cells for their position
            if config["program"]["filter_cells"] == "y":
                print("\n__________________________________________________________________________________________\n")
                print("Filtering Cells for their position:")
                # get the background mask
                path_input_background_mask = input("\nPath where image with background masks is saved (if same as "
                                                   "before, just press enter):  ").replace('\\', '/')
                # no new path -> use the same as before
                if path_input_background_mask == "":
                    path_input_background_mask = path_input
                background_mask_name = str(
                    input("Name of '.png'-file with background masks (without ending): ")) + '.png'
                background_mask = imf.read_single_img(os.path.join(path_input_background_mask, background_mask_name))

                # filter the cells and find the new celladhesion data
                filtered_cells = list()
                for i in range(len(cells)):
                    filtered_cells.append(Cell.filter_for_position(cells[i], background_mask))
                number_adherent_cells_filtered, number_cells_total_filtered, adherent_cells_filtered, non_adherent_cells_filtered = AdherentCell.find_adherent_cells(filtered_cells,
                                                                                                                 diams,
                                                                                                                 config["adhcelldet"][
                                                                                                                     "images_threshold"],
                                                                                                                 config["adhcelldet"][
                                                                                                                     "tolerance"])

                # find number of adherent cells (filtered) on each image
                nr_adherent_cells_on_img_filtered = AdherentCell.nr_adherent_cells_on_img(adherent_cells_filtered, len(masks))

                # Create boxplot to show size distribution and save the sizes
                prf.boxplot(non_adherent_cells_filtered, adherent_cells_filtered, path_output_adherent, 'sizes_filtered')

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

                # save celladhesion data in a '.csv'-file
                prf.celladhesion_to_csv(os.path.join(path_output_adherent, 'celladhesion_data.csv'),
                                        number_adherent_cells, len(cells[0]), nr_adherent_cells_on_img, confluence,
                                        number_adherent_cells_filtered, len(filtered_cells[0]),
                                        nr_adherent_cells_on_img_filtered
                                        )

            # if no filtering executed, save to '.csv' without optional filter arguments
            else:
                prf.celladhesion_to_csv(os.path.join(path_output_adherent, 'celladhesion_data.csv'),
                                        number_adherent_cells, len(cells[0]), nr_adherent_cells_on_img)

            txtfile.close()     # close txt file to safe the data

            # check if user wants to overlay the adherent cells on an image of the call layer
            if config["program"]["overlay_phc"] == "y":
                print("\n__________________________________________________________________________________________\n")
                print("Overlaying adherent Cells on image of the cell layer: ")

                # get path and image of the cell layer
                path_phc = input("\nPath where image of cell layer is saved (if same as before, just press enter):  ").replace('\\', '/')
                # no new path -> use the same as before
                if path_phc == "":
                    if config["program"]["filter_cells"] == "y":
                        path_phc = path_input_background_mask
                    else:
                        path_phc = path_input
                name_phc = str(input("Name of '.tif'-file of cell layer (without ending):  ")) + '.tif'
                img_phc = imf.read_single_img(os.path.join(path_phc, name_phc))

                # create new subdirectory for the overlayed images
                path_output_phc = os.path.join(path_output_adherent, 'celladhesion_overlayPhc')
                os.mkdir(path_output_phc)

                # overlay adherent cells on the image and save the result images in the directory
                adh_over_phc = imf.adherent_cells_over_phasecontrast(img_phc, masks, adherent_cells, [1.0, 0, 0])
                if config["program"]["filter_cells"] == "y":
                    adh_over_phc = imf.overlay_adherent_squares(adh_over_phc, adherent_cells_filtered, 30)
                prf.show_and_save_result_imgs(adh_over_phc, path_output_phc, "overlayPhc")

            print("\n__________________________________________________________________________________________\n")
            print("All data found and saved! ")
            print("\n__________________________________________________________________________________________\n")

            # check if user wants to rerun or stop the program
            rerun = input("\nRerun? [y / n]: ")
            # if no, break out of the loop to stop the program
            if rerun == "n":
                break
            else:
                print("\n\n")
                print("\n__________________________________________________________________________________________"
                      "\n")

                # get images from user, if overlay is required
                if config["program"]["overlay_outlines"] == 'y':
                    path_imgs = input("Path of '.tif'-images: ").replace('\\', '/')
                    imgs = imf.read_tifs(path_imgs)

                # get masks/diams from user
                path_input = input("Path where masks and diams are saved: ").replace('\\', '/')
                if config["program"]["auto_load_masks_and_diams"] == 'y':
                    masks, masks_name = imf.auto_load_masks(path_input)
                    diams, diams_name = imf.auto_load_diams(path_input)
                else:
                    masks_name = str(input("Name of '.npy'-file with masks (without ending): ")) + '.npy'
                    masks = imf.load_masks(os.path.join(path_input, masks_name))
                    diams_name = str(input("Name of '.txt'-file with diameters (without ending): ")) + '.txt'
                    diams = imf.load_diams(os.path.join(path_input, diams_name))

    elif program_choice == "3":

        print("Determine CONFLUENCE of a mask \n\n")

        while True:
            # get path where '.png'-imgs of mask are saved
            path_mask = input("\nPath where '.png'-image/s of background mask/s is/are saved:  ").replace('\\', '/')
            imgs_mask = imf.read_pngs(path_mask) # read images

            print("Confluence [%]: \n")

            for i in range(len(imgs_mask)):
                confluence = Cell.determine_confluence(imgs_mask[i])    # determine confluence of each mask
                print(confluence)   # print result

            print("\n__________________________________________________________________________________________\n")
            print("All data found! ")
            print("\n__________________________________________________________________________________________\n")

            # check if user wants to rerun or stop the program
            rerun = input("\nRerun? [y / n]: ")
            # if no, break out of the loop to stop the program
            if rerun == "n":
                break
            print("\n__________________________________________________________________________________________\n")

    elif program_choice == "4":
        print("Determine INTENSITY of images \n\n")

        while True:
            path_imgs = input("Path of '.tif'-images: ").replace('\\', '/')
            imgs = imf.read_tifs(path_imgs)

            background_choice = input("\nUse background mask to find intensities according to the background mask? "
                                      "[y / n]:  ")

            if background_choice == "y":
                path_background_mask = input("\nPath where '.png'-image/s of background mask/s is/are saved (if same as "
                                             "before, just press enter):  ").replace('\\', '/')
                # no new path -> use the same as before
                if path_background_mask == "":
                    path_background_mask = path_imgs

                imgs_background_mask = imf.read_pngs(path_background_mask)
                #name_background_mask = str(input("\nName of '.png'-file of cell layer (without ending):  ")) + '.png'
                #img_background_mask = imf.read_single_img(os.path.join(path_background_mask, name_background_mask))

                intensity = imf.find_intensity(imgs, imgs_background_mask)
                imgs_background_overlay = imf.background_mask_over_img(imgs, imgs_background_mask)

                # create new subdirectory for the output data
                path_output_intensity = os.path.join(path_imgs, 'intensity_mask')
                os.mkdir(path_output_intensity)

                for i in range(len(imgs)):
                    name = "intensity" + str(i) + "-intM_" + str(intensity[i]["mask"]) + "-intR_" \
                           + str(intensity[i]["rest"]) + "-confl_" + str(intensity[i]["confluence"])
                    prf.show_and_save_result_imgs(imgs_background_overlay[i], path_output_intensity, name)

            else:
                intensity = imf.find_intensity(imgs)

                # create new subdirectory for the output data
                path_output_intensity = os.path.join(path_imgs, 'intensity_total')
                os.mkdir(path_output_intensity)

                for i in range(len(imgs)):
                    name = "intensity" + str(i) + "_" + str(intensity[i])
                    prf.show_and_save_result_imgs(imgs[i], path_output_intensity, name)

            # save intensity data to csv file
            prf.intensities_to_csv(intensity, os.path.join(path_imgs, 'intensity_data.csv'))

            print("\n__________________________________________________________________________________________\n")
            print("All data found and saved! ")
            print("\n__________________________________________________________________________________________\n")

            # check if user wants to rerun or stop the program
            rerun = input("\nRerun? [y / n]: ")
            # if no, break out of the loop to stop the program
            if rerun == "n":
                break
            print("\n__________________________________________________________________________________________\n")

    elif program_choice == "5":
        print("Change CONFIGURATION \n\n")

        change_celldet = input("Change Cell detection parameters? [y / n]:  ")
        if change_celldet == "y":
            print("\n")
            prf.change_celldet_params()

        change_adhcelldet = input("\nChange Adherent Cell detection parameters: [y / n]:  ")
        if change_adhcelldet == "y":
            print("\n")
            prf.change_adhcelldet_params()

        change_program = input("\nChange program parameters: [y / n]:  ")
        if change_program == "y":
            print("\n")
            prf.change_program_params()

        with open("config.json", "r") as jsonFile:
            config = json.load(jsonFile)
        jsonFile.close()

        print("__________________________________________________________________________________________\n")
        print("NEW configuration: \n\n")
        print("Cell detection parameters: ")
        print(config["celldet"])
        print("\nAdherent Cell detection parameters: ")
        print(config["adhcelldet"])
        print("\nProgram parameters: ")
        print(config["program"])
        print("\n__________________________________________________________________________________________\n")

    else:
        print("Invalid choice!")

    close = input("\nClose the program? [y / n]:  ")
    print("\n")
    if close == "y":
        break


