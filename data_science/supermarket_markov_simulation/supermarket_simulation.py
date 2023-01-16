"""Markov Chain Monte Carlo Simulation of Supermarket Customer behavior"""
# Imports
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from faker import Faker
import pandas as pd
from config import (
    CUSTOMER_ARRIVAL_RATE,
    SIMULATION_DURATION,
    TRANS_PROB_MATRIX,
)


@dataclass(slots=True)
class Customer:
    """creates a customer object at location "entrance"""

    transition_probs: pd.DataFrame
    customer_id: int = 0
    name: str = "John Doe"
    current_location: str = "entrance"
    previous_location: str = "entrance"

    def __str__(self) -> str:
        """
        overwrites the str dunder function to return Customer information in a neater fashion.
        Use class_instance!r or repr(class_instance) method to get the repr dunder function
        and thus all class attributes including self.transition_probs.
        """
        customer_information = f"""
        Name (id): {self.name:>26} ({self.customer_id})
        Current Location: {self.current_location:>23}
        Previous Location: {self.previous_location:>22}"""
        return customer_information

    def next_location(self) -> None:
        """transitions the customer to the next location"""
        self.previous_location = self.current_location
        self.current_location = np.random.choice(
            a=self.transition_probs.columns.values,
            p=self.transition_probs.loc[self.current_location],
        )

    @property
    def is_active(self) -> bool:
        """Checks whether the customer has reached the checkout, yet"""
        return bool(self.current_location != "checkout")


@dataclass(slots=True)
class Supermarket:
    """manages multiple Customer instances that are currently in the market."""

    customers: list[Customer,...] = field(default_factory=list)
    minutes: int = 0
    last_id: int = 0
    simulation_output: pd.DataFrame = pd.DataFrame(
        columns=["timestamp", "customer_no", "name", "current_location"]
    )

    @property
    def get_time(self) -> str:
        """returns current time in HH:MM format"""
        return f"{int(np.floor(self.minutes/60)):02}:{self.minutes%60:02}"

    def next_minute(self) -> None:
        """propagates each customer to the next state."""
        self.minutes += 1
        for customer in self.customers:
            customer.next_location()

    def add_new_customers(
        self, frequency: tuple[int, int], transition_probs: pd.DataFrame
    ) -> None:
        """
        randomly creates new customers at a given frequency with transition_probs
        transitional probabilities.
        """
        n_customers = np.random.randint(low=frequency[0], high=frequency[1])
        for new_customer_idx in range(n_customers):
            self.customers.append(
                Customer(
                    transition_probs=transition_probs,
                    customer_id=self.last_id + new_customer_idx,
                    name=Faker().name(),
                )
            )
        self.last_id += n_customers
        if n_customers:
            print(f"{n_customers} new customer(s) entered the supermarket!")

    def remove_exiting_customers(self) -> None:
        """removes every customer that is not active anymore."""
        self.customers = [customer for customer in self.customers if customer.is_active]

    def print_customers(self) -> None:
        """prints all customers with the current time and id in CSV format."""
        print(f"At {self.get_time}, the following customers are currently in the supermarket:")
        for idx, customer in enumerate(self.customers):
            print(f"Customer No. {idx+1}", customer)
            new_customer_output = [
                self.get_time,
                customer.customer_id,
                customer.name,
                customer.current_location,
            ]
            self.simulation_output = pd.concat(
                [
                    self.simulation_output,
                    pd.DataFrame(
                        new_customer_output,
                        index=["timestamp", "customer_no", "name", "current_location"],
                    ).T,
                ],
                axis=0,
                ignore_index=True,
            )


def main() -> None:
    """Starts the supermarket simulation and save its output"""
    inst_supermarket = Supermarket()
    for _minute in range(SIMULATION_DURATION):
        inst_supermarket.next_minute()
        inst_supermarket.add_new_customers(
            frequency=CUSTOMER_ARRIVAL_RATE, transition_probs=TRANS_PROB_MATRIX
        )
        inst_supermarket.print_customers()
        inst_supermarket.remove_exiting_customers()
    save_str = f"output/simulation_{SIMULATION_DURATION}mins_{'-'.join(str(CUSTOMER_ARRIVAL_RATE).split('.'))}cpm"
    while Path(save_str + ".csv").is_file():
        save_str += "_new"
    inst_supermarket.simulation_output.to_csv(save_str + ".csv")


if __name__ == "__main__":
    main()
