import duckdb
from prefect import flow, get_run_logger

from etl.paths import (
    get_bucket_and_key_for_daily_pq_season_dir,
    get_bucket_and_key_for_season_pq,
)


@flow
def concatenate_season_data(season: int) -> None:
    logger = get_run_logger()
    logger.info("Concatenating all daily files for season %s", season)
    source_bucket, source_key = get_bucket_and_key_for_daily_pq_season_dir(
        season=season
    )
    source_uri = f"s3://{source_bucket}/{source_key}"

    conn = duckdb.connect()
    conn.execute("install httpfs; load httpfs; install aws; load aws;")
    conn.execute("call load_aws_credentials();")
    cur = conn.sql(
        f"""
        select id as location_id, observed_at, snowfall_24h, snowfall_ytd
        from '{source_uri}/*.parquet'
        where snowfall_24h >= 0.0
    """
    )

    dest_bucket, dest_key = get_bucket_and_key_for_season_pq(season=season)
    dest_uri = f"s3://{dest_bucket}/{dest_key}"
    cur.write_parquet(file_name=dest_uri, compression="snappy")
    logger.info("Wrote season dataset to %s", dest_uri)


if __name__ == "__main__":
    concatenate_season_data(2022)
    concatenate_season_data(2023)
