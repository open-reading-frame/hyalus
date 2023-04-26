"""Used to redefine hyalus fixtures to avoid the issues that arise from using pytest to test a pytest plugin"""

# Import fixtures here so that pytest becomes aware of them for any tests
from hyalus.run.python import fixture_run_dir

# Set up logging for the entire test suite here just once, within the main interpreter session
from hyalus.utils.logging_utils import configure_logging

configure_logging()
