# 🎯 Template Builder Integration Plan - "Make the Change Easy, Then Make the Easy Change"

## 📚 **Principles We're Following**

### **Kent Beck's Wisdom:**
> "Make the change easy, then make the easy change."

### **Our Approach:**
1. **Design to Interfaces** - Define strong contracts
2. **Refactor to Open/Closed** - Create space before adding features
3. **Test-Driven Development** - Red → Green → Refactor
4. **Emergent Design** - Let the design emerge from needs

---

## 🔍 **SITUATION ANALYSIS**

### **What We Have:**

**File A: `enhanced_simple_server.py`** (Episode 5 - Sep 24, 2025)
- ✅ Template Builder (working, tested, approved)
- ✅ Custom Combo Boxes v2.5
- ✅ Linkages v3.1
- ✅ 17 template API routes
- ✅ Template persistence
- ❌ No chat
- ❌ No dashboard
- ❌ No LLM integration

**File B: `prompt_manager_app.py`** (Current - Oct 11, 2025)
- ✅ Chat interface
- ✅ Dashboard
- ✅ LLM integration (OpenAI)
- ✅ Token tracking
- ✅ Conversation persistence
- ✅ Settings page
- ⚠️ Template builder (incomplete - missing routes)

### **The Challenge:**
Merge A + B without breaking either.

---

## 📐 **STEP 1: DEFINE THE INTERFACE CONTRACT** (15 minutes)

### **Template Builder Service Contract:**

```python
"""
Template Builder Service Interface

This defines the contract between the Template Builder subsystem
and the rest of the Prompt Manager application.
"""

class ITemplateBuilderService:
    """Interface for template builder operations."""
    
    # Page Rendering
    def render_template_builder_page() -> str
    
    # Template Operations
    def parse_template(template_text: str) -> dict
    def generate_dropdowns(template_text: str) -> dict
    def generate_final_prompt(template_text: str, selections: dict) -> str
    
    # Persistence
    def save_template(name: str, data: dict) -> bool
    def load_template(name: str) -> dict
    def list_templates() -> list
    def delete_template(name: str) -> bool
    
    # Custom Combo Box Operations
    def create_custom_combo_boxes(template_text: str) -> dict
    def handle_combo_box_change(combo_box_id: str, new_value: str, combo_boxes: list) -> list
    def generate_prompt_from_combo_boxes(template: str, combo_boxes: list) -> str
```

### **Required Dependencies:**
```python
# In app.config:
- 'CUSTOM_COMBO_INTEGRATION': CustomComboBoxIntegration instance
- 'TEMPLATE_SERVICE': TemplateService instance

# Static assets:
- /static/js/custom-combo-box-working.js (v2.5)
- /static/js/linkage-manager-v3.js (v3.1)
- /static/js/template-storage.js
- /static/css/custom-combo-box.css
```

**Questions for you:**
- Does this contract capture everything the template builder needs?
- Should we add any other methods?

---

## 🧪 **STEP 2: WRITE THE INTEGRATION TEST FIRST** (20 minutes)

### **Test-First Approach:**

**Create:** `tests/test_template_builder_integration_v2.py`

