(modelsearch_developing)=

# Developing

This page contains guidance for developing Django Modelsearch itself.

## Developer installation

From the root of the cloned repository, run:

```shell
pip install -e ".[test,docs,dev]"
```

## Testing

To run the test suite, run:

```shell
python ./runtests.py --backend BACKEND
```

where BACKEND is one of: `db`, `elasticsearch7`, `elasticsearch8`, `elasticsearch9`, `opensearch1`, `opensearch2`, `opensearch3`.

## Linting

This project uses [Ruff](https://docs.astral.sh/ruff/) for code linting and formatting. To run the linter:

```shell
make lint
```

To install the pre-commit hook so that linting is applied on every commit, run:

```shell
pre-commit install
```

## Documentation

To build the documentation, run the following from `docs`:

```shell
make html
```
