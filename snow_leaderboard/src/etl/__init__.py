from datetime import date, datetime, timedelta, timezone

from prefect import flow, get_run_logger

from etl.check_for_powder import check_for_powder_day
from etl.extract_daily_data import create_daily_dataset
from etl.load_hashboard import load_season_to_hashboard
from etl.paths import get_season_of_partition
from etl.transform_season_data import concatenate_season_data
from etl.update_dashboard_filter import update_dashboard_filter


def today() -> date:
    now_utc = datetime.now(tz=timezone.utc)
    return now_utc.date()


@flow
def backfill_all_daily_datasets_in_season(season: int) -> None:
    """
    The season is defined by the year it starts in; e.g., 23/24 season is 2023.
    This creates all daily datasets for a season and then concatenates them
    into a single file.

    The ski locations dataset must already exist in the s3 bucket.

    Args:
        season (int): The snow season to backfill, e.g., 2023 for the '23/'24
            season.
    """
    logger = get_run_logger()
    logger.info("Starting backfill for year %s", season)

    start_date = date(year=season, month=10, day=1)
    end_date = min(
        date(year=season + 1, month=10, day=1), today() + timedelta(days=1)
    )  # exclusive

    days = (end_date - start_date).days
    for i in range(days):
        create_daily_dataset(start_date + timedelta(days=i))

    concatenate_season_data(season=season)
    load_season_to_hashboard(season=season)


@flow
def update_current_season(delta: timedelta = timedelta(days=5)) -> None:
    """
    Snow data may be updated for up to 5 days after the observation date.

    delta (timedelta): The delta before today to update. Defaults to 5 days.
    """
    start_date = today() - delta
    end_date = today() + timedelta(days=1)  # exclusive
    logger = get_run_logger()
    logger.info("Starting backfill from %s to %s", start_date, end_date)
    days = (end_date - start_date).days
    for i in range(days):
        create_daily_dataset(start_date + timedelta(days=i))
    season = get_season_of_partition(partition=end_date)
    concatenate_season_data(season=season)
    load_season_to_hashboard(season=season)
    update_dashboard_filter(season=season)
    check_for_powder_day(season=season)
