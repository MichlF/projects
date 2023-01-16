from pandas import read_csv
from enum import Enum


class Locations(Enum):
    """Encapsulates store location strings"""

    BACKGROUND = "#"
    CHECKOUT = "C"
    CUSTOMER = "K"
    DAIRY = "D"
    DRINKS = "L"
    ENTRANCE = "G"
    EXIT = "E"
    FRUIT = "F"
    SPICES = "S"


# Paths
PATH_SUPERMARKETMAP = "images/supermarket.png"
PATH_TILES = "images/tiles.png"

# Simulation
SIMULATION_DURATION = 20  # Duration of simulation
CUSTOMER_ARRIVAL_RATE = (0, 3)  # min max
TRANS_PROB_MATRIX = read_csv("data/transitional_probabilities.csv").set_index("before")

# Visualization
MARKET = """
####################
##................##
##L..LD..DS..SF..F##
##L..LD..DS..SF..F##
##L..LD..DS..SF..F##
##L..LD..DS..SF..F##
##L..LD..DS..SF..F##
##................##
##...CC..CC..CC...##
##...CC..CC..CC...##
##................##
###E############G###
""".strip()
STORE_LOCATIONS = {
    Locations.CHECKOUT.value: ((4, 15), (8, 9)),
    Locations.DAIRY.value: ((7, 8), (2, 6)),
    Locations.DRINKS.value: ((3, 4), (2, 6)),
    Locations.FRUIT.value: ((15, 16), (2, 6)),
    Locations.EXIT.value: ((11, 12), (2, 6)),
    Locations.ENTRANCE.value: ((16, 16), (11, 11)),
    Locations.SPICES.value: ((11, 12), (2, 6)),
}
TILE_SIZE = 32
UNWALKABLES = ["#"]