```python
"""
Integration tests for Template Builder in merged app.

These tests verify that the template builder works correctly
when integrated into the main prompt_manager_app.
"""

import pytest
from prompt_manager_app import create_app

@pytest.fixture
def app():
    """Create app instance for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestTemplateBuilderIntegration:
    """Test template builder integration into main app."""
    
    def test_template_builder_page_loads(self, client):
        """RED: Template builder page should load."""
        response = client.get('/template-builder')
        assert response.status_code == 200
        assert b'Template Builder' in response.data
    
    def test_parse_template_route_exists(self, client):
        """RED: Parse template route should exist."""
        response = client.post('/template/parse',
                              json={'template': 'As a [role], I want [action]'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'variables' in data
        assert 'role' in data['variables']
        assert 'action' in data['variables']
    
    def test_save_template_route_exists(self, client):
        """RED: Save template route should exist."""
        response = client.post('/api/templates/save',
                              json={
                                  'name': 'Test',
                                  'description': 'Test template',
                                  'template_text': '[role]',
                                  'combo_box_values': {},
                                  'linkage_data': {}
                              })
        assert response.status_code == 200
    
    def test_chat_still_works_after_integration(self, client):
        """Ensure chat wasn't broken by template integration."""
        response = client.get('/chat')
        assert response.status_code == 200
        assert b'Chat' in response.data
    
    def test_settings_still_works_after_integration(self, client):
        """Ensure settings wasn't broken by template integration."""
        response = client.get('/settings')
        assert response.status_code == 200


class TestAllTemplateRoutes:
    """Verify all 17 template routes exist."""
    
    TEMPLATE_ROUTES = [
        ('/template-builder', 'GET'),
        ('/template/parse', 'POST'),
        ('/template/generate-dropdowns', 'POST'),
        ('/template/update-options', 'POST'),
        ('/template/generate-final', 'POST'),
        ('/template/edit-mode', 'POST'),
        ('/template/generate', 'POST'),
        ('/api/custom-combo-box/create-template', 'POST'),
        ('/api/custom-combo-box/handle-change', 'POST'),
        ('/api/custom-combo-box/generate-prompt', 'POST'),
        ('/api/custom-combo-box/validate-template', 'POST'),
        ('/api/custom-combo-box/available-templates', 'GET'),
        ('/api/custom-combo-box/export-config', 'POST'),
        ('/api/custom-combo-box/import-config', 'POST'),
        ('/api/templates/save', 'POST'),
        ('/api/templates/load/test', 'GET'),
        ('/api/templates/list', 'GET'),
        ('/api/templates/delete/test', 'DELETE'),
        ('/api/templates/exists/test', 'GET'),
    ]
    
    @pytest.mark.parametrize("route,method", TEMPLATE_ROUTES)
    def test_route_exists(self, client, route, method):
        """RED: Each template route should exist and respond."""
        if method == 'GET':
            response = client.get(route)
        elif method == 'POST':
            response = client.post(route, json={})
        elif method == 'DELETE':
            response = client.delete(route)
        
        # Should not be 404 (route exists)
        assert response.status_code != 404, f"Route {method} {route} not found"
```

**Run this test NOW:**
```bash
pytest tests/test_template_builder_integration_v2.py -v
```

**Expected:** ALL tests FAIL (RED) - because routes don't exist yet.

**Questions for you:**
- Should I create and run this test first to establish our baseline?
- Any other test scenarios you want covered?

---

## 🔧 **STEP 3: REFACTOR TO CREATE SPACE** (30 minutes)

### **"Make the Change Easy"**

Before adding template builder routes, we need to ensure there's no conflict.

#### **3A: Audit Current Routes** (10 min)

Check what routes currently exist in `prompt_manager_app.py`:

```bash
# List all registered routes
python -c "
from prompt_manager_app import create_app
app = create_app()
for rule in app.url_map.iter_rules():
    print(f'{rule.methods} {rule.rule}')
" | sort
```

**Look for:**
- Any `/template/*` routes?
- Any `/api/templates/*` routes?
- Any conflicts with what we need to add?

#### **3B: Check Blueprint Names** (5 min)

```python
# Current blueprints in prompt_manager_app.py:
- linkage_bp (from routes.linkage)
- static_bp (from routes.static)
- dashboard_bp (from routes.dashboard)
- prompts_bp (from routes.prompts_api)
```

**Question:** Does `linkage_bp` already have some template routes? If so, we need to either:
- **Option A:** Enhance existing linkage_bp with missing routes
- **Option B:** Create new template_bp and remove linkage_bp
- **Option C:** Rename linkage_bp to template_bp for clarity

#### **3C: Verify Static Assets** (5 min)

Check that JavaScript files exist and are accessible:
```bash
ls -la src/prompt_manager/static/js/custom-combo-box-working.js
ls -la src/prompt_manager/static/js/linkage-manager-v3.js
ls -la src/prompt_manager/static/js/template-storage.js
```

