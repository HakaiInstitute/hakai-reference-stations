from pathlib import Path

import click
import pandas as pd
from hakai_api import Client
from loguru import logger

STATIONS_ENDPOINT = "eims/views/output/sites"
ORGANIZATION_WORK_AREAS = {
    "HAKAI": {
        "label": "Hakai Institute",
        "color": "red",
        "work_areas": ["CALVERT", "QUADRA", "JOHNSTONE STRAIT", "LOWER MAINLAND"],
    },
    "SFC": {
        "label": "Skeena Fisheries Commission",
        "color": "orange",
        "work_areas": ["SKEENA"],
    },
    "PARKS CANADA": {
        "label": "Parks Canada",
        "color": "green",
        "work_areas": ["GWAII HAANAS"],
    },
    "NATURE TRUST": {
        "label": "Nature Trust",
        "color": "blue",
        "work_areas": ["ESTUARY"],
    },
    "UWT": {
        "label": "University of Washington",
        "color": "purple",
        "work_areas": ["CLAYOQUOT"],
    },
}
work_areas_to_organization = {
    work_area: organization
    for organization, work_areas in ORGANIZATION_WORK_AREAS.items()
    for work_area in work_areas["work_areas"]
}

COLUMNS = [
    "organization",
    "work_area",
    "name",
    "latitude",
    "longitude",
    "depth",
    "depth_source",
    "watershid_id",
    "lake_id",
]
SORT_BY = ["organization", "work_area", "name"]


@click.command()
@click.option("--api_root", help="Root URL of the API")
@click.option("--credentials", help="API token credentials")
@click.option("--output", default="docs/stations.csv", help="Output file")
def get_stations_from_database(api_root, credentials, output):
    # Initialize the client
    client = Client(credentials=credentials)

    # Get all the reference stations
    url = f"{api_root or client.api_root}/{STATIONS_ENDPOINT}?limit=-1"
    logger.info(f"Getting stations from {url}")
    response = client.get(url)
    response.raise_for_status()

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(response.json())
    df["organization"] = df["work_area"].map(work_areas_to_organization)
    if df["organization"].isnull().any():
        logger.warning(
            f"Some work areas don't have a corresponding organization: {df['work_area'][df['organization'].isnull()]}"
        )
    df[COLUMNS].sort_values(SORT_BY).to_csv(output, index=False)


if __name__ == "__main__":
    get_stations_from_database()
