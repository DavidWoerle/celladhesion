import json
import Cell
import AdherentCell
import imagefunctions as imf
from AdherentCell import AdherentCell
import skimage.io
import os.path
import csv
import config
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_ind


def change_celldet_params():
    """ Changes the cell detection parameters in the config file"""

    # load the current configuration
    with open("config.json", "r") as jsonFile:
        config = json.load(jsonFile)

    while True:
        try:
            config["celldet"]["cellprob_threshold"] = float(input("cellprob_threshold (between 0.0 and 1.0, higher: less masks will be found): "))
            break
        except ValueError:
            print("cellprob_threshold not valid")
    while True:
        try:
            config["celldet"]["flow_threshold"] = float(input("flow_threshold (between 0.0 and 1.0, lower: less masks will be found): "))
            break
        except ValueError:
            print("flow_threshold not valid")

    # write the new parameters to the config file
    with open("config.json", "w") as jsonFile:
        json.dump(config, jsonFile)
    jsonFile.close()


def change_adhcelldet_params():
    """ Changes the cell detection parameters in the config file"""

    # load the current configuration
    with open("config.json", "r") as jsonFile:
        config = json.load(jsonFile)

    while True:
        try:
            config["adhcelldet"]["time_for_adherent[s]"] = float(input("time [s] to be detected as adherent: "))
            break
        except ValueError:
            print("time not valid")
    while True:
        try:
            config["adhcelldet"]["delay[s]"] = float(input("delay [s] between images: "))
            break
        except ValueError:
            print("delay not valid")

    config["adhcelldet"]["images_threshold"] = imf.time_to_nrimgs(config["adhcelldet"]["time_for_adherent[s]"],
                                                               config["adhcelldet"]["delay[s]"])
    while True:
        try:
            config["adhcelldet"]["tolerance"] = int(input("tolerance radius for comparing cell positions: "))
            break
        except ValueError:
            print("tolerance radius not valid")

    # write the new parameters to the config file
    with open("config.json", "w") as jsonFile:
        json.dump(config, jsonFile)
    jsonFile.close()


def change_program_params():
    """ Changes the program parameters in the config file"""

    # load the current configuration
    with open("config.json", "r") as jsonFile:
        config = json.load(jsonFile)

    while True:
        inpt = input("Overlay outlines of the detected cells on the input images and mark the adherent cells? [y / n]: ")
        try:
            if inpt == 'y' or inpt == 'n':
                config["program"]["overlay_outlines"] = inpt
                break
            else:
                raise ValueError("Only 'y' or 'n' allowed")
        except ValueError:
            print("Only 'y' or 'n' allowed")

    while True:
        inpt = input("Filter cells for their position on a background mask? [y / n]:  ")
        try:
            if inpt == 'y' or inpt == 'n':
                config["program"]["filter_cells"] = inpt
                break
            else:
                raise ValueError("Only 'y' or 'n' allowed")
        except ValueError:
            print("Only 'y' or 'n' allowed")

    while True:
        inpt = input("Overlay adherent cells on image of the cell layer? [y / n]:  ")
        try:
            if inpt == 'y' or inpt == 'n':
                config["program"]["overlay_phc"] = inpt
                break
            else:
                raise ValueError("Only 'y' or 'n' allowed")
        except ValueError:
            print("Only 'y' or 'n' allowed")

    while True:
        inpt = input("Auto-load masks and diameters from the selected directory? [y / n]:  ")
        try:
            if inpt == 'y' or inpt == 'n':
                config["program"]["auto_load_masks_and_diams"] = inpt
                break
            else:
                raise ValueError("Only 'y' or 'n' allowed")
        except ValueError:
            print("Only 'y' or 'n' allowed")

    # write the new parameters to the config file
    with open("config.json", "w") as jsonFile:
        json.dump(config, jsonFile)
    jsonFile.close()



