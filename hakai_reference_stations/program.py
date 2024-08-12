import pandas as pd
import click


@click.command()
@click.option("--file", help="Path to the CSV file with the stations", default='stations.csv')
@click.option("--output", help="Output file")
def add_program(file, output):
    df = pd.read_csv(file)
    df_hakai = df[df["organization"] == "HAKAI"]
    oceanography_sites = (
        r"QU\d+|BU\d+|TO\d+A*|SENTRYSHOAL|PRUTH|DAWSONS|D\d+|J\d+|DI\d+|PR\d+|LD\d+|HS\d+|IA\d+|ZS\d+|PN\d+|QS1|OB\d+|"
        +r"JS\d+|J\d+|KN\d+|UBC\d+|FZH\d+|KWY\d+|MEA\d|KC\d+|BRK\d+|BUR\d+|FC\d+|DE\d+|QCS\d+|QSD\d+|HKP\d+|DFO\d+|RVRS\d+|RI\d+|"
        +r"WBCH\d+|KFPS\d+|JSPP"

    )
    watershed_sites = (
        "[\d\s]+OUTLET|[\d\s]+INLET\w+|ECP\d+"
    )
    projects = (
        r"\d+"
    )
    is_hakai_oceanography = df.query("organization == 'HAKAI' and name.str.fullmatch(@oceanography_sites)", engine="python")
    df['program'] = None
    df.loc[is_hakai_oceanography.index,'program'] = 'Oceanography'
    df.loc[df.query('organization == "HAKAI" and name.str.fullmatch(@watershed_sites) or watershid_id.notna() or lake_id.notna()', engine="python").index,'program'] = 'Watershed'
    df.loc[df.query('organization == "HAKAI" and name.str.fullmatch(@projects)', engine="python").index,'program'] = 'Projects'
    df.loc[df.query('organization == "HAKAI" and program.isnull()').index,'program'] = 'Nearshore'

    df.to_csv(output or file, index=False)



if __name__ == "__main__":
    add_program()