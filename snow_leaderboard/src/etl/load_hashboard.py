import subprocess
import tempfile
from pathlib import Path

from prefect import flow, get_run_logger
from ruamel.yaml import YAML

from etl.download import download_file_from_s3
from etl.paths import (
    get_bucket_and_key_for_location_data,
    get_bucket_and_key_for_season_pq,
)


@flow
def load_season_to_hashboard(season: int) -> None:
    logger = get_run_logger()
    logger.info("Loading season %s to Hashboard", season)
    bucket, key = get_bucket_and_key_for_season_pq(season)
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["hb", "pull", "--all"], cwd=tmpdir)
        yaml = YAML(typ="rt")
        model = yaml.load(Path(tmpdir) / "m_snowfall.yml")
        model_id = model["grn"]
    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = download_file_from_s3(bucket, key, Path(tmpdir)).resolve()
        subprocess.run(["hb", "upload", str(local_path)])
        subprocess.run(["hb", "cache", "clear", model_id])


@flow
def load_locations_to_hashboard() -> None:
    logger = get_run_logger()
    logger.info("Loading ski location data to Hashboard")
    bucket, key = get_bucket_and_key_for_location_data()
    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = download_file_from_s3(bucket, key, Path(tmpdir)).resolve()
        subprocess.run(["hb", "upload", str(local_path)])


if __name__ == "__main__":
    load_season_to_hashboard(2022)
    load_season_to_hashboard(2023)
    load_locations_to_hashboard()
