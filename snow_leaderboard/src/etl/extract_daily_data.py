from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import duckdb
import pandas as pd
import rasterio  # type: ignore
from prefect import flow, get_run_logger, task
from requests import HTTPError

from etl.download import download_file_from_url
from etl.paths import (
    get_bucket_and_key_for_daily_pq,
    get_bucket_and_key_for_location_data,
    get_bucket_and_key_for_tiffs,
    get_local_dir_for_tiffs,
    get_local_path_for_daily_pq,
    get_tiff_filenames_for_partition,
    s3_uri,
)
from etl.upload import upload_file_to_s3

if TYPE_CHECKING:
    from prefect.futures import PrefectFuture


@task
def download_tif(url: str) -> Path:
    tiffs_dir = get_local_dir_for_tiffs()
    tiffs_dir.mkdir(parents=True, exist_ok=True)
    p = download_file_from_url(url, tiffs_dir)
    return p


@task
def upload_file(path: Path, bucket: str, key: str) -> None:
    upload_file_to_s3(path, bucket, key)


@flow
def upload_tiffs_to_s3(local_paths: tuple[Path, Path]) -> tuple[str, str]:
    bucket, key = get_bucket_and_key_for_tiffs()
    daily_key = f"{key}/daily/{local_paths[0].name}"
    seasonal_key = f"{key}/seasonal/{local_paths[1].name}"
    upload_file.submit(local_paths[0], bucket, daily_key)
    upload_file.submit(local_paths[1], bucket, seasonal_key)
    return daily_key, seasonal_key


@flow
def download_daily_tiffs(partition: date) -> tuple[Path | HTTPError, Path | HTTPError]:
    # url components
    BASE_URL = "https://www.nohrsc.noaa.gov/snowfall_v2/data/"
    year_and_month = f"{partition.year}{partition.month:02}/"
    daily_filename, season_filename = get_tiff_filenames_for_partition(
        partition, utc_time="12"
    )

    daily_url = f"{BASE_URL}{year_and_month}{daily_filename}"
    season_url = f"{BASE_URL}{year_and_month}{season_filename}"
    futures: list[PrefectFuture] = []
    for url in [daily_url, season_url]:
        futures.append(download_tif.submit(url))
    return tuple(f.result(raise_on_failure=False) for f in futures)  # type: ignore


@task
def transform_tiffs_to_df(partition: date, tiffs: tuple[Path, Path]) -> pd.DataFrame:
    assert len(tiffs) == 2

    # First, query our locations dataset to build a list of
    # coordinates that we would like snowfall data for.
    loc_bucket, loc_key = get_bucket_and_key_for_location_data()
    loc_uri = s3_uri(loc_bucket, loc_key)
    conn = duckdb.connect()
    conn.execute("install httpfs; load httpfs; install aws; load aws;")
    conn.execute("call load_aws_credentials();")
    locations: list[tuple[str, float, float]] = conn.sql(
        f"select id, lat, long from '{loc_uri}'"
    ).fetchall()
    coords = [(location[2], location[1]) for location in locations]

    # Next, use rasterio to extract data for each coordinate
    with (
        rasterio.open(tiffs[0]) as daily_dataset,
        rasterio.open(tiffs[1]) as ytd_dataset,
    ):
        data = {
            "id": [location[0] for location in locations],
            "observed_at": [partition] * len(locations),
            "snowfall_24h": [arr[0] for arr in daily_dataset.sample(coords)],
            "snowfall_ytd": [arr[0] for arr in ytd_dataset.sample(coords)],
        }

    df = pd.DataFrame(data)
    return df


@task
def write_df_to_parquet(partition: date, df: pd.DataFrame) -> Path:
    p = get_local_path_for_daily_pq(partition=partition)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p)
    return p


@flow
def upload_parquet_to_s3(partition: date, local_path: Path) -> str:
    bucket, key = get_bucket_and_key_for_daily_pq(partition=partition)
    upload_file.submit(local_path, bucket, key)
    return s3_uri(bucket, key)


@flow
def create_daily_dataset(partition: date) -> None:
    logger = get_run_logger()
    logger.info("Creating dataset for %s", partition.isoformat())

    # Retrieve and back up raw data
    tiffs = download_daily_tiffs(partition=partition)
    assert tiffs is not None
    if any(isinstance(result, HTTPError) for result in tiffs):
        # we tolerate errors here so jobs that include the current
        # day can fail gracefully if the data isn't yet available;
        # that way we don't exit the flow with a failure, which could
        # prevent downstream flows (like concatenating and loading data)
        # from running.
        logger.error("GeoTiffs unavailable for %s", partition)
        return

    s3_keys = upload_tiffs_to_s3(tiffs)
    logger.info("Uploaded tiffs to s3 at %s", s3_keys)

    df = transform_tiffs_to_df(partition=partition, tiffs=tiffs)
    logger.info("Created df with shape %s", df.shape)

    parquet_file = write_df_to_parquet(partition=partition, df=df)
    logger.info("Saved DF to %s", parquet_file)

    s3_uri = upload_parquet_to_s3(partition=partition, local_path=parquet_file)
    logger.info(f"Uploaded file to s3: {s3_uri}")
