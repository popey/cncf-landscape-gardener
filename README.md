# cncf-landscape-gardener

A tool to maintain the CNCF Landscape.

## Introduction

`cncf-landscape-gardener` is a Python script designed to help maintain the [CNCF Landscape](https://github.com/cncf/landscape) YAML file (`landscape.yml`). It checks the validity of repository URLs within the file, ensuring they are accessible, public, and not archived (unless they are a CNCF archived project).

This tool helps automate the process of keeping the landscape data clean and up-to-date.

## Installation

`cncf-landscape-gardener` is written in Python and uses the `PyYAML` and `requests` libraries.

### Prerequisites

You need Python and the required libraries installed.

I use [uv](https://github.com/astral-sh/uv) to manage Python virtual environments. It's good. You might like it too.

```shell
git clone [https://github.com/popey/cncf-landscape-gardener](https://github.com/popey/cncf-landscape-gardener)
cd cncf-landscape-gardener
uv venv
source .venv/bin/activate
uv pip install PyYAML requests
```

## Usage

- Clone the CNCF Landscape repository:

    ```shell
    git clone [https://github.com/cncf/landscape](https://github.com/cncf/landscape)
    cd landscape
    ```

- Run the `cncf-landscape-gardener.py` script, providing the path to the `landscape.yml` file:

    ```shell
    python ../cncf-landscape-gardener.py
    ```

    The script will analyze the `landscape.yml` file and print a list of repositories with issues (e.g. private, incubating, archived, or deleted), or a message indicating that no issues were found.

## Functionality

The script performs the following checks:

* **Valid GitHub URL:** Checks if the `repo_url` is a valid GitHub repository URL.
* **Repository Existence:** Checks if the repository exists on GitHub.
* **Public/Private:** Checks if the repository is public or private.
* **Archived Status:** Checks if the repository is archived.
* **Organization URL Filtering:** Skips URLs that point to GitHub organizations instead of repositories.
* **CNCF Project Status:** If a repository is archived, it checks if the project has a CNCF project status (e.g., "archived") in the `landscape.yml` file and includes this information in the output.
* **Error Handling:** Handles common HTTP errors (404, 429, etc.) and retries when rate-limited.

## Missing Features

* Only checks GitHub URLs - should add capability to check other forge URLs

## License

This project is licensed under the Apache 2.0 License.
