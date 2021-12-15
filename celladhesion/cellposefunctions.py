from cellpose import models
from Cell import Cell
import numpy as np


def find_adherent_cells(cells, diams, threshold_imgs, tolerance):
    """
    Returns number of adherent adherent_cells (adherent_cells that hold their position on at least 'threshold_imgs'
    consecutive images). Position of a cell is compared to the position, where the cell was first detected (rolling
    adherent_cells may not be detected as adherent adherent_cells)

    :param cells: list
                list containing cell objects for each image: list[img_index][cell_index]
    :param diams: list
                list of cell diameters (float)
    :param threshold_imgs: int, >=2
                number of consecutive images (for example threshold_imgs = 3, if cell needs to be in same position on
                three consecutive images)
    :param tolerance: int
                tolerance radius for Cells.compare method

    :return number_adherent_cells: int
                total number of adherent adherent_cells with given parameters
    :return number_cells_total: int
                total number of adherent_cells
    """
    if threshold_imgs < 2:
        print("threshold_imgs has to be greater than or equal to 2")
        return "error", "error"
    elif float(tolerance) > min(diams)/2:
        print("tolerance has to be smaller than estimated cell size")   # prevent overlapping of adherent_cells
        return "error", "error"
    else:
        number_adherent_cells = 0   # complete number of adherent adherent_cells
        number_cells_total = 0      # complete number of adherent_cells

        adherent_cells = list()     # auxiliary variable to prevent multiple counts for one cell

        # iterate every image (ignore last image where no more new adherent adherent_cells can be found)
        for img_number in range(len(cells) - 1):

            # iterate every cell on image 'img_number'
            for cell_number in range(len(cells[img_number])):
                number_consecutive_imgs = 1  # auxiliary variable that represents number of images in which cell keeps its position

                # prevent multiple counts for one cell by checking if it's already in 'adherent_cells'-list
                if not (cells[img_number][cell_number] in adherent_cells):

                    # iterate every image after 'image_number' to find adherent adherent_cells
                    for check_img_number in range(img_number + 1, len(cells)):
                        """Boolean used to make sure no more images are searched for  adherent_cells[img_number][cell_number] if 
                        one image 'check_image_number' doesn't contain an adherent cell"""
                        cell_found = False

                        # iterate every cell on image 'check_img_number'
                        for check_cell_number in range(len(cells[check_img_number])):

                            # compare cell position
                            if cells[img_number][cell_number].compare(cells[check_img_number][check_cell_number],
                                                                      tolerance):
                                """if true, raise 'number_consecutive_imgs' and add cell to 'adherent_cells' 
                                (adherent_cells[check_img_number][check_cell_number] is same cell as the one on 
                                image 'img_number' -> doesn't have to be counted twice)"""
                                number_consecutive_imgs += 1
                                adherent_cells.append(cells[check_img_number][check_cell_number])
                                cell_found = True
                                break
                        if not cell_found:
                            break   # no cell found on image 'check_img_number'
                                    # -> jump to next cell cell[img_number][cell_number]

                # cell is only considered adherent, if it keeps position on at least 'threshold_imgs' images
                if number_consecutive_imgs >= threshold_imgs:
                    number_adherent_cells += 1

        """calculate total number of adherent_cells by counting all cell objects and subtracting the doubled adherent_cells 
        (saved in 'adherent_cells'-list)"""
        for i in range(len(cells)):
            for j in range(len(cells[i])):
                number_cells_total += 1
        number_cells_total -= len(adherent_cells)

        return number_adherent_cells, number_cells_total







