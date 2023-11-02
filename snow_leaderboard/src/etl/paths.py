import os
from datetime import date
from pathlib import Path
from typing import Literal

DATA_DIR = Path(__file__).parent.parent.parent / "data"

LOCATIONS = "ski_locations"
SNOWFALL = "snowfall"

TIFFS = "raw"

DAILY_PQ = "daily_pq"
SEASON_PQ = "season_pq"


def get_bucket() -> str:
    if not (bucket := os.getenv("S3_BUCKET")):
        raise ValueError("Must set the S3_BUCKET env var.")
    return bucket


# ski locations
def get_local_dir_for_location_data() -> Path:
    return DATA_DIR / LOCATIONS


def get_bucket_and_key_for_location_data() -> tuple[str, str]:
    key = f"{LOCATIONS}/ski_areas_all.parquet"
    return get_bucket(), key


# snowfall data
def get_season_of_partition(partition: date) -> int:
    return partition.year if partition.month >= 10 else partition.year - 1


def get_tiff_filenames_for_partition(
    partition: date, utc_time: Literal["00", "12"] = "12"
) -> tuple[str, str]:
    day_prefix = "sfav2_CONUS_24h_"
    season = get_season_of_partition(partition=partition)
    season_prefix = f"sfav2_CONUS_{season}0930{utc_time}_to_"
    date_str = partition.strftime("%Y%m%d")  # 20231030

    daily_fn = f"{day_prefix}{date_str}{utc_time}.tif"
    season_fn = f"{season_prefix}{date_str}{utc_time}.tif"
    return daily_fn, season_fn


def get_local_dir_for_tiffs() -> Path:
    return DATA_DIR / SNOWFALL / TIFFS


def get_bucket_and_key_for_tiffs() -> tuple[str, str]:
    key = f"{SNOWFALL}/{TIFFS}"
    return get_bucket(), key


def get_local_path_for_daily_pq(partition: date) -> Path:
    filename = f"{partition.strftime('%Y%m%d')}.parquet"
    return (
        DATA_DIR
        / SNOWFALL
        / DAILY_PQ
        / f"{get_season_of_partition(partition)}"
        / filename
    )


def get_bucket_and_key_for_daily_pq_season_dir(
    *, partition: date | None = None, season: int | None = None
) -> tuple[str, str]:
    if partition is None and season is None:
        raise TypeError("Must set either partition or season")
    elif partition is not None and season is not None:
        raise TypeError("Must set only one of partition or season")
    key = season or get_season_of_partition(partition=partition)  # type: ignore
    return get_bucket(), f"{SNOWFALL}/{DAILY_PQ}/{key}"


def get_bucket_and_key_for_daily_pq(partition: date) -> tuple[str, str]:
    filename = f"{partition.strftime('%Y%m%d')}.parquet"
    bucket, season_dir = get_bucket_and_key_for_daily_pq_season_dir(partition=partition)
    return (
        bucket,
        f"{season_dir}/{filename}",
    )


def get_bucket_and_key_for_season_pq(season: int) -> tuple[str, str]:
    return get_bucket(), f"{SNOWFALL}/{SEASON_PQ}/{season}.parquet"
