import sys
import os
import pytest
from approvaltests.reporters.generic_diff_reporter_factory import GenericDiffReporterFactory
from approvaltests.reporters import Reporter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from prompt_manager.api import PromptManagerAPI

# Configure approval tests reporter
@pytest.fixture(scope="session", autouse=True)
def configure_approval_tests():
    """Configure approval tests to use a simple reporter for CI/CD compatibility."""
    from approvaltests import Options
    from approvaltests.reporters import ReporterThatAutomaticallyApproves
    
    # Use auto-approve reporter for headless environments
    Options.default_reporter = ReporterThatAutomaticallyApproves()

@pytest.fixture
def client():
    api = PromptManagerAPI()
    app = api.app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client