#### **3D: Create Abstraction** (10 min)

If needed, create a facade to isolate template builder:

```python
# src/prompt_manager/business/template_builder_facade.py

class TemplateBuilderFacade:
    """
    Facade for template builder operations.
    Isolates the template builder subsystem from the rest of the app.
    """
    
    def __init__(self, custom_combo_integration, template_service):
        self.custom_combo = custom_combo_integration
        self.template_service = template_service
    
    def parse_template(self, template_text):
        """Parse template and extract variables."""
        import re
        return re.findall(r'\[([^\]]+)\]', template_text)
    
    # ... other methods that wrap the subsystem
```

**Questions for you:**
- Do we need this facade layer?
- Or can we directly use the existing services?

---

## 🔨 **STEP 4: MAKE THE EASY CHANGE** (30 minutes)

### **Now that space is created, add the feature:**

#### **4A: Extract Template Routes** (15 min)

```python
# routes/template_builder_complete.py

"""
Template Builder Routes - Complete Episode 5 Version

Extracted from enhanced_simple_server.py (Sep 24, 2025)
All 17 routes with ZERO modifications to logic.
"""

from flask import Blueprint, current_app, render_template_string, request
import json

template_bp = Blueprint('template_builder', __name__)

# Helper to get services from app config
def get_custom_combo():
    return current_app.config['CUSTOM_COMBO_INTEGRATION']

def get_template_service():
    return current_app.config['TEMPLATE_SERVICE']

# Copy EXACT HTML from enhanced_simple_server.py
TEMPLATE_BUILDER_HTML = """
... (45,000 chars - copy verbatim)
"""

# Copy ALL 17 routes EXACTLY, only changing:
# 1. @app.route → @template_bp.route
# 2. custom_combo_integration → get_custom_combo()
# 3. template_service → get_template_service() (if used)
```

#### **4B: Register Blueprint** (5 min)

```python
# prompt_manager_app.py

def create_app():
    # ... existing code ...
    
    # Register blueprints
    from routes.template_builder_complete import template_bp
    from routes.static import static_bp
    from routes.dashboard import dashboard_bp
    from routes.prompts_api import prompts_bp
    
    app.register_blueprint(template_bp)  # Add template builder
    app.register_blueprint(static_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prompts_bp)
    
    return app
```

#### **4C: Remove Old Incomplete Linkage** (5 min)

```python
# REMOVE this line:
# from routes.linkage import linkage_bp
# app.register_blueprint(linkage_bp)

# REPLACE with:
from routes.template_builder_complete import template_bp
app.register_blueprint(template_bp)
```

#### **4D: Run Tests** (5 min)

```bash
pytest tests/test_template_builder_integration_v2.py -v
```

**Expected:** All tests GREEN ✅

---

## ✅ **STEP 5: VERIFY INTEGRATION** (20 minutes)

### **5A: Start Server**
```bash
python prompt_manager_app.py
```

### **5B: Manual Testing Checklist**

**Template Builder:**
- [ ] Page loads: http://localhost:8000/template-builder
- [ ] Can create combo box
- [ ] Can add options to combo box
- [ ] Can create linkages between combo boxes
- [ ] Can save template
- [ ] Can load template
- [ ] Linkages restore correctly

**Chat Interface:**
- [ ] Page loads: http://localhost:8000/chat
- [ ] Can send message
- [ ] History works
- [ ] Token tracking works
- [ ] All buttons functional

**Settings:**
- [ ] Page loads: http://localhost:8000/settings
- [ ] Can add API key
- [ ] Can set system prompt

### **5C: Run Full Test Suite**
```bash
pytest tests/ -v
```

All existing tests should still pass.

---

## 🎓 **LEARNING OBJECTIVES**

### **What We're Learning:**

1. **Design to Interfaces**
   - Define contracts before implementation
   - Services communicate through well-defined APIs
   - Reduces coupling

2. **Refactor to Open/Closed**
   - Make space in code before adding features
   - Existing code doesn't change when adding new features
   - Open for extension, closed for modification

