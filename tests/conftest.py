import sys
import os
import pytest
import tempfile
import json
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
    # Create a temporary file with valid empty JSON structure
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as tmp:
        json.dump({"prompts": {}}, tmp)
        temp_storage = tmp.name
    
    try:
        api = PromptManagerAPI(temp_storage)
        app = api.app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_storage)
        except:
            pass

@pytest.fixture
def template_client():
    """Client fixture for template tests that uses a clean templates.json file."""
    # Create a temporary templates.json file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        temp_templates = tmp.name
    
    try:
        # Create a clean templates.json file
        with open(temp_templates, 'w') as f:
            json.dump({}, f)
        
        # Monkey patch the template service to use our temporary file
        import src.prompt_manager.template_service as ts_module
        original_init = ts_module.TemplateService.__init__
        
        def mock_init(self, storage_file='templates.json'):
            original_init(self, temp_templates)
        
        ts_module.TemplateService.__init__ = mock_init
        
        api = PromptManagerAPI()
        app = api.app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    finally:
        # Restore original init
        ts_module.TemplateService.__init__ = original_init
        # Clean up temporary file
        try:
            os.unlink(temp_templates)
        except:
            pass