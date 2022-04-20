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

with open("config.json", "r") as jsonFile:
    config = json.load(jsonFile)
jsonFile.close()

print("\n\n\nWelcome to 'celladhesion'! \n")
print("__________________________________________________________________________________________\n")
print("Current configuration: \n\n")
print("Cell detection parameters: ")
print(config["celldet"])
print("\nAdherent Cell detection parameters: ")
print(config["adhcelldet"])
print("\n__________________________________________________________________________________________\n")


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
                                                       config.celldet["cellprob_threshold"]) + 'ft' + str(
                                                       config.celldet["flow_threshold"]))
            os.mkdir(path_output_cells_diams)

            # run 'find_cells' method and save masks and diams (names: include 'cellprob_threshold' and 'flow_threshold')
            masks, diams = Cell.run_cellpose(imgs[data_nr], cellprob_threshold=config.celldet["cellprob_threshold"],
                                             flow_threshold=config.celldet["flow_threshold"])
            masks_name = 'masks_' + 'cpt' + str(config.celldet["cellprob_threshold"]) + 'ft' + str(config.celldet["flow_threshold"])
            Cell.safe_masks(masks, path_output_cells_diams, masks_name)
            diams_name = 'diams_' + 'cpt' + str(config.celldet["cellprob_threshold"]) + 'ft' + str(config.celldet["flow_threshold"])
            Cell.safe_diams(diams, path_output_cells_diams, diams_name)

        print("\n__________________________________________________________________________________________\n")
        print("All masks/diameters found and saved! ")
        print("\n__________________________________________________________________________________________\n")

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