3. **Test-Driven Integration**
   - Write integration tests FIRST (RED)
   - Implement just enough to pass (GREEN)
   - Refactor for clarity (REFACTOR)

4. **Emergent Design**
   - Design emerges from needs, not upfront planning
   - Refactor continuously as understanding grows
   - Simple solutions first, complexity only when needed

---

## ⚠️ **POTENTIAL ISSUES & SOLUTIONS**

### **Issue 1: Route Conflicts**
**Symptom:** Same route defined in multiple blueprints  
**Detection:** Flask will warn on startup  
**Solution:** Remove duplicate from old blueprint

### **Issue 2: Missing Dependencies**
**Symptom:** `AttributeError` or `KeyError` accessing app.config  
**Detection:** Server crashes on route access  
**Solution:** Ensure all services initialized in create_app()

### **Issue 3: JavaScript Not Loading**
**Symptom:** Template builder loads but combo boxes don't work  
**Detection:** Browser console shows 404 for .js files  
**Solution:** Verify static_folder configured correctly

### **Issue 4: Template Service Conflicts**
**Symptom:** Can't save/load templates  
**Detection:** API returns 500 errors  
**Solution:** Ensure TemplateService uses correct file path

---

## 📊 **SUCCESS CRITERIA**

### **Integration is successful when:**
1. ✅ All 17 template routes respond (not 404)
2. ✅ Template builder page loads and renders
3. ✅ Custom combo boxes work (add, edit, delete)
4. ✅ Linkages work (cascading updates)
5. ✅ Templates save and load correctly
6. ✅ Chat interface still works
7. ✅ Dashboard still works
8. ✅ Settings still works
9. ✅ All existing tests pass
10. ✅ New integration tests pass

---

## 🎬 **EXECUTION TIMELINE**

### **Phase 1: Preparation** (30 min)
- Define contract (this document)
- Write integration tests (RED)
- Audit current routes
- Identify conflicts

### **Phase 2: Refactoring** (30 min)
- Create space in code
- Remove incomplete linkage_bp if needed
- Ensure services available
- Prepare for new blueprint

### **Phase 3: Integration** (30 min)
- Extract template routes to new blueprint
- Minimal changes (only Blueprint conversion)
- Register in main app
- Run tests (GREEN)

### **Phase 4: Verification** (30 min)
- Manual testing all features
- Full test suite
- Fix any issues
- Document any learnings

**Total: 2 hours**

---

## 🤔 **QUESTIONS FOR YOU**

### **Before I Start:**

1. **Test Strategy:**
   - Should I write the integration tests FIRST (true TDD)?
   - Or extract routes first, then test?
   - **My recommendation:** Tests first (RED), then implement (GREEN)

2. **Blueprint Naming:**
   - Keep name `linkage_bp` or rename to `template_bp`?
   - **My recommendation:** Rename to `template_bp` for clarity

3. **Old Linkage File:**
   - Keep `routes/linkage.py` as backup?
   - Or delete and replace completely?
   - **My recommendation:** Rename to `linkage_old.py`, create new clean file

4. **Commit Strategy:**
   - Commit after each step?
   - Or one big commit at end?
   - **My recommendation:** Commit after each phase (4 commits)

5. **If Something Breaks:**
   - Stop immediately and ask you?
   - Try to fix and document?
   - **My recommendation:** Stop and ask

---

## 📝 **DOCUMENTATION STRATEGY**

### **As We Work:**
Document each decision and why:
- Why we chose this approach
- What alternatives we considered
- What we learned
- What worked / didn't work

This becomes the content for the YouTube video!

---

## 🎥 **VIDEO CONTENT CAPTURE**

### **Record These Moments:**
1. Writing the integration test (RED)
2. Extracting the template routes
3. First attempt to start server
4. Tests turning GREEN
5. Manual testing showing both features working
6. Reflection on what we learned

---

**Ready to proceed? Please answer the 5 questions above and I'll execute methodically.** 🚀

