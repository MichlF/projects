from dataclasses import dataclass, field
import numpy as np
import cv2
from supermarket_simulation import Supermarket
from create_supermarket_map import main as create_supermarket_map
from path_finder import main as run_pathfinder
from config import (
    CUSTOMER_ARRIVAL_RATE,
    Locations,
    MARKET,
    PATH_SUPERMARKETMAP,
    PATH_TILES,
    SIMULATION_DURATION,
    STORE_LOCATIONS,
    TILE_SIZE,
    TRANS_PROB_MATRIX,
    UNWALKABLES,
)


@dataclass
class VisualizeCustomers(Supermarket):
    """Draws and navigates the avatar of the customer on the map"""

    avatar: np.ndarray = np.full(shape=(32, 32, 3), fill_value=255)
    store_locations: dict = field(default_factory=dict)

    def find_path(
        self,
        grid: str | list[list[str, ...]] = MARKET,
        unwalkables: list[str, ...] = field(default_factory=list),
        start_name: str = "entrance",
        end_name: str = "exit",
        is_efficient: bool = True,
    ) -> list[tuple[int, int], ...]:
        """Returns a path object with x,y coordinates for each move to the target"""
        #! We might not actually need this and can call run_pathfinder directly instead...
        all_members = [member for member in dir(Locations) if not member.startswith("_")]
        if not all(loc_name in all_members for loc_name in [start_name.upper(), end_name.upper()]):
            raise ValueError("Either start or end name is unknown!")

        return run_pathfinder(
            grid=grid,
            unwalkables=unwalkables,
            start_symbol=Locations.__members__[start_name.upper()].value,
            end_symbol=Locations.__members__[end_name.upper()].value,
            store_locations=self.store_locations,
            is_efficient=is_efficient,
        )

    def draw_background(self, background: np.ndarray, supermarket_map: np.ndarray) -> np.ndarray:
        """Draws base image (supermarket map) onto frame"""
        frame = background.copy()
        try:
            supermarket_map.draw(frame)
        except AttributeError:
            frame[0 : supermarket_map.shape[0], 0 : supermarket_map.shape[1]] = supermarket_map

        return frame

    def draw_move(self, frame: np.array, location: tuple[int, int]) -> None:
        """Draws a customer avatar on the frame"""
        x_coord = location[1] * TILE_SIZE
        y_coord = location[0] * TILE_SIZE
        frame[
            y_coord : y_coord + self.avatar.shape[0], x_coord : x_coord + self.avatar.shape[1]
        ] = self.avatar


def main() -> None:
    supermarket_map = create_supermarket_map(path_map=PATH_SUPERMARKETMAP, path_tile=PATH_TILES)
    background = np.zeros(np.shape(supermarket_map), np.uint8)
    tiles = cv2.imread(PATH_TILES)
    customer_avatar = (4 * TILE_SIZE, 0 * TILE_SIZE)
    customer_avatar = tiles[
        customer_avatar[0] : customer_avatar[0] + TILE_SIZE,
        customer_avatar[1] : customer_avatar[1] + TILE_SIZE,
        :,
    ]
    inst_viz_customers = VisualizeCustomers(
        store_locations=STORE_LOCATIONS, avatar=customer_avatar
    )
    # Start simulation
    for _minute in range(SIMULATION_DURATION):
        frame = inst_viz_customers.draw_background(
            background=background, supermarket_map=supermarket_map
        )
        inst_viz_customers.next_minute()
        inst_viz_customers.add_new_customers(
            frequency=CUSTOMER_ARRIVAL_RATE, transition_probs=TRANS_PROB_MATRIX
        )
        # For each customer, get target location, find the path and draw to target location
        for customer in inst_viz_customers.customers:
            path = inst_viz_customers.find_path(
                unwalkables=UNWALKABLES,
                start_name=customer.previous_location,
                end_name=customer.current_location,
                is_efficient=False,
            )
            inst_viz_customers.draw_move(frame=frame, location=path[-1])
        inst_viz_customers.print_customers()
        # Show frame with dynamically title, that updates simulation on SPACEBAR and aborts on q
        while True:
            cv2.imshow("frame", frame)
            cv2.setWindowTitle(
                "frame", f"My simulated supermarket after {inst_viz_customers.get_time} (HH:MM)!"
            )
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == " ":  # Spacebar
                cv2.imwrite(f"images/animation/{_minute:02}min.png", frame)
                break
            if key == "q":
                cv2.destroyAllWindows()
                raise KeyError("You have stopped the simulation!")
        inst_viz_customers.remove_exiting_customers()


if __name__ == "__main__":
    main()
