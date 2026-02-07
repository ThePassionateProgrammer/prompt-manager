# Component Development Checklist
**For building and integrating isolated components**

---

## Phase 1: Design the Interface

### ✅ Before Writing Any Code:

- [ ] **Define the contract**
  - What does this component do?
  - What are its inputs?
  - What are its outputs?
  - What are its dependencies?

- [ ] **Write examples**
  - Example usage code
  - Expected behavior
  - Edge cases

- [ ] **Document integration points**
  - How will it connect to the system?
  - What data flows in/out?
  - What events does it emit/consume?

---

## Phase 2: Build in Isolation

### ✅ Create Test Harness:

- [ ] **Standalone file** (separate from main system)
- [ ] **Minimal dependencies** (mock what you need)
- [ ] **Fast feedback loop** (run tests quickly)

### ✅ Build the Component:

- [ ] **Start with simplest case**
- [ ] **Add features incrementally**
- [ ] **Test each feature before next**
- [ ] **Keep interface stable**

### ✅ Verify Completely:

- [ ] **All features work**
- [ ] **All edge cases handled**
- [ ] **No console errors**
- [ ] **Visual inspection complete**
- [ ] **Performance acceptable**

---

## Phase 3: Prepare for Extraction

### ✅ Before Copying Anything:

- [ ] **Record file sizes** (note bytes, not lines)
  ```bash
  wc -c test_harness_file.html  # Note this number!
  ```

- [ ] **Screenshot the working version**
  - Take photos of UI
  - Note any quirks
  - Document known issues

- [ ] **Create extraction branch**
  ```bash
  git checkout -b extract-component-name
  ```

- [ ] **Commit working state**
  ```bash
  git add . && git commit -m "Before extraction: component working in test harness"
  ```

---

## Phase 4: Extract Component

### ✅ Extraction Process:

- [ ] **Copy component code**
- [ ] **Verify file size immediately**
  ```bash
  # If source is 45,670 bytes, target should be similar
  wc -c source.html target.html
  diff <(wc -c source.html) <(wc -c target.html)
  ```

- [ ] **Visual diff check**
  ```bash
  # Compare files visually
  diff source.html target.html | head -50
  # Or use a GUI diff tool
  ```

- [ ] **Test in isolation again**
  - Load extracted version
  - Verify all features still work
  - Check console for errors

### ✅ If Extraction Looks Wrong:

- [ ] **Stop immediately**
- [ ] **Compare file sizes**
- [ ] **Check for truncation**
- [ ] **Re-extract if needed**
- [ ] **Don't proceed until verified**

---

## Phase 5: Integration

### ✅ Before Integrating:

- [ ] **Review integration points** (from Phase 1)
- [ ] **Identify what needs to change** (routes, imports, etc.)
- [ ] **Make list of connection steps**

### ✅ Integration Process:

- [ ] **Connect one thing at a time**
  - Add route
  - Test route loads
  - Add next connection
  - Test again

- [ ] **After each connection:**
  ```bash
  # Does it boot?
  python app.py
  curl http://localhost:8000/component-route
  ```

### ✅ Smoke Tests:

- [ ] **Component page loads**
- [ ] **No console errors**
- [ ] **Basic functionality works**
- [ ] **Styling looks right**
- [ ] **Interactions respond**

---

## Phase 6: Verification

### ✅ Comprehensive Testing:

- [ ] **All features work in integrated system**
- [ ] **No regressions in existing features**
- [ ] **Performance still acceptable**
- [ ] **Works in all target browsers** (if applicable)

### ✅ Side-by-Side Comparison:

- [ ] **Open test harness version**
- [ ] **Open integrated version**
- [ ] **Compare visually**
- [ ] **Test same actions in both**
- [ ] **Verify identical behavior**

### ✅ Final Checks:

- [ ] **Run full test suite**
  ```bash
  pytest
  ```

- [ ] **Manual testing of integrated feature**
- [ ] **Check for TODO comments**
- [ ] **Review code quality**

---

## Phase 7: Documentation & Commit

### ✅ Document:

- [ ] **Update README** (if public interface changed)
- [ ] **Add component docs** (how to use)
- [ ] **Note integration points** (for future reference)
- [ ] **Record any quirks** (things that surprised you)

### ✅ Commit:

- [ ] **Meaningful commit message**
  ```bash
  git add -A
  git commit -m "integrate: Add ComponentName to main system
  
  - Extracted from test harness
  - Verified file integrity (45,670 bytes → 45,668 bytes)
  - All features working
  - Smoke tested integration
  - Full test suite passing"
  ```

- [ ] **Tag if significant**
  ```bash
  git tag -a v1.x-component-integrated -m "ComponentName integrated"
  ```

---

## 🚨 Red Flags - Stop and Investigate

**If you see any of these, STOP:**

- ❌ **File size dramatically different** (>5% change)
- ❌ **Console errors after extraction**
- ❌ **Visual differences between test harness and integrated**
- ❌ **Features work in harness but not integrated**
- ❌ **Integration requires major changes to component**
- ❌ **"It should work" without actually testing**

**When you see a red flag:**
1. Don't proceed
2. Compare with working version
3. Check file integrity
4. Ask: "What did I assume that might be wrong?"
5. Fix the issue before continuing

---

## 📋 Quick Checklist (Print This)

**Before Extraction:**
- [ ] Working in test harness? ✓
- [ ] File size noted? _________
- [ ] Screenshots taken? ✓
- [ ] Committed? ✓

**During Extraction:**
- [ ] File size verified? _________ (should match)
- [ ] Visual diff clean? ✓
- [ ] Still works isolated? ✓

**During Integration:**
- [ ] Connects one step at a time? ✓
- [ ] Smoke test after each step? ✓
- [ ] Side-by-side comparison? ✓

**Before Committing:**
- [ ] Full test suite passes? ✓
- [ ] Manual testing complete? ✓
- [ ] Documentation updated? ✓

---

## 🎓 Lessons from Custom Combo Box

**What we learned:**
1. **File size is a canary** - Check it immediately
2. **Don't assume, verify** - "It should work" is dangerous
3. **Smoke test after integration** - Load the page!
4. **Compare with working version** - Side-by-side catches issues
5. **Root cause first** - Git archaeology wastes time; compare files first

**Time saved with this checklist:**
- Template builder issue: 6 hours debugging → would have been 5 minutes
- Future integrations: Catch issues in seconds, not weeks

---

## 🤝 How David Can Support Claude's Best Work

**During component development:**
1. **Review the interface design** before I build
2. **Check in after extraction** - "Did you verify file sizes?"
3. **Insist on smoke tests** - "Show me it loads"
4. **Pair on integration** - More eyes catch issues

**When issues arise:**
1. **Ask for root cause analysis first** - Not solutions
2. **"Compare with the working version"** - Before git archaeology
3. **"What's the simplest way to verify this?"** - Tests > assumptions

**General collaboration:**
1. **Catch me when I rush** - "Slow down, verify this"
2. **Ask clarifying questions** - Forces me to think clearly
3. **Challenge assumptions** - "How do you know that works?"
4. **Celebrate good process** - "Great! You checked file sizes"

---

*Use this checklist for every component extraction. 5 minutes of verification saves hours of debugging.*

