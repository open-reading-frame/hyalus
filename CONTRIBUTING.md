# Installation

Hyalus is packaged as a python package, installable with `pip`.
It is not currently hosted anywhere other than GitHub, so must be installed with `pip` by pointing to this repo.

```bash
python -m pip install "git+https://${GITHUB_TOKEN}@github.com/GenapsysInc/hyalus@main"
```

where `${GITHUB_TOKEN}` is an environment variable corresponding to a [GitHub PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

If a specific version is desired, `main` can be replaced with the version, e.g.

```bash
python -m pip install "git+https://${GITHUB_TOKEN}@github.com/GenapsysInc/hyalus@<version>"
```

Hyalus can also be installed by cloning the [hyalus git repository](https://github.com/GenapsysInc/hyalus) and running `pip install .` inside the repository.
It can be installed in development mode by running `pip install -e .`.
This will link `src/hyalus` to the python site-packages directory so that when edited locally, changes are automatically incorporated when changing hyalus functionality.

> **_NOTE:_** Installing in development mode will *not* update the main entrypoint for hyalus, so to incorporate changes made to `src/bin/hyalus`, hyalus will have to be reinstalled.

# Making Changes

Submit a pull request at <https://github.com/GenapsysInc/hyalus>.
All pull requests are expected to have at least one corresponding test case added/changed to test the changes.
All existing tests and new tests must be passing to merge into `main`.
Code coverage must also be at or above 90%.
Tests can be run locally by running `make test` or `pytest --cov`.
`pytest` and `pytest-cov` must be installed to run tests and gather coverage information.
`make test` will display both test results as well as code coverage from running the test suite.

```text
> make test
pytest --cov
======================================================================== test session starts =========================================================================
platform darwin -- Python 3.11.1, pytest-7.2.2, pluggy-1.0.0
rootdir: /path/to/git/hyalus
plugins: cov-4.0.0, hyalus-0.1.0
collected 373 items

tests/assertions/test_apply.py ....                                                    [  1%]
tests/assertions/test_compare.py ..................................................    [ 14%]
tests/config/test_loader.py ......                                                     [ 16%]
...
tests/utils/test_json_utils.py ...........................                             [ 93%]
tests/utils/test_logging_utils.py ............                                         [ 96%]
tests/utils/test_typing_utils.py ............                                          [100%]

---------- coverage: platform darwin, python 3.11.1-final-0 ----------
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
src/hyalus/__init__.py                    4      0   100%
src/hyalus/assertions/__init__.py         0      0   100%
src/hyalus/assertions/apply.py           16      0   100%
...
src/hyalus/utils/logging_utils.py        61      4    93%   73-75, 96
src/hyalus/utils/pandas_utils.py         13      2    85%   11-12
src/hyalus/utils/typing_utils.py         34      0   100%
-------------------------------------------------------------------
TOTAL                                  1450     29    98%

Required test coverage of 90.0% reached. Total coverage: 98.00%
```

Hyalus is a (largely) typed python package. All changes should have typing annotations added as applicable.
Static type checking is performed using [mypy](https://mypy-lang.org/) as part of the build.
`mypy` can be run locally by running `make mypy` or `mypy .`.

```text
> make mypy
mypy .
Success: no issues found in 68 source files
```

Other static analysis is performed with [pylint](https://pypi.org/project/pylint/).
`pylint` can be run locally by running `make pylint` or `pylint --recursive=true .`.

```text
> make pylint
pylint --recursive=true .
************* Module src.hyalus.parse.h5
src/hyalus/parse/h5.py:18:1: W0511: TODO: When https://github.com/python/mypy/issues/12280 has been addressed, remove any type: ignore comments (fixme)
src/hyalus/parse/h5.py:30:9: W0511: TODO: Probably a smarter, less memory intensive way to do this? (fixme)
************* Module src.hyalus.parse.base
src/hyalus/parse/base.py:25:1: W0511: TODO: When https://github.com/python/mypy/issues/12280 has been addressed, remove any type: ignore comments (fixme)

------------------------------------------------------------------
Your code has been rated at 9.99/10 (previous run: 9.99/10, +0.00)
```

Documentation for hyalus code and corresponding tests can be found at <https://genapsysinc.github.io/hyalus>.
[Sphinx](https://www.sphinx-doc.org/en/master/) and [sphinx-apidoc](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html) are used to render code documentation.
Docstrings should be added to new modules, classes, methods, functions, etc. in valid [Python Signatures format](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#signatures) where applicable.
Documentation can be rendered locally by running `make html`.
The output from the doc build will be in `_builder/html`.

The hyalus *package* versioning follows [Semantic Versioning](https://semver.org/), in the format `MAJOR.MINOR.PATCH`.
The hyalus *repository* versioning includes a `-RELEASE` number appended onto the package version, where `RELEASE` corresponds to a change made to the repository that has no impact on functionality, such as changes to documentation.
Changes made to hyalus should incur a change in version based on the nature of the change.
The version is defined in `src/hyalus/metadata.json`.
The hyalus repository will be automatically tagged by GitHub Actions according to the defined version.

# Reporting Issues

Create a issue at <https://github.com/GenapsysInc/hyalus/issues>.
Describe what the problem is, including expected behavior, observed behavior, and any information to reproduce the issue, such as `hyalus` version, python version, and operating system.
The issue template will have sections to fill out with this sort of information.