"""def get_celldet_params():
    # get parameters for cell detection from user
    while True:
        try:
            cellprob_threshold = float(input("cellprob_threshold (between 0.0 and 1.0, higher: less masks will be found): "))
            break
        except ValueError:
            print("cellprob_threshold not valid")
    while True:
        try:
            flow_threshold = float(input("flow_threshold (between 0.0 and 1.0, lower: less masks will be found): "))
            break
        except ValueError:
            print("flow_threshold not valid")
    return cellprob_threshold, flow_threshold"""





"""def get_adhcelldet_params(diams):
    # get parameters for adherent-cell detection from user
    while True:
        try:
            time_for_adherent = float(input("time [s] to be detected as adherent: "))
            break
        except ValueError:
            print("time not valid")
    while True:
        try:
            delay = float(input("delay [s] between images: "))
            break
        except ValueError:
            print("delay not valid")
    images_threshold = imf.time_to_nrimgs(time_for_adherent, delay)
    while True:
        try:
            """"""compare_threshold = int(input(
                "tolerance radius for comparing cell positions: ".format(
                    min(diams) / 2)))""""""
            compare_threshold = int(input("tolerance radius for comparing cell positions: "))
            break
        except ValueError:
            print("tolerance radius not valid")

    return time_for_adherent, delay, images_threshold, compare_threshold"""


"""def save_params_in_txtfile(txtfile, masks_name, diams_name, time_for_adherent, delay, images_threshold,
                           compare_threshold):
    # save the used masks, diams and parameters in the text file
    txtfile.write("masks={0}, diams={1}, time_for_adherent[s]={2}, delay[s]={3}, images_threshold={4}, \
    tolerance={5}\n".format(masks_name, diams_name, time_for_adherent, delay, images_threshold, compare_threshold))"""


def save_config_in_txtfile(txtfile, masks_name, diams_name, config):
    # save the used masks, diams and parameters in the text file
    txtfile.write("masks: {0}, diams: {1}\n".format(masks_name, diams_name))
    txtfile.write("Cell detection parameters:")
    txtfile.write(str(config["celldet"]))
    txtfile.write("\nAdherent Cell detection parameters:")
    txtfile.write(str(config["adhcelldet"]))
    txtfile.write("\n__________________________________________________________________________________________\n\n")


def save_adh_in_txtfile(txtfile, number_adherent_cells, number_cells_total, adherent_cells, cells,
                        nr_adherent_cells_on_img):
    # save the information found about the adherent cells in the text file
    # number adherent cells
    print("Number adherent cells: ", number_adherent_cells)
    txtfile.write("Number adherent cells: {0}\n".format(number_adherent_cells))

    # number cells total
    print("Number cells total: ", number_cells_total)
    txtfile.write("Number cells total: {0}\n".format(number_cells_total))

    # number generated Cell objects
    cellcounter = 0
    for img_nr in range(len(cells)):
        for cell_nr in range(len(cells[img_nr])):
            cellcounter += 1
    print("Number generated Cell objects: {0}".format(cellcounter))
    txtfile.write("Number generated Cell objects: {0}\n\n".format(cellcounter))

    # number cells on first image
    print("\nNumber cells on first image: {0}".format(len(cells[0])))
    txtfile.write("\n\nNumber cells on first image: {0}".format(len(cells[0])))

    # number adherent cells on each image
    print("\nNumber adherent cells on each image: \n")
    txtfile.write("\n\nNumber adherent cells on each image: \n")
    for i in range(len(nr_adherent_cells_on_img)):
        print("    Image {0}:  {1}".format(i, nr_adherent_cells_on_img[i]))
        txtfile.write("\n    Image {0}:  {1} ".format(i, nr_adherent_cells_on_img[i]))

    # adherent cells
    print("\n\nAdherent cells: \n")
    txtfile.write("\n\nAdherent cells: \n\n")
    for i in range(len(adherent_cells)):
        print("    {0}".format(adherent_cells[i]))
        txtfile.write("    {0}".format(adherent_cells[i].__str__()))
        txtfile.write("\n")

    # number generated AdherentCell objects
    print("\nCreated AdherentCell-objects: ", AdherentCell.get_adherent_cellcounter())
    txtfile.write("\n\nCreated AdherentCell-objects: {0}\n".format(AdherentCell.get_adherent_cellcounter()))

    # Adhesion quotient
    print("\nAdhesion quotient A: ", round(number_adherent_cells / len(cells[0]), 2))
    txtfile.write("\n\nAdhesion quotient A: {0}\n".format(round(number_adherent_cells / len(cells[0]), 2)))

    # Corrected Adhesion quotient
    print("\nCorrected Adhesion quotient A_c = (N_adh - N_adh,first) / N_first: ", round((number_adherent_cells - nr_adherent_cells_on_img[0]) / len(cells[0]), 2))
    txtfile.write("\n\nCorrected Adhesion quotient A_c = (N_adh - N_adh,first) / N_first: {0}\n".format(round((number_adherent_cells - nr_adherent_cells_on_img[0]) / len(cells[0]), 2)))

    print("\n__________________________________________________________________________________________\n\n")
    txtfile.write("\n\n__________________________________________________________________________________________\n\n")


