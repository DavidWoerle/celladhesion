"""Configuration file for the needed parameters"""

# cell detection parameters for 'cellpose' functions
celldet = {
    "cellprob_threshold": 0.0,  # float: (between 0.0 and 1.0, higher: less masks will be found)
    "flow_threshold": 0.4,      # float: (between 0.0 and 1.0, lower: less masks will be found)
}

# adherent cell detection parameters
adhcelldet = {
    "time_for_adherent[s]": 60,    # int or float: time [s] to be detected as adherent
    "delay[s]": 30,                # int or float: delay [s] between images
    "images_threshold": 3,
    "tolerance": 10             # int: tolerance radius for comparing cell positions (pixels)
}