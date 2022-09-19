import os.path
import cellpose.models
import numpy as np
import imagefunctions as imf


class Cell:
    """ Object 'Cell' for each mask returned by 'cellpose' representing one cell """
    cellcounter = 0   # number of created 'Cell'-objects

    def __init__(self, pos, radius):
        """
        creates Object 'Cell' with given parameters

        :param pos: array
                1-dim array representing pixel positions x and y of cell center: [x, y] (x and y: int)
        :param radius: int
                radius of the cell

        """

        self.__position = pos
        self.__radius = radius

        Cell.cellcounter += 1

    def get_position(self):
        return self.__position

    def set_position(self, pos):
        self.__position = pos

    def get_radius(self):
        return  self.__radius

    def set_radius(self, radius):
        self.__radius = radius

    @staticmethod
    def reset_cellcounter():
        Cell.cellcounter = 0

    @staticmethod
    def get_cellcounter():
        return Cell.cellcounter

    def __str__(self):
        return "Pos.: {0}, Radius: {1}".format(self.get_position(), self.get_radius())

    @staticmethod
    def calculate_radius(number_pixels):
        # calculates the radius of an approximately round cell with an area of 'number_pixels'
        return int(round(np.sqrt(number_pixels / np.pi)))


    """   OLD VERSION
    @staticmethod

    def find_cells(imgs, flow_threshold=0.4, diameter=None, model_type='cyto'):
        
        Uses 'cellpose' to find masks on images 'imgs' where each mask represents one cell and returns
        list of 'Cell' objects

        :param imgs: list
                containing 'ndarray' of each image
        :param flow_threshold: float (optional, default 0.4)
                flow error threshold (all adherent_cells with errors below threshold are kept)
        :param diameter: float (optional, default None)
                diameter for each image (only used if rescale is None),
                if diameter is None, set to diam_mean
        :param model_type: str (optional, default 'cyto')
                'cyto'=cytoplasm model; 'nuclei'=nucleus model
        :return adherent_cells: list
                list containing cell objects for each image: list[img_index][cell_index]
        


            cellpose returns 'masks': list of 2D arrays; labelled 
            image, where 0=no masks; 1,2,...=mask labels 
        model = cellpose.models.Cellpose(gpu=False, model_type=model_type)
        masks, flows, styles, diams = model.eval(imgs, diameter=None, channels=[0,0],
                                         flow_threshold=0.4, do_3D=False)
        masks = np.asarray(masks)

        adherent_cells = list()

        for img_index in range(masks.shape[0]):             # walk through all images in 'imgs'
            cells_on_img = list()                           # temporary list object for each image
            for cell_index in range(1, masks[img_index].max() + 1):     # iterate through all masks

                x_tot = 0           # counter for pixel x-position to calculate center of cell
                y_tot = 0           # counter for pixel y-position to calculate center of cell
                pixel_counter = 0       # counter for overall pixel number
                for y in range(masks[img_index].shape[0]):   # walk every pixel
                    for x in range(masks[img_index].shape[1]):
                        if masks[img_index][y][x] == cell_index:    # find pixels of each mask 'cell_index'
                            x_tot += x
                            y_tot += y
                            pixel_counter += 1
                x_center = int(round(x_tot / pixel_counter))    # calculate center
                y_center = int(round(y_tot / pixel_counter))
                pos = np.array([x_center, y_center])
                cells_on_img.append(Cell(cell_index, pos))      # initialize Cell object with 'cell_index' and center position 'pos'
            adherent_cells.append(cells_on_img)

        return adherent_cells 
    """


    @staticmethod
    def run_cellpose(imgs, flow_threshold=0.4, cellprob_threshold=0.0, diameter=None, model_type='cyto', min_size=15):
        """ Uses Uses 'cellpose' to find masks on images 'imgs' where each mask represents one cell

        :param imgs: list
                containing 'ndarray' of each image
        :param flow_threshold: float (optional, default 0.4)
                flow error threshold (all adherent_cells with errors below threshold are kept)
        :param cellprob_threshold: float (optional, default 0.0)
                cell probability threshold (all pixels with prob above threshold kept for masks)
        :param diameter: float (optional, default None)
                diameter for each image (only used if rescale is None),
                if diameter is None, set to diam_mean
        :param model_type: str (optional, default 'cyto')
                'cyto'=cytoplasm model; 'nuclei'=nucleus model
        :param min_size: int
                minimum number of pixels per mask, can turn off with -1

        :return masks: list of 2D arrays; labelled
                image, where 0=no masks; 1,2,...=mask labels
        :return diams: list
                list of cell diameters (float)
        """

        model = cellpose.models.Cellpose(gpu=False, model_type=model_type)
        masks, flows, styles, diams = model.eval(imgs, diameter=diameter, channels=[0, 0],
                                                 flow_threshold=flow_threshold,
                                                 cellprob_threshold=cellprob_threshold, do_3D=False, min_size=min_size)
        # change data types
        masks = np.asarray(masks)
        diams = [float(i) for i in diams]

        return masks, diams

    @staticmethod
    def find_cells(masks):
        """
        Creates 'Cell' object for each cellpose mask and returns them as a list item

       :param masks: list of 2D arrays; labelled
                image, where 0=no masks; 1,2,...=mask labels

        :return cells: list
                list containing cell objects for each image: list[img_index][cell_index]
        """

        Cell.reset_cellcounter()  # reset cellcounter every time the method is called
        cells = list()

        for img_index in range(masks.shape[0]):             # walk through all images in 'imgs'
            cells_on_img = list()                           # temporary list object for each image
            number_of_cells = masks[img_index].max()        # number of cells (=highest mask label)
            x_tot = np.zeros(number_of_cells + 1)           # arrays to calculate center of cell
            y_tot = np.zeros(number_of_cells + 1)
            pixel_counter = np.zeros(number_of_cells + 1)
            for y in range(masks[img_index].shape[0]):      # walk every pixel
                for x in range(masks[img_index].shape[1]):
                    vap = masks[img_index][y][x]            # value at pixel

                    # if mask-pixel, add position to 'y_tot' and 'x_total' , index is mask-label number
                    if vap != 0:
                        y_tot[vap] += y
                        x_tot[vap] += x
                        pixel_counter[vap] += 1

            for i in range(1, number_of_cells + 1):         # create position array with center pos for each cell/mask
                pos = np.array([int(round(x_tot[i] / pixel_counter[i])), int(round(y_tot[i] / pixel_counter[i]))])
                radius = Cell.calculate_radius(pixel_counter[i])
                cells_on_img.append(Cell(pos, radius))           # add to temporary list for each image
            cells.append(cells_on_img)                      # add to complete cells list

        return cells

    def compare(self, cell2, tolerance):
        """ Checks if position of two 'Cell'-objects match within given 'tolerance' radius:
            equal if ((x2-x1)^2 + (y2-y1)^2 < tolerance^2)  """
        return (cell2.get_position()[0] - self.get_position()[0]) ** 2 + \
               (cell2.get_position()[1] - self.get_position()[1]) ** 2 <= tolerance ** 2

    @staticmethod
    def safe_masks(masks, path, filename):
        """ Save 'masks' as a '.npy'-file under the name 'filename' at given 'path'
        :param masks: list of 2D arrays
        labelled image, where 0=no masks; 1,2,...=mask labels
        :param path: string
                Format: "...:/.../..."
        :param filename: string
                without '.npy' ending
        """

        masks_array = np.asarray(masks)
        open(os.path.join(path, (filename + '.npy')), 'w+')     # create file
        np.save(os.path.join(path, (filename + '.npy')), masks_array)

    @staticmethod
    def safe_diams(diams, path, filename):
        """ Save 'diams' as a '.txt' file under the name 'filename' at given 'path'
        :param diams: list
                list of cell diameters (float)
        :param path: string
                Format: "...:/.../..."
        :param filename: string
                without '.txt' ending
        """

        txtfile = open(os.path.join(path, (filename + '.txt')), 'w+')
        txtfile.write("\n".join(str(item) for item in diams))

    @staticmethod
    def determine_confluence(mask):
        """
        Determines the confluence (percentage of the surface of a culture dish that is covered by adherent cells) of the
        cells, represented by the mask

        :param mask: 2D array; labelled
                image, where 0=no masks; 1,2,...=mask labels

        :return confluence: int
                confluence of cells on img, given in percent
        """

        pixels = 0              # total number of pixels
        pixels_cells = 0        # number of pixels belonging to a cell (mask)

        for y in range(mask.shape[0]):          # iterate whole image
            for x in range(mask.shape[1]):
                pixels += 1                     # count pixels
                if mask[y][x] != 0:             # if mask pixel, increase pixel_cells counter
                    pixels_cells += 1
        confluence = round((pixels_cells / pixels) * 100)   # calculate confluence

        return confluence

    @staticmethod
    def filter_for_position(cells, background_mask):
        """
        Filters an given 'cells' list, so that only those cells that have the same position as the cells on an
        'background_mask' will remain. Use this function to consider cell adhesion only for those cells, that have a
        certain position, determined by the background mask.

        :param cells: list
                list containing cell objects: list[cell_index]
        :param background_mask: 2D array; labelled
                image, where 0=no masks; 1,2,...=mask labels
        :return: filtered_cells: list
                list containing only the cells whose position matches the background mask

        """

        filtered_cells = list()     # new list for the results

        for cell_nr in range(len(cells)):       # iterate all cells
            cell = cells[cell_nr]               # simplify cell call
            # check if the center of the cell already matches the background mask
            if background_mask[cell.get_position()[1]][cell.get_position()[0]] != 0:
                filtered_cells.append(cells[cell_nr])       # if yes, add the cell to the result list
            else:
                radius = cell.get_radius()      # simplify radius call
                match_found = False             # used to make sure, each cell is added to 'filtered_cells' only once
                # iterate over all pixels in a square around the cell (side length: 2 * cell_radius)
                for y in range(cell.get_position()[1] - radius, cell.get_position()[1] + radius):
                    for x in range(cell.get_position()[0] - radius, cell.get_position()[0] + radius):
                        # prevent adding cell to 'filtered_cells' more than once
                        if not match_found:
                            # only check pixels of the actual cell (approx. circle with radius  of the cell)
                            if (y - cell.get_position()[1]) ** 2 + (x - cell.get_position()[0]) ** 2 <= radius:
                                # make sure the pixel is part of the background img (relevant for cells on edges of the img)
                                if (0 <= y < background_mask.shape[0]) and (0 <= x < background_mask.shape[1]):
                                    # if the position of the pixel matches a mask pixel, add the cell to list
                                    if background_mask[y][x] != 0:
                                        match_found = True
                                        filtered_cells.append(cells[cell_nr])

        return filtered_cells















