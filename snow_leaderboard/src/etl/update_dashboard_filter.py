import subprocess
from datetime import datetime, time, timezone
from pathlib import Path

import duckdb
from prefect import flow, get_run_logger
from ruamel.yaml import YAML

from etl.paths import (
    get_bucket_and_key_for_location_data,
    get_bucket_and_key_for_season_pq,
    s3_uri,
)

VIZ_DIRECTORY = Path(__file__).parent.parent / "viz"


@flow
def update_dashboard_filter(season: int) -> None:
    logger = get_run_logger()
    # query the current season file to find the resort at the top of the
    # leaderboard
    season_bucket, season_key = get_bucket_and_key_for_season_pq(season=season)
    season_uri = s3_uri(season_bucket, season_key)
    loc_bucket, loc_key = get_bucket_and_key_for_location_data()
    loc_uri = s3_uri(loc_bucket, loc_key)
    conn = duckdb.connect()
    conn.execute("install httpfs; load httpfs; install aws; load aws;")
    conn.execute("call load_aws_credentials();")
    cur = conn.sql(
        f"""
        select distinct
            first_value(locations.name) over (
                order by snowfall.snowfall_ytd desc
            ) as top_resort
        from '{season_uri}' as snowfall
        join '{loc_uri}' as locations on snowfall.location_id = locations.id
    """
    )
    (top_resort_name,) = cur.fetchone()  # type: ignore
    logger.info("%s is top resort", top_resort_name)
    cur = conn.sql(
        f"""
        select max(observed_at) as last_updated_at
        from '{season_uri}' as snowfall
    """
    )
    (last_updated_at,) = cur.fetchone()  # type: ignore
    last_updated_str = datetime.combine(
        last_updated_at, time(hour=12), tzinfo=timezone.utc
    ).isoformat()

    # pull the remote state of all Hashboard assets into
    # config files in the viz directory
    subprocess.run(["hb", "pull", "--all"], cwd=str(VIZ_DIRECTORY))
    yaml = YAML(typ="rt")
    dashboard_path = VIZ_DIRECTORY / "dsb_snowleaderboard.yml"
    dashboard_config = yaml.load(dashboard_path)

    # update the description with "last upated" date:
    description = (
        "There are 661 ski areas in the Lower 48 -- which ones get the most snow?\n\n"
        "Data provided by the National Weather Service's National Gridded Snowfall "
        f"Analysis. Last updated {last_updated_str}.\n"
        '"Observed At" dates represent the 24-hour period preceding 12:00:00 UTC on '
        "that date."
    )
    dashboard_config["description"] = description

    # update the filter value with the top resort name
    for i, section in enumerate(dashboard_config["sections"]):
        for j, filter_ in enumerate(section["filters"]):
            if "columnId" in filter_ and filter_["columnId"] == "name":
                dashboard_config["sections"][i]["filters"][j]["values"] = [
                    top_resort_name
                ]
                logger.info(
                    "Section %s, filter %s updated with %s", i, j, top_resort_name
                )
                break
    yaml.dump(dashboard_config, dashboard_path)

    # deploy the updated dashboard
    subprocess.run(["hb", "deploy", "--no-preview"], cwd=str(VIZ_DIRECTORY))
    logger.info("Dashboard deployed.")


if __name__ == "__main__":
    update_dashboard_filter(2023)
