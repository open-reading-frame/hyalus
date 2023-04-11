# Hyalus Settings

Hyalus uses settings to configure how the application is run.
These settings are stored by user based on the returned value from `getpass.getuser()`.
Settings can be printed, updated, and/or reset using the `hyalus settings` command.
Descriptions for each setting can also be reported using this command, with the `-d/--descriptions` flag, e.g.

```text
> hyalus settings -d
debug (allowable values - bool, default False): Debug mode for hyalus - turns on debug logging, test runs will always be kept. Overrides cleanup_on_pass
stdout (allowable values - bool, default False): Log test run messages to stdout
config_author (allowable values - str, default ''): Name of author field for the template command. Also used for the credits field
template_output_dir (allowable values - str, default '.'): Path to the output directory when running the template command. Note if given a relative path, it will be relative to where hyalus is run from
runs_dir (allowable values - str, default '.'): Directory to output test runs to. Note if given a relative path, it will be relative to where hyalus is run from
search_dirs (allowable values - list[str], default ['.']): Comma-delimited list of directories to search for hyalus tests in. Note if given a relative path, it will be relative to where hyalus is run from
cleanup_on_pass (allowable values - bool, default False): Cleanup passing test runs
tag_operator (allowable values - ['all', 'any'], default 'any'): Operator to use when searching for tests matching given tags when using the runsuite command
oldest_test_run (allowable values - ^\d{4}-\d{2}-\d{2}|\d+$, default '0001-01-01'): Either the oldest date or the number of days from today for a test run to be kept when using hyalus clean
newest_test_run (allowable values - ^\d{4}-\d{2}-\d{2}|\d+$, default '9999-12-31'): The newest date for a test run to be kept when using hyalus clean
force_clean (allowable values - bool, default False): Flag to indicate that rest runs should be removed without confirmation when using hyalus clean
```

The values for certain settings can be overridden at runtime by passing flags for commands, but the default values for those flags will be set based on values in the user settings file itself.
Hyalus will type/value check settings at runtime and will exit if any setting is found to have an invalid value based on the constraints for each setting.
This is to prevent manually updating the settings files to something not allowed.

# Hyalus Tests

## Creating Tests

Hyalus will consider any directory with a file called `config.py` in it to be a "test".
The `config.py` tells hyalus how to run the test and defines fields intended for engineers looking at the test to understand what the test accomplishes, and why.
All other files that will be used in the test are placed the `input` subdirectory.
Hyalus *requires* the following fields in the `config.py` before it will run a test:

`AUTHOR (str)` - Who wrote the test?

`CREDITS (list[str])` - Who contributed to the creation of the test?

`CREATED_ON (str)` - The date on which the test was created.

`TEST_DESCRIPTION (str)` - A description of the test.
Information should include what the test is accomplishing, why, links to any relevant issues (GitHub, Jira, etc.), and any other pertinent information.

`INPUT_DATA (str)` - If the test has a set of input files being used, this section should include information on where the files came from, any modifications, and any relevant information about what is special about the data set.
If no input files are being used, set to "N/A".

