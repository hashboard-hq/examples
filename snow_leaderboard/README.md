# Snow Leaderboard
This project extracts data from NOAA's National Gridded Snowfall Analysis,
transforms it into tabular data, and loads it into Hashboard as files. The
workflow is orchestrated by Prefect.

## Building this Project
This project is in Python and is built using Poetry.

1.  Install Python 3.10 or higher
2.  Install [Poetry](https://python-poetry.org/docs/) using any
    method; `pipx install poetry` is easiest if you already have pipx installed.
3.  Install the Poetry-dotenv [plugin](https://pypi.org/project/poetry-dotenv-plugin/)
    with `poetry self add poetry-dotenv-plugin`.
5.  Clone this project into a folder on your machine. `cd` to that folder.
6.  Create a new file, `.env`, in the root directory of this project. That file should
    contain the environment variables needed to run this project locally. It will
    look like this:
    ```sh
    S3_BUCKET = <my bucket>
    S3_PREFIX = <dir inside bucket>
    ```
7.  Run `poetry install --sync` to install the dependencies for this project,
    including development and testing dependencies, into a virtual environment
    managed by Poetry. Ensure the Python version of the venv is at least 3.10
    (you should get a warning if that is not the case).
8.  Run `poetry shell` to spawn a subshell with the virtual environment activated
    and the environment variables loaded from the `.env` file.
9.  Run `pre-commit install` to install the pre-commit hooks. These will prevent
    un-linted changes from being committed.
10.  Run `make` to run tests and linters, or `make lint` to skip tests and run linters.
11.  Run `python -m etl` to run the daily job to update the data in Hashboard.