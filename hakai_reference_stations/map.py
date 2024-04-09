from pathlib import Path

import click
import folium
import jinja2
import numpy as np
import pandas as pd
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
        return f"<div style='width:100px;'><strong>{row['name']}</strong><br>Organization: {row['organization']}<br>Work Area: {row['work_area']}</div>"

    # Create a map
    m = folium.Map(location=center, zoom_start=6)

    # Add the stations
    for group_id, df_group in stations.groupby(["organization", "work_area"]):
        color = ORGANIZATION_WORK_AREAS[group_id[0]]["color"]
        logger.debug("Adding group {}", group_id)
        logger.debug("Color: {}", color)
        layer = folium.FeatureGroup(name=f"{group_id[0]}: {group_id[1]}")
        for id,row in df_group.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                popup=_popup(row),
                radius=3,
                color=color,
                stroke=False,
                fill=True,
                fill_opacity=0.5,
                tooltip=row["name"],
            ).add_to(layer)
        layer.add_to(m)
    folium.LayerControl().add_to(m)
    # Render the map
    m.save(output)


@click.command()
@click.option(
    "--stations_csv",
    help="CSV file with the stations",
    default="docs/stations.csv",
    type=click.Path(exists=True),
)
@click.option(
    "--output",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Output file",
    default=Path("."),
)
@click.option(
    "--base_directory",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Base directory for the output files",
    default="docs",
)
def create_base_map(stations_csv: Path, output: Path, base_directory: Path):
    (base_directory / output).mkdir(parents=True, exist_ok=True)
    # Load the stations
    df = pd.read_csv(stations_csv).dropna(subset=["latitude", "longitude"])
    df = df.replace({pd.NA: "", np.NaN: ""})
    # Generate the pages
    (base_directory / output / "index.html").write_text(
        environment.get_template("index.html").render(
            base_directory=base_directory, output=output
        )
    )
    generate_map(df, base_directory / output / "map.html")
    (base_directory / output / "table.html").write_text(
        environment.get_template("table.html").render(
            table_html=df.to_html(
                index=False,
                classes="table table-striped table-hover table-sm",
                escape=False,
                table_id="stations-table",
            ),
            base_directory=base_directory,
            output=output,
        )
    )


if __name__ == "__main__":
    create_base_map()
