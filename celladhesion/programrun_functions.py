import imagefunctions as imf
from AdherentCell import AdherentCell
import skimage.io
import os.path
import csv


def get_celldet_params():
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
    return cellprob_threshold, flow_threshold

def get_adhcelldet_parmas(diams):
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
            """compare_threshold = int(input(
                "tolerance radius for comparing cell positions: ".format(
                    min(diams) / 2)))"""
            compare_threshold = int(input("tolerance radius for comparing cell positions: "))
            break
        except ValueError:
            print("tolerance radius not valid")

    return time_for_adherent, delay, images_threshold, compare_threshold

def save_params_in_txtfile(txtfile, masks_name, diams_name, time_for_adherent, delay, images_threshold,
                           compare_threshold):
    # save the used masks, diams and parameters in the text file
    txtfile.write("masks={0}, diams={1}, time_for_adherent[s]={2}, delay[s]={3}, images_threshold={4}, \
    tolerance={5}\n".format(masks_name, diams_name, time_for_adherent, delay, images_threshold, compare_threshold))


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


def save_confluence_in_txtfile(txtfile, cellprob_threshold_layer, flow_threshold_layer, confluence):
    print("confluence: {0}%".format(confluence))
    txtfile.write("\n\n\nConfluence (cpt={0}, ft={1}): {2}%".format(cellprob_threshold_layer, flow_threshold_layer,
                                                                    confluence))

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


