import duckdb
from prefect import flow, get_run_logger, task
from prefect.events import emit_event

from etl.paths import (
    get_bucket_and_key_for_location_data,
    get_bucket_and_key_for_season_pq,
    s3_uri,
)


@task
def get_latest_snowfall_for_resorts(
    resorts: list[str], season: int
) -> list[tuple[str, float]]:
    """
    Query a season file to find the most recent snowfall for specific resorts.
    """

    season_bucket, season_key = get_bucket_and_key_for_season_pq(season=season)
    season_uri = s3_uri(season_bucket, season_key)
    loc_bucket, loc_key = get_bucket_and_key_for_location_data()
    loc_uri = s3_uri(loc_bucket, loc_key)
    locations_str = ", ".join([f"'{resort}'" for resort in resorts])
    conn = duckdb.connect()
    conn.execute("install httpfs; load httpfs; install aws; load aws;")
    conn.execute("call load_aws_credentials();")
    cur = conn.sql(
        f"""
        select distinct
            locations.name,
            first_value(snowfall.snowfall_24h) over (
                partition by locations.name
                order by observed_at desc
            ) as latest_snowfall
        from '{season_uri}' as snowfall
        join '{loc_uri}' as locations on snowfall.location_id = locations.id
        where locations.name in ({locations_str})
    """
    )
    latest_snowfall: list[tuple[str, float]] = cur.fetchall()
    return latest_snowfall


@flow
def check_for_powder_day(season: int) -> None:
    logger = get_run_logger()
    resorts = [
        "Lake Eldora Ski Area (CO)",
        "Vail Ski Area (CO)",
        "Winter Park Ski Area (CO)",
    ]
    latest_snowfall = get_latest_snowfall_for_resorts(resorts=resorts, season=season)
    logger.info("Got recent snowfall data: %s", latest_snowfall)
    assert latest_snowfall is not None
    for resort, snowfall in latest_snowfall:
        if snowfall >= 6.0:
            emit_event(
                event="powder_day",
                resource={"prefect.resource.id": "snowfall"},
                payload={"resort": resort, "snowfall_24h": snowfall},
            )


if __name__ == "__main__":
    check_for_powder_day(2023)
