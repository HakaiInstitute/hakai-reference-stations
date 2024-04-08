from pathlib import Path

import click
import folium
import jinja2
import pandas as pd
from folium.plugins import FastMarkerCluster
from loguru import logger

from hakai_reference_stations.load_from_database import ORGANIZATION_WORK_AREAS

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader("hakai_reference_stations/templates")
)

marker_callback = """\
function (row) {
    var icon, marker;
    icon = L.AwesomeMarkers.icon({
        icon: "map-marker", markerColor: row[2]});
    marker = L.marker(new L.LatLng(row[0], row[1]));
    marker.setIcon(icon);
    marker.bindPopup("Station: " + row[3]);
    return marker;
};
"""


def generate_map(stations, output, center=[49.5, -125], zoom_level=6):
    def _popup(row):
        return f"{row['organization']}<br>Work Area: {row['work_area']}<br>Station: {row['name']}"

    # Create a map
    m = folium.Map(location=center, zoom_start=6)

    # Add the stations
    for group_id, df_group in stations.groupby(["organization", "work_area"]):
        color = ORGANIZATION_WORK_AREAS[group_id[0]]["color"]
        logger.debug("Adding group {}", group_id)
        logger.debug("Color: {}", color)
        FastMarkerCluster(
            data=df_group.assign(color=color)[
                ["latitude", "longitude", "color", "name"]
            ].values.tolist(),
            popups=df_group.apply(_popup, axis=1).values.tolist(),
            name=f"{group_id[0]}: {group_id[1]}",
            overlay=True,
            control=True,
            callback=marker_callback,
        ).add_to(m)
    folium.LayerControl().add_to(m)
    # Render the map
    m.save(output)


@click.command()
@click.option(
    "--stations_csv", help="CSV file with the stations", default="docs/stations.csv"
)
@click.option("--output", help="Output file", default="docs/index.html")
def create_base_map(stations_csv="output/stations.csv", output="docs/map.html"):
    # Load the stations
    df = pd.read_csv(stations_csv).dropna(subset=["latitude", "longitude"])

    # Generate the map
    generate_map(df, output)


if __name__ == "__main__":
    create_base_map()