`STEPS (list[StepBase])` - The list of hyalus steps to be run.
Steps are classes that define required inputs and run some sort of functionality.
Examples are running a software pipeline, or making an assertion that a result is as is expected.
Steps that hyalus directly supports can be found [here](https://genapsysinc.github.io/hyalus/_src/hyalus/hyalus.config.steps.html).
Test engineers can create their own Steps by subclassing the [StepBase class](https://genapsysinc.github.io/hyalus/_src/hyalus/hyalus.config.steps.base.html#hyalus.config.steps.base.StepBase).
They can also modify Step behavior by subclassing any other Step.

`TAGS (list[TagBase])` - A list of Tags for the test.
Each Tag defines some sort of metadata for the test, such as expected runtime or the type of test (unit, integration, end-to-end, regression, etc.).
The list of Tags *must* include a [RuntimeTag](https://genapsysinc.github.io/hyalus/_src/hyalus/hyalus.config.tags.runtime.html) at the very least in order to be considered valid.

The `config.py` can import anything available by the Python interpreter that was used to install hyalus.
Hyalus is intentionally developed with very minimal use of third-party packages so that it can be installed in any Python 3.10/3.11 environment and directly integrated with the software undergoing test with minimal possibility for dependency conflicts.
This means that in a `config.py` file, you can directly import a class/function/etc. undergoing test and use it in whatever way you want.
The only third-party package explicitly required is [typing-extensions](https://pypi.org/project/typing-extensions/), which has no third-party dependencies, for typing compatibility between Python versions.
Some functionality is dependent on [h5py](https://www.h5py.org/) and [pandas](https://pandas.pydata.org/), with the expectation being that if HDF5 files or dataframes are wanted to be used, the respective packages are to be installed.
Hyalus conditionally includes the relevant functionality based on whether it is able to import the given package.

### Hyalus Steps

Since Steps are the core functionality of how hyalus runs, understanding how they work and how they are defined is essential to using hyalus.
This section will go over the basic Steps that hyalus explicitly supports and how to define new Steps.

#### Using Steps

As noted above, the Steps for a given hyalus test are defined with the `STEPS` field.
It might look something like:

```python
import json

from hyalus.config.steps import RunFunctionStep, AssertEQ

def custom_func(arg1, arg2, kwarg1=0, kwarg2=0):
    assert arg1 is not None and arg2 is not None

    with open("file.json", 'r', encoding="utf-8") as fh:
        json.dump(fh, {"values": [{"kwarg_sum": kwarg_1 + kwarg2}]})

STEPS = [
    RunFunctionStep(custom_func, "arg1", "arg2", kwarg1=1, kwarg2=2),
    AssertEQ("file.json", {"values": [{"kwarg_sum": 3}]}),
    AssertEQ(("file.json", "values"), [{"kwarg_sum": 3}]),
    AssertEQ(("file.json", ["values", 0, "kwarg_sum"]), 3),
]
```

There are a few things going on here:

* The first Step, `RunFunctionStep`, is executing the `custom_func` function and passing given arguments to the function at runtime.
This function makes some assertions and then writes some things to a file called `file.json`.
* The second Step, `AssertEQ`, is asserting that the contents of `file.json` are equal to `{"values": [{"kwarg_sum": 3}]}`.
Any AssertionStep will automatically parse any file given as input into a corresponding data structure.
In this case, it is parsing a JSON file into a dictionary as was written in `custom_func`.
* The third Step, `AssertEQ` is asserting that the value for `"values"` within `file.json` is equal to `[{"kwarg_sum": 3}]`.
If a length-2 tuple is given as a value to an AssertionStep, hyalus will try to parse the first element of the tuple if it is a file, and then use the second element to "search" the file.
In the case of a JSON file, the second element is used to index into the parsed JSON content.
* The last Step, `AssertEQ` is asserting that the value for `"values"` -> `0` -> `"kwarg_sum"` within `file.json` is equal to `3`.
In the case of the second element of a tuple within an assertion being a list, hyalus will use each element to progressively search a parsed file.
So in this case we have (under the hood) `json_content["values"][0]["kwarg_sum"] == 3` as the assertion being made.

Note that the three `AssertEQ` Steps are essentially doing the same thing, with slight differences as to specifically how deep into the data they are searching and the corresponding comparisons to make.

To note is that contents of multiple files can be compared to each other by giving multiple tuples.
This lets you make an assertion like "assert the value at position x in file 1 == the value at position y in file 2", like:

```python
from hyalus.config.steps import AssertEQ

STEPS = [
    AssertEQ(("output/file_1.json", ["position", "x"]), ("output/file_2.json", ["position", "y"]))
]
```

If hyalus cannot find a file to parse when a filepath is given, it will treat the value as a string literal instead.

#### Pre-defined Steps

[SubprocessStep](https://genapsysinc.github.io/hyalus/_src/hyalus/hyalus.config.steps.run.html#hyalus.config.steps.run.SubprocessStep) - This step will run a subprocess command with any given kwargs applied to the subprocess call.

> **_NOTE:_** `capture_output` will always be set to `True` and `check` will always be set to `False` when running a subprocess - these cannot be overridden.

Example:

```python
from hyalus.config.steps import SubprocessStep

STEPS = [
    # Run "my_app" with given flags, redirecting stdout to some_file.txt"
    SubprocessStep(["my_app", "--flag1", "--flag2"], stdout="some_file.txt")
]
```

[RunFunctionStep](https://genapsysinc.github.io/hyalus/_src/hyalus/hyalus.config.steps.run.html#hyalus.config.steps.run.RunFunctionStep) - This step will run a given function with given args/kwargs

Example:

```python
from hyalus.config.steps import RunFunctionStep

def write_to_file(file_name, to_write=""):
    with open(file_name, 'w', encoding="utf-8") as out_fh:
        out_fh.write(to_write)

STEPS = [
    # Runs write_to_file with file_name="output_file.txt" and to_write="some content\n"
    RunFunctionStep(write_to_file, "output_file.txt", to_write="some content\n")
]
```

[AssertionSteps](https://genapsysinc.github.io/hyalus/_src/hyalus/hyalus.config.steps.assertions.html#hyalus.config.steps.assertions.AssertionStep) - Multiple subclasses of this Step exist, which all perform a specific assertion.
These assertions are defined within the `hyalus.config.steps.assertions` module.

Available Assertions:

* `AssertEQ` - Assert that all given arguments are equal to each other
* `AssertNE` - Assert that none of the given arguments are equal to each other
* `AssertGT` - Assert that given arguments are given in a strictly descending order
* `AssertGE` - Assert that given arguments are given in a non-increasing order
* `AssertLT` - Assert that given arguments are given in a strictly ascending order
* `AssertLE` - Assert that given arguments are given in a non-decreasing order
* `AssertIn` - Assert the first argument is in the second argument
* `AssertNotIn` - Assert the first argument is not in the second argument
* `AssertContains` - Assert the first argument contains the second argument
* `AssertDoesNotContain` - Assert the first argument does not contain the second argument
* `AssertKeysContain` - Assert the first argument's keys (dict) contain the second argument
* `AssertValuesContain` - Assert the first argument's values (dict) contain the second argument
* `AssertItemsContain` - Assert the first argument's items (dict) contain the second argument
* `AssertDataFrameContains` - Assert the first argument (DataFrame) contains a record/row matching a list of column/value pairs

Example:

```python
from hyalus.config.steps import RunFunctionStep, AssertEQ

def write_to_file(file_name, to_write=""):
    with open(file_name, 'w', encoding="utf-8") as out_fh:
        out_fh.write(to_write)

STEPS = [
    # Runs write_to_file with file_name="output_file.txt" and to_write="some content\n"
    RunFunctionStep(write_to_file, "output_file.txt", to_write="some content\n"),
    # Assert that the contents of "output_file.txt" are "some content\n"
    AssertEQ("output_file.txt", "some content\n")
]
```

## Running Tests

Hyalus runs a test by loading the `config.py` and inspecting the `STEPS` field.
Each element of the list of `STEPS` will be executed sequentially.
If any Step fails or errors, hyalus will stop execution of the test and not execute subsequent Steps.
Certain Steps (such as `AssertionSteps`) will *not* cause hyalus to stop on failure, but will still cause hyalus to stop on error.
This functionality is defined by the `halt_on_failure` property of each Step class.
Hyalus will keep track of each Step and whether or not it was successful, writing information to a log file specific to each Step.
Upon completion, hyalus will output an overall test result based on the status of all Steps executed: successfully passed, failed or in error state.

Hyalus tests can be run using two commands via the CLI, `runtest` and `runsuite`, which run a single test or a suite of tests, respectively.
Both commands take test name(s) or direct path(s) to the test to run.
If giving test name(s), hyalus will search directories set in the `search_dirs` hyalus setting to find the test(s) to run.
The `list` command will also search this directory to find tests.
`runsuite` can also take a "test suite" file, with extension `.ste`.
This file should contain a newline-delimited list of test names or other test suites.
By parsing a test suite file, hyalus will figure out all the relevant tests to run.
Test suites can be created for purposes such as regression tests, smoke tests, release testing, etc.
`runsuite` is able to take test names/suites as input from stdin as well, allowing a combination of `hyalus list` and `hyalus runsuite` to be used to find relevant tests, and then run them all.

Examples:

```
# Runs test_001 if it can be found in the current working directory or any directory in the `search_dirs` setting
> hyalus runtest test_001
```

```
# Will run test_001 by following the given path
> hyalus runtest path/to/test_001
```

```
# Runs test_001, test_002, and test_003 if they can all be found
> hyalus runsuite test_001 test_002 test_003
```

```
# Runs all tests in the regression and smoke test suites, as well as test_001
> hyalus runsuite regression.ste smoke.ste test_001
```

```
# Runs all tests found by hyalus list
> hyalus list | hyalus runsuite
```

### Test Results

When running `runtest` or `runsuite`, hyalus will create a run directory for the output of each test that was run.
The name of the directory is created using the name of the test, the date the test run was started, and a random alphanumeric string.
Hyalus will create `output`, `tmp`, and `hyalus` subdirectories within each run directory.
When configuring tests, a test engineer can assume that at runtime these directories will exist, and should attempt to write output files to `output` and temporary files to `tmp`.
If the software under test can be given arguments for output and temporary directories, they should be set accordingly.
The `hyalus` subdirectory is used for information about the hyalus run itself.
It will contain test logs for each Step that was run, as well as a test log for the overall test run.

#### Runtest Results

The result of running a given hyalus test will be output to the console as `SUCCESS`, `FAILURE`, or `ERROR`, depending on the results of the constituent Steps for a given test.
`SUCCESS` means that *all* Steps executed successfully, and *all* assertions made were found to be true.
`FAILURE` means that *all* Steps executed successfully, but *at least one* assertion made was found to be false.
`ERROR` means that hyalus could not successfully execute all of the given Steps because an error occurred.
Hyalus will also exit with an exit code of 0 when the test result was `SUCCESS`, and with an exit code of 1 when the test result was `FAILURE` or `ERROR`.

#### Runsuite Results

The result of each individual hyalus test run will be output to the console, as `SUCCESS`, `FAILURE`, or `ERROR`, just like with `runtest`.
However, the exit code of `runsuite` is 0 if *all* tests had a result of `SUCCESS`, and 1 if *any* test result was `FAILURE` or `ERROR`.

### Test Logs

Hyalus will write a log file for each Step run as part of a given test, as well as a log for the overall test run.
The name for each Step's log is created based on sequentially which Step it is in the list of `STEPS`, the name of the Step class, and a log file suffix `_log.txt`.
Specifics for each Step will be in their respective Step log files, as well as the overall test run log.
The overall test run log is called `hyalus.log`.
During Step execution, any logging from called code will be written to the Step's log as well as anywhere else it should go, such as an app-specific log.

Example:

```python
from hyalus.config.steps import RunFunctionStep, AssertEQ

def write_to_file(file_name, to_write=""):
    with open(file_name, 'w', encoding="utf-8") as out_fh:
        out_fh.write(to_write)

STEPS = [
    RunFunctionStep(write_to_file, "output/output_file.txt", to_write="some content\n"),
    RunFunctionStep(write_to_file, "tmp/tmp_file.txt", to_write="I am a temp file\n"),
    AssertEQ("output/output_file.txt", "some content\n"),
    AssertEQ("tmp/tmp_file.txt", "I am a temp file\n")
]

# Expected logs would be:
# > ls -1
# 1_RunFunctionStep_log.txt
# 2_RunFunctionStep_log.txt
# 3_AssertEQ_log.txt
# 4_AssertEQ_log.txt
# hyalus.log
```

# Pytest Integration

In addition to acting as a standalone tool, hyalus is packaged with functionality which supports integration with [pytest](https://docs.pytest.org/en/7.2.x/).
This functionality lives in the `hyalus.run.python` module.
Hyalus Steps can be run prior to running test cases through pytest's built-in fixture system, as well as with some custom decorators that are shipped with hyalus.
Hyalus also comes with the `run_dir` fixture that, when requested, will create a hyalus run directory from pytest's `tmp_path` fixture.
This fixture will automatically be available to any pytest-style test upon installing hyalus in an environment.
The benefits to using hyalus functionality in this way are not substantial compared to creating custom fixtures that run specific pieces of code, but does allow for custom Steps to be used in both a pytest setting as well as a standalone hyalus setting.

## Fixtures

### Packaged Fixtures

The `hyalus.run.python.fixture_run_dir` fixture (named `run_dir`) can be used by any test.
It will create `input`, `output`, `tmp`, and `hyalus` subdirectories in whatever directory is pointed to by the `tmp_path` fixture (if they do not already exist), and return a [`HyalusRun`](https://genapsysinc.github.io/hyalus/_src/hyalus/hyalus.run.common.html#hyalus.run.common.HyalusRun) object.
This object has properties that can be used to access the relevant subdirectories, namely `input_dir`, `output_dir`, `tmp_dir`, and `hyalus_dir`.
The `run_dir` can then be used with hyalus Steps within the body of a test.

Example:

```python
from hyalus.config.steps import SubprocessStep

def test_step_output(run_dir):
    step = SubprocessStep(["my_app", "--flag1", "--flag2", "-o", str(run_dir.output_dir)])
    step.run(1, run_dir)

    with open(run_dir.output_dir / "my_app_output.txt", 'r') as fh:
        assert fh.read() == "expected_content"
```

### Custom Fixtures

If the above didn't seem that useful (couldn't you just do a `subprocess.call`?), custom fixtures using `run_dir` and Steps will start to give a little more flexibility.
Steps can be reused in multiple test cases by abstracting the Step being run into another fixture.

Example:

```python
import pytest

from hyalus.config.steps import SubprocessStep

# Scope the fixture to the module so we only run it once
@pytest.fixture(scope="module")
def my_app_step(run_dir):
    step = SubprocessStep(["my_app", "--flag1", "--flag2", "-o", str(run_dir.output_dir)])
    return step.run(1, run_dir)


# Check that output content matches what was expected
def test_step_output(my_app_step, run_dir):
    with open(run_dir.output_dir / "my_app_output.txt", 'r') as fh:
        assert fh.read() == "expected_content"


# Assert the app exited with an exit code of 0
def test_returncode(my_app_step):
    assert run_my_app.returncode == 0
```

## Decorators

Hyalus comes with decorators intended to be similar to pytest fixtures but with added flexibility.
Fixtures cannot take input (although they *can* be parameterized), but these decorators can, in the form of Steps.
This allows for concrete definitions of pre-processing at test function/method definition time.

### run_steps

The `hyalus.run.python.run_steps` decorator takes *n* Steps as input, and will run them prior to function execution.
The Steps can be reused by any number of tests.
When using this decorator on a pytest test, the `run_dir` fixture is automatically requested and used by each Step.
However, if the test does not explicitly request the fixture, it cannot be used within the body of the function as this would break scope; to use `run_dir` within the body of the function, it must explicitly be requested.

Example:

```python
from hyalus.config.steps import SubprocessStep
from hyalus.run.python import run_steps

# For the sake of example, say we have 3 apps. pre_process will exit with code 0 always. my_app will exit with code 0 if
# the last command run was pre_process, otherwise with code 1. post_process will exit with code 0 if the last command
# run was my_app, otherwise with code 1.
step_1 = SubprocessStep(["pre_process", "--flag1"])
step_2 = SubprocessStep(["my_app", "--flag1", "--flag2"])
step_3 = SubprocessStep(["post_process", "--flag1"])
# "Flush" the last call
step_4 = SubprocessStep(["ls"])

# Steps are run at function call time, not definition time...
@run_steps(step_1, step_2, step_4)
def test_pre_process_and_app_call():
    # ... so inside the body of the function, we can inspect the Steps and see how they were run
    assert step_1.returncode == 0
    assert step_2.returncode == 0


@run_steps(step_1, step_3, step_4)
def test_pre_process_and_post_process():
    assert step_1.returncode == 0
    assert step_3.returncode == 1


@run_steps(step_2, step_3, step_4)
def test_app_call_and_post_process():
    assert step_2.returncode == 1
    assert step_3.returncode == 1


@run_steps(step_1, step_2, step_3, step_4)
def test_all_calls():
    assert step_1.returncode == 0
    assert step_2.returncode == 0
    assert step_3.returncode == 0
```

`run_steps` can also be used outside of the scope of pytest.
This can be done by setting the kwarg `running_pytest` to `False` when decorating.

Example:

```python
from hyalus.config.steps import RunFunctionStep
from hyalus.run.python import run_steps, apply_decorator

step_1 = RunFunctionStep(print, "1")
step_2 = RunFunctionStep(print, "2")

@run_steps(step_1, step_2, running_pytest=False)
def print_lots(*to_print):
    for item in to_print:
        print(item)

# Prints 1, 2, 3, 4, and 5
print_lots("3", "4", "5")
```

### apply_decorator

The `hyalus.run.python.apply_decorator` decorator decorates *all methods of a class* with a given decorator.
In conjunction with the `run_steps` decorator, this lets you run a set of Steps prior to every single test method of a test class.
Additionally, each test method can also be decorated with the `run_steps` decorator individually, which will cause Steps to be run *after* the Steps from the class-level decoration.

Example:

```python
from hyalus.config.steps import RunFunctionStep
from hyalus.run.python import run_steps, apply_decorator

step_1 = RunFunctionStep(print, "1")
step_2 = RunFunctionStep(print, "2")
step_3 = RunFunctionStep(print, "3")

# Class-level decoration - all methods will always print 1 and 2 prior to execution
@apply_decorator(run_steps(step_1, step_2))
class TestMyApp:

    # Results in 1, 2, and 4 being printed in that order
    def test_1(self):
        print("4")

    # Results in 1, 2, 3, and 4 being printed in that order
    @run_steps(step_3)
    def test_2(self):
        print("4")

    # Results in 1, 2, 3, 2, 1, and 4 being printed in that order
    @run_steps(step_3)
    @run_steps(step_2, step_1)
    def test_3(self):
        print("4")
```

# Hyalus CLI

## Settings

Update user settings for hyalus.

### Help

```text
> hyalus settings -h
usage: hyalus settings [-h] [-d] [-u UPDATE [UPDATE ...]] [-r RESET [RESET ...]]

options:
  -h, --help            show this help message and exit
  -d, --descriptions    Print descriptions for all settings prior to outputting current setting values
  -u UPDATE [UPDATE ...], --update UPDATE [UPDATE ...]
                        Setting/value pairs in the format '<setting>=<value>' to use to update hyalus configuration.
  -r RESET [RESET ...], --reset RESET [RESET ...]
                        Setting names to reset to default value.
```

### Examples

```text
> hyalus settings
debug: False
stdout: True
config_author:
template_output_dir: .
runs_dir: .
search_dirs: ['/path/to/some/tests', '/path/to/separate/tests']
cleanup_on_pass: False
tag_operator: any
oldest_test_run: 0001-01-01
newest_test_run: 9999-12-31
force_clean: False
```

```text
> hyalus settings --update stdout=false
debug: False
stdout: False
config_author:
template_output_dir: .
runs_dir: .
search_dirs: ['/path/to/some/tests']
cleanup_on_pass: False
tag_operator: any
oldest_test_run: 0001-01-01
newest_test_run: 9999-12-31
force_clean: False
```

```text
> hyalus settings --reset stdout
debug: False
stdout: False
config_author:
template_output_dir: .
runs_dir: .
search_dirs: ['/path/to/some/tests']
cleanup_on_pass: False
tag_operator: any
oldest_test_run: 0001-01-01
newest_test_run: 9999-12-31
force_clean: False
```

### Notes

`hyalus settings` cannot be run with both `--update` and `--reset` simultaneously if a setting is specified in both sections - should it be updated or reset?

The `hyalus settings` command will automatically include new settings when they are added to hyalus via the `update` subcommand.

## Template

Create a new hyalus test from a template config file.

### Help

```text
> hyalus template -h
usage: hyalus template [-h] [-o OUTPUT_DIR] [-c CONFIG_TEMPLATE] tests [tests ...]

positional arguments:
  tests                 List of names of template tests to make.

options:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory path for the generated template tests. Defaults to the template_output_directory config setting.
  -c CONFIG_TEMPLATE, --config-template CONFIG_TEMPLATE
                        Use a given config file template instead of the default hyalus one.
```

### Examples

```text
> hyalus template test_1 -o .
> ls test_1
config.py input     output    tmp
```

### Notes

`hyalus template` will output generated template tests to the directory pointed at by the `template_output_directory` user setting.

The only field used in the default config template is `config_author`.
This template can be changed with the `-c` option.

The default config template can be found at `src/hyalus/run/static/config_template`.
Fields are filled out based on user setting values using the `str.format` method.
So in the template, `{config_author}` will be replaced with whatever `config_author` is set to in the user settings.

## List

List available tests, optionally matching given tags.

### Help

```text
> hyalus list -h
usage: hyalus list [-h] [-t TAGS [TAGS ...]] [-o {any,all}]

options:
  -h, --help            show this help message and exit
  -t TAGS [TAGS ...], --tags TAGS [TAGS ...]
                        List of tags to compare against hyalus test config files which when matched will result in a given test being run, e.g. 'Short' will run all
                        tests tagged with the 'Short' tag. Tags are case insensitive. If multiple tags are given, tests will have to meet either any of or all of
                        the given tags based on the tag operator.
  -o {any,all}, --tag-op {any,all}
                        Operator to apply to tag searching. 'any' means config must match one or more of specified tags, 'all' means config must match all of the
                        specified tags.
```

### Examples

```text
> hyalus list
runtest_1
runtest_2
runtest_7
```

```text
> hyalus list -t short
runtest_1
```

```text
> hyalus list -t short medium -o any
runtest_1
runtest_2
```

```text
> hyalus list -t short medium -o all
(no output)
```

### Notes

`hyalus list` searches directories stored in the `search_dirs` user setting for tests.
It does not check for validity of `config.py` files, only that they exist.

If no tags are given, *all* tests found will be reported.

The tag operator defaults to whatever the `tag_operator` user setting is set to.

Output from `hyalus list` can be piped into `hyalus runsuite` to find given tests and then execute them.

## Runtest

Run a single hyalus test.

### Help

```text
> hyalus runtest -h
usage: hyalus runtest [-h] test

positional arguments:
  test        Name or path of test to run. Hyalus will look in the current working directory as well as any directories pointed to in the search_dirs config setting
              if a name is given. If a path is given, hyalus will grab the test directly from that path, relative to the current working directory.

options:
  -h, --help  show this help message and exit
```

### Examples

```text
> hyalus runtest runtest_1
/path/to/runs_dir/runtest_1_2023-03-15_yJ4Pev5q: SUCCESS
> echo $?
0
```

```text
 > hyalus runtest runtest_2
/path/to/runs_dir/runtest_2_2023-03-15_mG06KqXT: FAILURE
> echo $?
1
```

### Notes

`hyalus runtest` searches directories in the `search_dirs` user setting for tests, and will output them in the directory pointed to by the `runs_dir` user setting.

The `cleanup_on_pass` user setting can be set to `True` to automatically remove passing tests after they have been run.
When the `debug` user setting is set to `True`, the `cleanup_on_pass` flag is ignored.

If the `stdout` user setting is set to True or the `-s` flag is provided to hyalus, logging will be written to stdout as well as hyalus log files.

## Runsuite

Run multiple tests and/or suites of tests, optionally only matching giving tags.

### Help

```text
> hyalus runsuite -h
usage: hyalus runsuite [-h] [-t TAGS [TAGS ...]] [-o {any,all}] [tests ...]

positional arguments:
  tests                 Names or paths of tests/test plans to run. Hyalus will look in the current working directory as well as any directories pointed to in the
                        search_dirs config setting to find tests and test plans to run if just names are given. If paths are given, hyalus will grab the tests and
                        test plans directly from those paths, relative to the current working directory.

options:
  -h, --help            show this help message and exit
  -t TAGS [TAGS ...], --tags TAGS [TAGS ...]
                        List of tags to compare against hyalus test config files which when matched will result in a given test being run, e.g. 'Short' will run all
                        tests tagged with the 'Short' tag. Tags are case insensitive. If multiple tags are given, tests will have to meet either any of or all of
                        the given tags based on the tag operator.
  -o {any,all}, --tag-op {any,all}
                        Operator to apply to tag searching. 'any' means config must match one or more of specified tags, 'all' means config must match all of the
                        specified tags.
```

### Examples

```text
> hyalus runsuite runtest_1 runtest_7
/path/to/runs_dir/runtest_7_2023-03-15_3eLw7E3H: SUCCESS
/path/to/runs_dir/runtest_1_2023-03-15_oBhA7lnX: SUCCESS
> echo $?
0
```

```text
> hyalus runsuite runtest_1 runtest_2
/path/to/runs_dir/runtest_1_2023-03-15_ciPf1Ghk: SUCCESS
/path/to/runs_dir/runtest_2_2023-03-15_fDe4oamx: FAILURE
> echo $?
1
```

```text
> hyalus runsuite test_plan.ste
/path/to/runs_dir/runtest_7_2023-03-15_3eLw7E3H: SUCCESS
/path/to/runs_dir/runtest_1_2023-03-15_oBhA7lnX: SUCCESS
```

```text
> hyalus list | hyalus runsuite
/path/to/runs_dir/runtest_1_2023-03-15_fQD2dzBJ: SUCCESS
/path/to/runs_dir/runtest_2_2023-03-15_yg18c260: FAILURE
/path/to/runs_dir/runtest_7_2023-03-15_oB5wtusU: SUCCESS
```

```text
> hyalus list -t short medium -o any | hyalus runsuite
/path/to/runs_dir/runtest_1_2023-03-15_ttS3C9jA: SUCCESS
/path/to/runs_dir/runtest_2_2023-03-15_OYPzP3G9: FAILURE
```

### Notes

`hyalus runsuite` uses the same user settings as `hyalus runtest`, in addition to the `tag_operator` setting.

Tests are run in parallel, and the results of each test are output to the console in whatever order they finish in.
This is *not* guaranteed to be the same across multiple runs!

Any logging to stdout is turned *off* with `hyalus runsuite`.
This is to prevent log streams showing up from different tests at the same time on the console, which is inherently confusing and actively unhelpful.

## Clean

Clean up old hyalus test runs based on matching tags and date criteria.

### Help

```text
> hyalus clean -h
usage: hyalus clean [-h] [-t TAGS [TAGS ...]] [-o {any,all}] [--oldest OLDEST] [--newest NEWEST] [-f] [test_names ...]

positional arguments:
  test_names            Names of tests to match against test runs. If none provided, all test runs will be considered matched.

options:
  -h, --help            show this help message and exit
  -t TAGS [TAGS ...], --tags TAGS [TAGS ...]
                        List of tags to compare against hyalus test config files which when matched will result in a given test being run, e.g. 'Short' will run all
                        tests tagged with the 'Short' tag. Tags are case insensitive. If multiple tags are given, tests will have to meet either any of or all of
                        the given tags based on the tag operator.
  -o {any,all}, --tag-op {any,all}
                        Operator to apply to tag searching. 'any' means config must match one or more of specified tags, 'all' means config must match all of the
                        specified tags.
  --oldest OLDEST       Date in the format YYYY-MM-DD OR integer specifying the oldest date a test run should be kept, or the number of days from today a test run
                        should be kept, respectively. Defaults to the oldest_test_run config setting.
  --newest NEWEST       Date in the format YYYY-MM-DD specifying the newest date a test run should be kept. Defaults to the newest_test_run config setting.
  -f, --force           Force clean any test runs found to match criteria
```

### Examples

```text
> hyalus clean
12 test runs marked for removal. Are you sure you want to proceed? Y/N
y
12 old test runs have been removed
```

```text
> hyalus clean
12 test runs marked for removal. Are you sure you want to proceed? Y/N
n
Test run removal canceled
```

```text
> hyalus clean -f
6 old test runs have been removed
```

```text
> hyalus clean -t short
4 test runs marked for removal. Are you sure you want to proceed? Y/N
y
4 old test runs have been removed
```

```text
> hyalus clean --oldest 30
2 test runs marked for removal. Are you sure you want to proceed? Y/N
y
2 old test runs have been removed
```

### Notes

`hyalus clean` will look in the directory pointed at by the `runs_dir` user setting and remove tests accordingly.

By default, the user is prompted to confirm test removal, but by setting the `force_clean` user setting to `True`, or giving the `-f` flag, this confirmation is skipped.

**When no arguments are given, all tests will be marked for removal!**

The `--oldest` and `--newest` flags, and their corresponding user settings `oldest_test_run` and `newest_test_run`, can be used in conjunction with Cron jobs or something similar to automatically remove old test runs after a given amount of time.

## Version

Display the version of hyalus currently installed.

### Help

```text
> hyalus version -h
usage: hyalus version [-h]

options:
  -h, --help  show this help message and exit
```

### Examples

```text
> hyalus version
hyalus version: 0.1.0
```

### Notes

The version can also be retrieved from within a python interpreter session by accessing `hyalus.__version__`, e.g.

```text
> python
Python 3.10.9 (main, Jan 18 2023, 17:16:21) [Clang 13.1.6 (clang-1316.0.21.2.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import hyalus
>>> hyalus.__version__
'0.1.0'
```

The version itself is configured/updated at `src/hyalus/metadata.json`.