def save_confluence_in_txtfile(txtfile, mask_name, confluence):
    print("Confluence: {0}% \n\n".format(confluence))
    txtfile.write("\n\n\nConfluence (Used background mask: {0}): {1}% \n\n\n".format(mask_name, confluence))


def show_and_save_result_imgs(imgs, path, name):
    # show images and save them in the directory under a given name
    if isinstance(imgs, list):
        for i in range(len(imgs)):
            skimage.io.imshow(imgs[i])
            skimage.io.show()
            filename = name + str(i) + ".jpg"
            skimage.io.imsave(os.path.join(path, filename), skimage.util.img_as_ubyte(imgs[i]))
    else:
        skimage.io.imshow(imgs)
        skimage.io.show()
        filename = name + ".jpg"
        skimage.io.imsave(os.path.join(path, filename), skimage.util.img_as_ubyte(imgs))


def number_adh_on_image_to_csv(nr_adherent_cells_on_img, path):
    # saves the nr_adherent_cells_on_img ('int'-list) in csv file
    with open(path, 'w', newline='') as csv_1:
        csv_out = csv.writer(csv_1)
        csv_out.writerows([nr_adherent_cells_on_img[index]] for index in range(0, len(nr_adherent_cells_on_img)))


def celladhesion_to_csv(path, nr_adherent_cells, nr_on_first, nr_adherent_cells_on_img, confluence=None,
                        nr_adherent_cells_filtered=None, nr_on_first_filtered=None,
                        nr_adherent_cells_on_img_filtered=None):
    with open(path, 'w') as csv_1:
        csv_out = csv.writer(csv_1)

        if confluence is None:
            csv_out.writerow(['Confl', 'adhC', 'Cfirst', 'A', 'A_c'])
            csv_out.writerow([str(100), str(nr_adherent_cells), str(nr_on_first),
                              str(round(nr_adherent_cells / nr_on_first, 2)).replace('.', ','),
                              str(round((nr_adherent_cells - nr_adherent_cells_on_img[0]) / nr_on_first, 2))
                             .replace('.', ',')])
        else:
            csv_out.writerow(['Confl', 'adhC', 'Cfirst', 'A', 'A_c', 'adhC_filter', 'Cfirst_filter',
                              'A_filter', 'A_c_filter'])
            csv_out.writerow([str(confluence).replace('.', ','), str(nr_adherent_cells), str(nr_on_first),
                              str(round(nr_adherent_cells / nr_on_first, 2)).replace('.', ','),
                              str(round((nr_adherent_cells - nr_adherent_cells_on_img[0]) / nr_on_first, 2))
                             .replace('.', ','),
                              str(nr_adherent_cells_filtered), str(nr_on_first_filtered),
                              str(round(nr_adherent_cells_filtered / nr_on_first_filtered, 2)).replace('.', ','),
                              str(round((nr_adherent_cells_filtered - nr_adherent_cells_on_img_filtered[0]) / nr_on_first_filtered, 2))
                             .replace('.', ',')
                              ])
    csv_1.close()


