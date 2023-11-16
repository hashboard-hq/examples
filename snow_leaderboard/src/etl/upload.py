from pathlib import Path

import boto3


def upload_file_to_s3(local_path: Path, bucket: str, key: str) -> None:
    """
    Places file at local_path in bucket at s3://{bucket}/{key}.
    """
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).upload_file(local_path, key)
