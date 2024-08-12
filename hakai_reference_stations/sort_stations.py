import pandas as pd
import click
from loguru import logger


@click.command()
@click.option("--file", help="Path to the CSV file with the stations", default='stations.csv')
@click.option("--output", help="Output file")
def main(file='station.csv',output=None):
    """Sort the stations by organization, work_area, and name.

    Args:
        file (str): Path to the CSV file with the stations.
        output (str, optional): Path to the output file. Defaults to file.
    """
    stations = pd.read_csv(file)
    sorted_stations = stations.sort_values(by=["organization", "work_area", "name"])
    sorted_stations.to_csv(output or file, index=False)


if __name__ == "__main__":
    main()