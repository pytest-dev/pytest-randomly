# Contributing

This page lists  the steps you need to follow to set up your development environment and contribute to the project.

1. Fork and clone this repo

2. Install initial dependencies in a virtual environment:

    ```shell
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install --upgrade 'tox>=4.2'
    ```

3. Run tests:

    ```shell
    tox run
    ```

    or for a specific pythong version:

    ```shell
    tox run -f py311
    ```

4. Lint your code via pre-commit:

    ```shell
    tox -e lint
    ```

5. Re-compile dependencies:

    ```shell
    tox TODO
    ```
