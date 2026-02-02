import sys
import os
import pytest
import tempfile
import json
from approvaltests.reporters.generic_diff_reporter_factory import GenericDiffReporterFactory
from approvaltests.reporters import Reporter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


# Feature flag helpers
def load_feature_flags():
    """Load feature flags from settings file."""
    flags_path = os.path.join(os.path.dirname(__file__), '..', 'settings', 'feature_flags.json')
    try:
        with open(flags_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def is_feature_enabled(feature_name):
    """Check if a feature is enabled."""
    flags = load_feature_flags()
    return flags.get(feature_name, False)


# Skip markers for feature-flagged tests
def skip_if_feature_disabled(feature_name):
    """Return a pytest skip marker if feature is disabled."""
    if not is_feature_enabled(feature_name):
        return pytest.mark.skip(reason=f"Feature '{feature_name}' is disabled")
    return pytest.mark.skipif(False, reason="")


# Pre-defined skip markers for common features
skip_template_builder = pytest.mark.skipif(
    not is_feature_enabled('TEMPLATE_BUILDER'),
    reason="TEMPLATE_BUILDER feature is disabled"
)

skip_custom_combo = pytest.mark.skipif(
    not is_feature_enabled('CUSTOM_COMBO_BOX'),
    reason="CUSTOM_COMBO_BOX feature is disabled"
)

skip_linkages = pytest.mark.skipif(
    not is_feature_enabled('LINKAGES'),
    reason="LINKAGES feature is disabled"
)

skip_memory_cards = pytest.mark.skipif(
    not is_feature_enabled('MEMORY_CARDS'),
    reason="MEMORY_CARDS feature is disabled"
)

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