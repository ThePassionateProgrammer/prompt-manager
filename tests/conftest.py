import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from prompt_manager.api import PromptManagerAPI

@pytest.fixture
def client():
    api = PromptManagerAPI()
    app = api.app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client