import numpy as np

from Cell import Cell


class AdherentCell(Cell):
    """
    Subclass of Cell with extra attributes 'first_appearance' and 'number_appearances' needed for adherent adherent_cells
    """
    adherent_cellcounter = 0  # number of created 'AdherentCell'- objects

    def __init__(self, pos, radius, first_appearance, number_appearances):
        """

        :param pos: array
                1-dim array representing pixel positions x and y of cell center: [x, y] (x and y: int)
        :param first_appearance: int
                image number of first appearance; e.g. if image with first appearance is first image in the image
                folder, first_appearance will be 0 (image is imgs[0])
        :param number_appearances: int
                number of consecutive images where adherent cell is detected
        """
        super().__init__(pos, radius)
        self.__first_appearance = first_appearance
        self.__number_appearances = number_appearances

        AdherentCell.adherent_cellcounter += 1

    def get_first_appearance(self):
        return self.__first_appearance

    def set_first_appearance(self, first_appearance):
        self.__first_appearance = first_appearance

    def get_number_appearances(self):
        return self.__number_appearances

    def set_number_appearances(self, number_appearances):
        self.__number_appearances = number_appearances

    @staticmethod
    def reset_adherent_cellcounter():
        AdherentCell.adherent_cellcounter = 0

    @staticmethod
    def get_adherent_cellcounter():
        return AdherentCell.adherent_cellcounter

    def __str__(self):
        return "Pos.: {0}, Radius: {1}, Imgnr. first appearance: {2}, Nr. appearances: {3}".format(self.get_position(),
                                                                                                   self.get_radius(),
                                                                                      self.get_first_appearance(),
                                                                                      self.get_number_appearances())

    @staticmethod
    def find_adherent_cells(cells, diams, threshold_imgs, tolerance):
        """
        Returns number of adherent adherent_cells (adherent_cells that hold their position on at least 'threshold_imgs'
        consecutive images). Position of a cell is compared to the position, where the cell was first detected (rolling
        cells may not be detected as adherent cells)

        :param cells: list
                    list containing cell objects for each image: list[img_index][cell_index]
        :param diams: list
                    list of cell diameters (float)
        :param threshold_imgs: int, >=2
                    number of consecutive images (for example threshold_imgs = 3, if cell needs to be in same position
                    on three consecutive images)
        :param tolerance: int
                    tolerance radius for Cells.compare method

        :return number_adherent_cells: int
                    total number of adherent adherent_cells with given parameters
        :return number_cells_total: int
                    total number of adherent_cells
        :return adherent_cells: list
                    list of 'AdherentCell' objects
        """
        if threshold_imgs < 2:
            print("threshold_imgs has to be greater than or equal to 2")
            return "error", "error", "error"
        """elif float(tolerance) > min(diams) / 2:
            print("tolerance has to be smaller than estimated cell size")  # prevent overlapping of adherent_cells
            return "error", "error", "error" """

        AdherentCell.reset_adherent_cellcounter()   # reset adherent_cellcounter every time the method is called
        number_adherent_cells = 0  # complete number of adherent adherent_cells
        number_cells_total = 0  # complete number of adherent_cells

        adherent_cells_doubles = list()  # auxiliary variable to prevent multiple counts for one cell
        adherent_cells = list()          # list with 'AdherentCell'-objects

        # iterate every image (ignore last image where no more new adherent adherent_cells can be found)
        for img_number in range(len(cells) - 1):

            # iterate every cell on image 'img_number'
            for cell_number in range(len(cells[img_number])):
                number_consecutive_imgs = 1  # auxiliary variable that represents number of images in which cell keeps its position

                # prevent multiple counts for one cell by checking if it's already in 'adherent_cells_doubles'-list
                if not (cells[img_number][cell_number] in adherent_cells_doubles):

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
                                """if true, raise 'number_consecutive_imgs' and add cell to 'adherent_cells_doubles' 
                                (adherent_cells[check_img_number][check_cell_number] is same cell as the one on 
                                image 'img_number' -> doesn't have to be counted twice)"""
                                number_consecutive_imgs += 1
                                adherent_cells_doubles.append(cells[check_img_number][check_cell_number])
                                cell_found = True
                                break
                        if not cell_found:
                            break  # no cell found on image 'check_img_number'
                            # -> jump to next cell cell[img_number][cell_number]

                # cell is only considered adherent, if it keeps position on at least 'threshold_imgs' images
                if number_consecutive_imgs >= threshold_imgs:
                    number_adherent_cells += 1
                    adherent_cells.append(AdherentCell(cells[img_number][cell_number].get_position(),
                                                       cells[img_number][cell_number].get_radius(), img_number,
                                                       number_consecutive_imgs))

        """calculate total number of adherent_cells by counting all cell objects and subtracting the doubled 
        adherent_cells (saved in 'adherent_cells_doubles'-list)"""
        for i in range(len(cells)):
            for j in range(len(cells[i])):
                number_cells_total += 1
        number_cells_total -= len(adherent_cells_doubles)

        if not adherent_cells:  # prevent ValueError if 'adherent_cells'-list is empty
            return number_adherent_cells, number_cells_total, ["No adherent cells found"]
        else:
            return number_adherent_cells, number_cells_total, adherent_cells

    @staticmethod
    def find_adherent_cells2(cells, diams, threshold_imgs, tolerance, missing_cell_threshold=0):
        """
        Same as 'AdherentCell.find_adherent_cells', but with an optional parameter 'missing_cell_threshold'.
        Returns number of adherent adherent_cells (adherent_cells that hold their position on at least 'threshold_imgs'
        consecutive images). Position of a cell is compared to the position, where the cell was first detected (rolling
        cells may not be detected as adherent cells)

        :param cells: list
                    list containing cell objects for each image: list[img_index][cell_index]
        :param diams: list
                    list of cell diameters (float)
        :param threshold_imgs: int, >=2
                    number of consecutive images (for example threshold_imgs = 3, if cell needs to be in same position
                    on three consecutive images)
        :param tolerance: int
                    tolerance radius for Cells.compare method
        :param missing_cell_threshold: int
                    if one cell is not found on 'missing_cell_threshold' images, but on enough other consecutive images,
                    the cell will still be detected as adherent

        :return number_adherent_cells: int
                    total number of adherent adherent_cells with given parameters
        :return number_cells_total: int
                    total number of adherent_cells
        :return adherent_cells: list
                    list of 'AdherentCell' objects
        """
        if threshold_imgs < 2:
            print("threshold_imgs has to be greater than or equal to 2")
            return "error", "error", "error"

        AdherentCell.reset_adherent_cellcounter()  # reset adherent_cellcounter every time the method is called
        number_adherent_cells = 0  # complete number of adherent adherent_cells
        number_cells_total = 0  # complete number of adherent_cells

        adherent_cells_doubles = list()  # auxiliary variable to prevent multiple counts for one cell
        adherent_cells = list()  # list with 'AdherentCell'-objects

        # iterate every image (ignore last image where no more new adherent adherent_cells can be found)
        for img_number in range(len(cells) - 1):

            # iterate every cell on image 'img_number'
            for cell_number in range(len(cells[img_number])):
                number_consecutive_imgs = 1  # auxiliary variable that represents number of images in which cell keeps its position

                # prevent multiple counts for one cell by checking if it's already in 'adherent_cells_doubles'-list
                if not (cells[img_number][cell_number] in adherent_cells_doubles):
                    missing_cell_counter = 0

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
                                """if true, raise 'number_consecutive_imgs' and add cell to 'adherent_cells_doubles' 
                                (adherent_cells[check_img_number][check_cell_number] is same cell as the one on 
                                image 'img_number' -> doesn't have to be counted twice)"""
                                number_consecutive_imgs += 1
                                adherent_cells_doubles.append(cells[check_img_number][check_cell_number])
                                cell_found = True
                                break
                        if not cell_found:
                            missing_cell_counter += 1  # no cell found on image 'check_img_number'
                        if missing_cell_counter > missing_cell_threshold:
                            """ jump to next cell cell[img_number][cell_number], if number of images with a missing
                                cell is greater than the missing_cell_threshold """
                            break

                            # cell is only considered adherent, if it keeps position on at least 'threshold_imgs' images
                if number_consecutive_imgs >= threshold_imgs:
                    number_adherent_cells += 1
                    adherent_cells.append(AdherentCell(cells[img_number][cell_number].get_position(), img_number,
                                                       number_consecutive_imgs))

        """calculate total number of adherent_cells by counting all cell objects and subtracting the doubled 
        adherent_cells (saved in 'adherent_cells_doubles'-list)"""
        for i in range(len(cells)):
            for j in range(len(cells[i])):
                number_cells_total += 1
        number_cells_total -= len(adherent_cells_doubles)

        if not adherent_cells:  # prevent ValueError if 'adherent_cells'-list is empty
            return number_adherent_cells, number_cells_total, ["No adherent cells found"]
        else:
            return number_adherent_cells, number_cells_total, adherent_cells

    @staticmethod
    def nr_adherent_cells_on_img(adherent_cells, nr_imgs):
        """
        Returns how many of the 'adherent_cells' are located on which image

        :param adherent_cells: list
                    list of 'AdherentCell' objects
        :param nr_imgs: int
                    total number of images

        :return: nr_adherent_cells_on_img: array
                    1-dim array where each element represents one image. 'int' value of element is the number of
                    adherent cells on the image
        """
        # create 1-dim array where default number of adherent cells on each image is 0
        nr_adherent_cells_on_img = np.zeros((nr_imgs,), dtype=int)

        for cell_number in range(len(adherent_cells)):      # iterate all adherent cells in 'adherent_cells' list
            cell = adherent_cells[cell_number]              # simplify calling the cell
            # iterate 'number_appearances'-attribute of the cell to count the appearances for all images
            for number_appearance in range(cell.get_number_appearances()):
                # raise the adherent cells counter for the respective image
                nr_adherent_cells_on_img[cell.get_first_appearance() + number_appearance] += 1

        return nr_adherent_cells_on_img








