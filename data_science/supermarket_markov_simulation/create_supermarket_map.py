from dataclasses import dataclass
from pathlib import Path
import numpy as np
import cv2
from config import Locations, TILE_SIZE


@dataclass
class SupermarketMap:
    """
    Draws and maintaines the supermarket background map
    """

    layout: str  # a string with each character representing a tile
    tiles: np.ndarray  # contains all tile images

    def __post_init__(self):
        # split the layout string into a two dimensional matrix
        self.contents = [list(row) for row in self.layout.split("\n")]
        self.ncols = len(self.contents[0])
        self.nrows = len(self.contents)
        self.image = np.zeros((self.nrows * TILE_SIZE, self.ncols * TILE_SIZE, 3), dtype=np.uint8)
        self.prepare_map()

    def prepare_map(self):
        """prepares the entire image as a big numpy array"""
        for row, line in enumerate(self.contents):
            for col, char in enumerate(line):
                bm = self.get_tile(char=char)
                y_coord = row * TILE_SIZE
                x_coord = col * TILE_SIZE
                self.image[y_coord : y_coord + TILE_SIZE, x_coord : x_coord + TILE_SIZE] = bm

    def get_tile(self, char):
        """returns the array for a given tile character"""
        if char == Locations.BACKGROUND.value:
            tile_coords = (1, 2)
        elif char == Locations.ENTRANCE.value:
            tile_coords = (7, 3)
        elif char == Locations.CHECKOUT.value:
            tile_coords = (2, 8)
        elif char == Locations.CUSTOMER.value:
            tile_coords = (7, 0)
        elif char == Locations.EXIT.value:
            tile_coords = (6, 10)
        elif char == Locations.DAIRY.value:
            tile_coords = (2, 6)
        elif char == Locations.SPICES.value:
            tile_coords = (0, 3)
        elif char == Locations.FRUIT.value:
            tile_coords = (0, 4)
        elif char == Locations.DRINKS.value:
            tile_coords = (3, 13)
        else:  # Floor
            tile_coords = (2, 1)

        return self.extract_tile(row=tile_coords[0], col=tile_coords[1])

    def extract_tile(self, row, col):
        """extract a tile array from the tiles image"""
        y_coord = row * TILE_SIZE
        x_coord = col * TILE_SIZE
        return self.tiles[y_coord : y_coord + TILE_SIZE, x_coord : x_coord + TILE_SIZE]

    def draw(self, frame):
        """draws the image into a frame"""
        frame[0 : self.image.shape[0], 0 : self.image.shape[1]] = self.image

    def write_image(self, filename):
        """writes the image into a file"""
        cv2.imwrite(filename=filename, img=self.image)


def main(path_map: str, path_tile: str) -> np.ndarray:
    """creates a basic supermarket map as background"""
    if not Path(path_map).is_file():
        background = np.zeros((500, 700, 3), np.uint8)
        tiles = cv2.imread(path_tile)
        market = SupermarketMap(layout=MARKET, tiles=tiles)
        while True:
            bg_frame = background.copy()
            market.draw(frame=bg_frame)
            # Lookup DEC keys in https://www.ascii-code.com/
            key = cv2.waitKey(1)
            if key == 113:  # 'q' key
                break
            cv2.imshow("frame", bg_frame)
        cv2.destroyAllWindows()
        market.write_image(path_map)
        market_map = market.image
    else:
        print("Supermarket Map is already created, returning the one at path_map...")
        market_map = cv2.imread(path_map)
    return market_map


if __name__ == "__main__":
    main()
