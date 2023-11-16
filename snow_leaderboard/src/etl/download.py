from pathlib import Path
from urllib.parse import urlsplit

import boto3
import requests


def download_file_from_url(
    url: str, local_dir: Path, filename: str | None = None
) -> Path:
    """
    Downloads the file at url into local_dir; if filename is not provided, it is
    taken from the last part of the url.

    Args:
        url (str): The url for the file to be downloaded.
        local_dir (Path): A Path to a directory to download the file to.
        filename (str | None): The name of the downloaded file, including the
            extension. If not provided, will be built from the url.
    Returns:
        Path: the path to the downloaded file.
    """
    if not filename:
        filename = urlsplit(url).path.split("/")[-1]
    p = local_dir / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(p, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    return p


def download_file_from_s3(
    bucket: str, key: str, local_dir: Path, filename: str | None = None
) -> Path:
    """
    Downloads file at s3://{bucket}/{key} to local_dir / filename.
    """
    s3 = boto3.resource("s3")
    if not filename:
        filename = key.split("/")[-1]
    p = local_dir / filename
    s3.Bucket(bucket).download_file(key, p)
    return p
