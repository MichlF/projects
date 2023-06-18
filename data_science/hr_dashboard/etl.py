import datetime as dt
from typing import Union

import pandas as pd


def get_distribution(
    data: pd.DataFrame, column_name: str, decimals: int
) -> pd.DataFrame:
    distribution = (
        data[column_name].value_counts(normalize=True).mul(100).round(decimals)
    )
    dist_df = pd.DataFrame(distribution)
    dist_df.columns = ["Percentage"]

    return dist_df


def get_signups(
    data: pd.DataFrame,
    date_column: str,
    start: Union[str, dt.datetime, None] = None,
    end: Union[str, dt.datetime, None] = None,
) -> pd.DataFrame:
    data = data.copy()
    data[date_column] = pd.to_datetime(data[date_column])
    data.set_index(date_column, inplace=True)

    # Filter data based on start and end dates
    if isinstance(start, str):
        start = pd.to_datetime(start)
    if isinstance(end, str):
        end = pd.to_datetime(end)
    if start is not None:
        data = data.loc[data.index >= start]
    if end is not None:
        data = data.loc[data.index <= end]

    # Resample the dataframe by month and calculate cumulative sum
    monthly_accumulated = data.resample("M").size().cumsum()

    # Create a new pandas DataFrame with the cumulative sum and monthly datetime index
    monthly_df = pd.DataFrame(monthly_accumulated.values, columns=["Acc. Count"])
    monthly_df.index = monthly_accumulated.index.to_period("M").to_timestamp()

    return monthly_df


def get_agg_distribution(
    data, group_column_name: str, agg_column_name: str
) -> pd.DataFrame:
    # group and agg column cannot be the same and agg column has to be numerical
    data = data.copy()

    if group_column_name == "Age":
        age_bins = [0, 18, 29, 39, 49, 59, 69, 79, float("inf")]
        age_labels = [
            "0-18",
            "18-29",
            "30-39",
            "40-49",
            "50-59",
            "60-69",
            "70-79",
            "80+",
        ]
        data["Age"] = pd.cut(data["Age"], bins=age_bins, labels=age_labels, right=False)

    return data.groupby(group_column_name)[agg_column_name].mean()


def search(
    data: pd.DataFrame, column: Union[str, None], search_term: str
) -> pd.DataFrame:
    if column in ["Age", "Salary"]:
        search_term = int(search_term)  # type: ignore

    if column not in data.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    filtered_data = data[data[column] == search_term]

    return filtered_data


if __name__ == "__main__":
    # For local testing
    data = pd.read_csv("data/data.csv")

    gender_distribution = get_distribution(data, "Gender", 2)
    age_distribution = get_distribution(data, "Age", 2)
    salaries_by_age = get_agg_distribution(data, "Age", "Salary")
    salaries_by_profession = get_agg_distribution(data, "Profession", "Salary")
    accumulated_signups = get_signups(
        data, "Onboarding Date", dt.datetime(2020, 1, 1), dt.datetime(2022, 1, 1)
    )
    search_result = search(data, "Onboarding Date", "2022-11-20")
    search_result = search(data, "Onboarding Date", "2022-11-20")
