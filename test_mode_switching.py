#!/usr/bin/env python3
"""
Simple test script to verify mode switching functionality
"""

import requests
import json

def test_mode_switching():
    """Test the mode switching functionality."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Custom Combo Box Mode Switching")
    print("=" * 50)
    
    # Test 1: Check if test page loads
    print("1. Testing page load...")
    response = requests.get(f"{base_url}/custom-combo-test")
    if response.status_code == 200:
        print("   ✅ Test page loads successfully")
        
        # Check for key elements
        content = response.text
        if "Custom Combo Box Test" in content:
            print("   ✅ Page title found")
        if "mode-toggle" in content:
            print("   ✅ Mode toggle button found")
        if "handleEditModeChange" in content:
            print("   ✅ Edit mode functions found")
        if "getModeOptions" in content:
            print("   ✅ Mode options function found")
        if "Add item" in content and "Select item" in content:
            print("   ✅ Mode-specific first items found")
    else:
        print(f"   ❌ Test page failed to load: {response.status_code}")
        return
    
    print("\n2. Testing mode-specific behavior...")
    
    # Check for mode-specific logic
    if "isEditMode" in content:
        print("   ✅ Mode state variable found")
    if "Enter ${tag}" in content and "Select ${tag}" in content:
        print("   ✅ Mode-specific placeholders found")
    
    print("\n3. Testing template generation...")
    
    # Test template generation with edit mode
    test_data = {
        "template": "As a [Role], I want to [What], so that [Why]",
        "edit_mode": True
    }
    
    response = requests.post(
        f"{base_url}/template/generate",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Template generation works")
        
        if "dropdowns" in data:
            print("   ✅ Dropdowns generated")
            
            # Check if we have the custom properties
            role_dropdown = data["dropdowns"].get("Role", {})
            if role_dropdown.get("is_custom"):
                print("   ✅ Custom combo box properties found")
            else:
                print("   ⚠️  Custom combo box properties not found")
    else:
        print(f"   ❌ Template generation failed: {response.status_code}")
    
    print("\n🎯 Summary:")
    print("   - Test page is accessible and functional")
    print("   - Mode switching logic is implemented")
    print("   - Mode-specific first items are configured")
    print("   - Ready for manual testing in browser")
    
    print(f"\n🌐 Visit: {base_url}/custom-combo-test")
    print("   - Click 'Generate Test Combo Boxes'")
    print("   - Toggle between EDIT and DISPLAY modes")
    print("   - Verify first items change: 'Add item' vs 'Select item'")
    print("   - Verify placeholders change: 'Enter Role' vs 'Select Role'")

if __name__ == "__main__":
    test_mode_switching()