def intensities_to_csv(intensity, path):

    with open(path, 'w') as csv_1:
        csv_out = csv.writer(csv_1)
        # single image, no background mask
        if isinstance(intensity, float):
            csv_out.writerow(['Intensity'])
            csv_out.writerow([str(intensity).replace('.', ',')])
        # single image, background mask
        elif isinstance(intensity, dict):
            csv_out.writerow(['Confluence', 'Intensity Mask', 'Intensity Rest', 'Diff.', 'Diff. Norm.'])
            csv_out.writerow([str(intensity["confluence"]).replace('.', ','),
                              str(intensity["mask"]).replace('.', ','),
                              str(intensity["rest"]).replace('.', ','),
                              str(intensity["mask"] - intensity["rest"]).replace('.', ','),
                              str((intensity["mask"] - intensity["rest"]) / (intensity["mask"] + intensity["rest"])).replace('.', ',')])
        # multiple images
        else:
            # no background mask
            if isinstance(intensity[0], float):
                csv_out.writerow(['Image Nr.', 'Intensity'])
                for i in range(len(intensity)):
                    csv_out.writerow([i, intensity[i]])
                csv_out.writerow([''])
                csv_out.writerow(['Images', 'Intensity Diff.'])
                for i in range(len(intensity) - 1):
                    csv_out.writerow([str(i + 1) + ' - ' + str(i),
                                      intensity[i + 1] - intensity[i]])
            # background mask
            else:
                # create lists for the results (simplify writing to the csv file)
                confluence = list()
                mask = list()
                rest = list()
                diff = list()
                diff_norm = list()

                csv_out.writerow(['Image Nr.', 'Confluence', 'Intensity Mask', 'Intensity Rest', 'Diff.', 'Diff. Norm.'])
                for i in range(len(intensity)):
                    # add results to the lists
                    confluence.append(intensity[i]["confluence"])
                    mask.append(intensity[i]["mask"])
                    rest.append(intensity[i]["rest"])
                    diff.append(mask[i] - rest[i])
                    diff_norm.append((mask[i] - rest[i]) / (mask[i] + rest[i]))
                    csv_out.writerow([i,
                                      str(confluence[i]).replace('.', ','),
                                      str(mask[i]).replace('.', ','),
                                      str(rest[i]).replace('.', ','),
                                      str(diff[i]).replace('.', ','),
                                      str(diff_norm[i]).replace('.', ',')])
                csv_out.writerow([''])
                csv_out.writerow(['Images', 'Intensity Diff.', 'Intensity Diff. Norm.'])
                for i in range(len(intensity) - 1):
                    csv_out.writerow([str(i + 1) + ' - ' + str(i),
                                      str(diff[i + 1] - diff[i]).replace('.', ','),
                                      str(diff_norm[i + 1] - diff_norm[i]).replace('.', ',')])

    csv_1.close()


