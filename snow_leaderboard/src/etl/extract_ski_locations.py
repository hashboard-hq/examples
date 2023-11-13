import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb
import pandas as pd
from prefect import flow, get_run_logger, task

from etl.constants import STATES
from etl.download import download_file_from_url
from etl.paths import (
    get_bucket_and_key_for_location_data,
    get_local_dir_for_location_data,
    s3_uri,
)
from etl.upload import upload_file_to_s3


@task(retries=1)
def download_and_extract_file() -> Path:
    """
    Downloads an archive from NOAA and extracts a single shapefile with all
    ski locations; returns the path to the extracted file.
    """
    url = "https://www.nohrsc.noaa.gov/data/vector/master/ski_areas_all.tar.gz"
    directory = get_local_dir_for_location_data()
    shp_file = "ski_areas_all.shp"
    with TemporaryDirectory() as tmp:
        p = download_file_from_url(url, Path(tmp))
        with tarfile.open(p) as archive:
            archive.extractall(directory)
    return directory / shp_file


@task
def convert_shp_file_to_parquet(shp_file: Path) -> Path:
    """
    Opens the shp file with duckdb and saves the relevant info to a new parquet
    file.
    """
    states_df = pd.DataFrame.from_records(STATES)
    states_df.columns = ("state_name", "state_code")  # type: ignore

    conn = duckdb.connect()
    conn.execute("install spatial; load spatial;")
    # there are a small number (~4) of duplicate resorts with slightly different
    # coordinates; we filter out the bad ones and average the others
    cur = conn.sql(
        f"""
        select distinct
            md5(ski_areas.name || '-' || ski_areas.state) as id,
            ski_areas.name || ' (' || states_df.state_code || ')' as "NAME",
            ski_areas.state,
            avg(ski_areas.lat) over (partition by id) as lat,
            avg(ski_areas.long) over (partition by id) as long
        from st_read('{shp_file}') as ski_areas
        join states_df on ski_areas.state = states_df.state_name
        where
            ski_areas.type in ('Alpine', 'Both')
            and not (
                ski_areas.name = 'Mount High East Ski Area'
                and ski_areas.long = -117.43
            )
            and not (
                ski_areas.name = 'Mount High West Ski Area'
                and ski_areas.long = -117.74
            )
            and not (
                ski_areas.name = 'Sky Tavern Ski Area'
                and ski_areas.long = -119.90
            )
            and not (
                ski_areas.name = 'Angel Fire Ski Area'
                and ski_areas.long = -105.27
            )
        order by ski_areas.state asc, ski_areas.name asc
    """
    )
    p = shp_file.with_suffix(".parquet")
    cur.write_parquet(str(p), compression="snappy")
    return p


@task(retries=1)
def upload_parquet_to_s3(pq_file: Path) -> str:
    """
    Returns key of s3 object.
    """
    bucket, key = get_bucket_and_key_for_location_data()
    upload_file_to_s3(pq_file, bucket, key)
    return s3_uri(bucket, key)


@flow
def create_ski_locations_dataset() -> None:
    """
    Downloads a shapefile of ski locations and writes the data to a parquet file
    locally and on S3.
    """
    logger = get_run_logger()
    shp_file = download_and_extract_file()
    assert shp_file is not None
    pq_file = convert_shp_file_to_parquet(shp_file=shp_file)
    s3_uri = upload_parquet_to_s3(pq_file=pq_file)
    logger.info("Created ski resort parquet file at %s", s3_uri)


if __name__ == "__main__":
    create_ski_locations_dataset()
