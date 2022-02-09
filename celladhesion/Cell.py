import os.path
import cellpose.models
import numpy as np
import imagefunctions as imf



class Cell:
    """ Object 'Cell' for each mask returned by 'cellpose' representing one cell """
    __cellcounter = 0   # number of created 'Cell'-objects

    def __init__(self, pos):
        """
        creates Object 'Cell' with given parameters

        :param pos: array
                1-dim array representing pixel positions x and y of cell center: [x, y] (x and y: int)

        """

        self.__position = pos

        Cell.__cellcounter += 1

    def get_position(self):
        return self.__position

    def set_position(self, pos):
        self.__position = pos

    @staticmethod
    def get_cellcounter():
        return Cell.__cellcounter

    def __str__(self):
        return "Pos.: {0}".format(self.__position)


    """
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
    def find_cells(imgs, flow_threshold=0.4, cellprob_threshold=0.0, diameter=None, model_type='cyto', min_size = 15):
        """
        Uses 'cellpose' to find masks on images 'imgs' where each mask represents one cell and returns
        list of 'Cell' objects

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

        :return cells: list
                list containing cell objects for each image: list[img_index][cell_index]
        :return diams: list
                list of cell diameters (float)
        """

        """ cellpose returns 'masks': list of 2D arrays; labelled 
            image, where 0=no masks; 1,2,...=mask labels """

        model = cellpose.models.Cellpose(gpu=False, model_type=model_type)
        masks, flows, styles, diams = model.eval(imgs, diameter=diameter, channels=[0, 0],
                                                 flow_threshold=flow_threshold,
                                                 cellprob_threshold=cellprob_threshold, do_3D=False, min_size=min_size)

        # change data types
        diams = [float(i) for i in diams]
        masks = np.asarray(masks)

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
                cells_on_img.append(Cell(pos))           # add to temporary list for each image
            cells.append(cells_on_img)                      # add to complete cells list

        return cells, diams, masks





    @staticmethod
    def find_cells_test(flow_threshold=0.4, diameter=None, model_type='cyto'):
        """
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
        :return cells: list
                list containing cell objects for each image: list[img_index][cell_index]
        :return diams: list
                list of cell diameters (float)
        :return masks: list of 2D arrays
        labelled image, where 0=no masks; 1,2,...=mask labels
        """

        """ cellpose returns 'masks': list of 2D arrays; labelled 
            image, where 0=no masks; 1,2,...=mask labels """

        masks = imf.load_test_masks()
        diams = imf.load_test_diams()
        diams = [float(i) for i in diams]

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
                    if vap != 0:                            # if mask-pixel, add position to 'y_tot' and 'x_total' , index is mask-label number
                        y_tot[vap] += y
                        x_tot[vap] += x
                        pixel_counter[vap] += 1

            for i in range(1, number_of_cells + 1):         # create position array with center pos for each cell/mask
                pos = np.array([int(round(x_tot[i] / pixel_counter[i])), int(round(y_tot[i] / pixel_counter[i]))])
                cells_on_img.append(Cell(pos))           # add to temporary list for each image
            cells.append(cells_on_img)                      # add to complete cells list

        return cells, diams, masks

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
    def find_cells_from_masks(masks):
        """ Find and create 'Cell'-objects from the given masks
        :param masks: list of 2D arrays
                labelled image, where 0=no masks; 1,2,...=mask labels
        :return cells: list
                list containing cell objects for each image: list[img_index][cell_index]
        """

        cells = list()

        for img_index in range(masks.shape[0]):  # walk through all images in 'masks'
            cells_on_img = list()  # temporary list object for each image
            number_of_cells = masks[img_index].max()  # number of cells (=highest mask label)
            x_tot = np.zeros(number_of_cells + 1)  # arrays to calculate center of cell
            y_tot = np.zeros(number_of_cells + 1)
            pixel_counter = np.zeros(number_of_cells + 1)
            for y in range(masks[img_index].shape[0]):  # walk every pixel
                for x in range(masks[img_index].shape[1]):
                    vap = masks[img_index][y][x]  # value at pixel
                    if vap != 0:  # if mask-pixel, add position to 'y_tot' and 'x_total' , index is mask-label number
                        y_tot[vap] += y
                        x_tot[vap] += x
                        pixel_counter[vap] += 1

            for i in range(1, number_of_cells + 1):  # create position array with center pos for each cell/mask
                pos = np.array([int(round(x_tot[i] / pixel_counter[i])), int(round(y_tot[i] / pixel_counter[i]))])
                cells_on_img.append(Cell(pos))  # add to temporary list for each image
            cells.append(cells_on_img)  # add to complete cells list

        return cells