def boxplot(non_adherent_cells, adherent_cells, path, filename):

    # convert non-adherent cells radius to right format for matplotlib.plot

    # convert adherent_cells to right format for matplotlib.plot
    data_non_adherent = np.empty(len(non_adherent_cells))  # create empty numpy array with size of the number of non-adh cells
    # check if array contains cell objects (otherwise it contains string 'empty' instead of first cell object)
    if not isinstance(type(non_adherent_cells[0]), str):
        for i in range(len(non_adherent_cells)):
            data_non_adherent[i] = non_adherent_cells[i].get_radius()  # get size and add it to data_non_adharent array
    """
    size = 0    # counter for whole number of cells
    for j in range(len(cells)):     # run all images cells[j]
        for i in range(len(cells[j])):      # run all cells cells[j][i] on image j
            size += 1          # increment cell counter
    data_all = np.empty(size)       # create empty numpy array with same size as number of cells

    # add cells to the numpy array:

    # check if array contains cell objects (otherwise it contains string 'empty' instead of first cell object)
    if not isinstance(type(cells[0][0]), str):
        #  if cells array contains cells: iterate all cells in array, get size and safe it to data_all array
        counter = 0
        for j in range(len(cells)):
            for i in range(len(cells[j])):
                data_all[counter] = cells[j][i].get_radius()
                counter += 1
                """

    # convert adherent cells radius to right format for matplotlib.plot
    data_adherent = np.empty(len(adherent_cells))       # create empty numpy array with size of the number of adh cells
    # check if array contains cell objects (otherwise it contains string 'empty' instead of first cell object)
    if not isinstance(type(adherent_cells[0]), str):
        try:
            for i in range(len(adherent_cells)):
                data_adherent[i] = adherent_cells[i].get_radius()   # get size and add it to data_adharent array
        except:
            data_adherent[0] = 0

    # statistic calculations:
    mean_non_adherent = np.mean(data_non_adherent)    # mean value and standard deviation of non-adh cells
    std_dev_non_adherent = np.std(data_non_adherent)
    mean_adherent = np.mean(data_adherent)  # mean value and standard deviation of adherent cells
    std_dev_adherent = np.std(data_adherent)
    t_stat, p_val = ttest_ind(data_non_adherent, data_adherent)  # t-test between the two groups and get p-value p_val

    # Plot the data as boxplot

    data = [data_non_adherent, data_adherent]    # data structure for the plt.boxplot function
    labels = ['Non-adherent', 'Adherent']        # labels for both boxplots

    plt.title('Size distribution')      # title of plot
    plt.boxplot(data, patch_artist=True, labels=labels)     # create the plot
    # add legend that contains the mean values and standard deviations
    plt.legend(["Non-adherent: " + str(np.round(mean_non_adherent, 3)) + u"\u00B1" + str(np.round(std_dev_non_adherent, 3)),
                "Adharent: " + str(np.round(mean_adherent, 3)) + u"\u00B1" + str(np.round(std_dev_adherent, 2))])
    plt.ylabel('Radius [pixels]')       # label the y-axis
    plt.savefig(os.path.join(path, (filename + '.pdf')))            # save the plot at the given path
    plt.show()                          # show the plot

    # print the mean values, standard deviations and p-value
    print('\nSizes: \n')
    print('Non-adherent:  ' + str(np.round(mean_non_adherent, 3)) + u"\u00B1" + str(np.round(std_dev_non_adherent, 3)))
    print('Adherent:  ' + str(np.round(mean_adherent, 3)) + u"\u00B1" + str(np.round(std_dev_adherent, 2)))
    print('p-value:  ' + str(p_val) + '\n\n')

    with open(os.path.join(path, (filename + '.csv')), 'w') as csv_1:
        csv_out = csv.writer(csv_1)
        csv_out.writerow(['radius in [pixels]'])
        csv_out.writerow(['Non-adh cells', 'adh Cells', '', 'mean n-adh', 'stddev n-adh', 'mean adh', 'stddev adh', 'p-val'])
        csv_out.writerow([str(np.round(data_non_adherent[0]).astype(int)).replace('.', ','),  str(np.round(data_adherent[0]).astype(int)).replace('.', ','), ' ', str(mean_non_adherent).replace('.', ','),   str(std_dev_non_adherent).replace('.', ','),   str(mean_adherent).replace('.', ','),   str(std_dev_adherent).replace('.', ','),  str(p_val).replace('.', ',')])

        if len(data_non_adherent) >= len(data_adherent):
            for i in range(1, len(data_non_adherent)):
                try:
                    csv_out.writerow([str(np.round(data_non_adherent[i]).astype(int)).replace('.', ','), str(np.round(data_adherent[i]).astype(int)).replace('.', ',')])
                except:
                    csv_out.writerow([str(np.round(data_non_adherent[i]).astype(int)).replace('.', ',')])
        else:
            for i in range(1, len(data_adherent)):
                try:
                    csv_out.writerow([str(np.round(data_non_adherent[i]).astype(int)).replace('.', ','), str(np.round(data_adherent[i]).astype(int)).replace('.', ',')])
                except:
                    csv_out.writerow(['', str(np.round(data_adherent[i]).astype(int)).replace('.', ',')])

    csv_1.close()







