#!/usr/bin/env python3
"""
Phase 6 Testing: Image Support (Vision)
Tests for image upload, processing, display, and Claude vision integration
"""

import sys
import os
from pathlib import Path
import base64
from io import BytesIO

# Test counter
tests_passed = 0
tests_failed = 0

def test(name):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed
            try:
                func()
                print(f"✅ {name}")
                tests_passed += 1
            except AssertionError as e:
                print(f"❌ {name}: {e}")
                tests_failed += 1
            except Exception as e:
                print(f"❌ {name}: Unexpected error: {e}")
                tests_failed += 1
        return wrapper
    return decorator


print("=" * 70)
print("PHASE 6 TESTING: Image Support (Vision)")
print("=" * 70)
print()

# Test 1: Image processing functions exist
@test("1. Image processing functions exist")
def test_image_functions():
    import main
    assert hasattr(main, 'encode_image_to_base64'), "encode_image_to_base64 missing"
    assert hasattr(main, 'get_media_type'), "get_media_type missing"
    assert hasattr(main, 'create_image_content'), "create_image_content missing"
    assert hasattr(main, 'validate_image_size'), "validate_image_size missing"

test_image_functions()


# Test 2: Base64 encoding
@test("2. Base64 encoding works")
def test_base64_encoding():
    from main import encode_image_to_base64

    test_bytes = b"Hello, World!"
    encoded = encode_image_to_base64(test_bytes)

    assert isinstance(encoded, str), "Should return string"
    assert len(encoded) > 0, "Should not be empty"

    # Verify it's valid base64
    decoded = base64.b64decode(encoded)
    assert decoded == test_bytes, "Encoding/decoding should match"

test_base64_encoding()


# Test 3: Media type detection
@test("3. Media type detection works")
def test_media_type():
    from main import get_media_type

    assert get_media_type("image.jpg") == "image/jpeg"
    assert get_media_type("photo.jpeg") == "image/jpeg"
    assert get_media_type("picture.png") == "image/png"
    assert get_media_type("graphic.webp") == "image/webp"
    assert get_media_type("animation.gif") == "image/gif"
    assert get_media_type("IMAGE.JPG") == "image/jpeg"  # Case insensitive

test_media_type()


# Test 4: Image content creation
@test("4. Image content creation works")
def test_image_content():
    from main import create_image_content

    test_bytes = b"fake_image_data"
    media_type = "image/jpeg"

    content = create_image_content(test_bytes, media_type)

    assert content["type"] == "image", "Type should be 'image'"
    assert "source" in content, "Should have 'source' field"
    assert content["source"]["type"] == "base64", "Source type should be 'base64'"
    assert content["source"]["media_type"] == media_type, "Media type should match"
    assert "data" in content["source"], "Should have 'data' field"

test_image_content()


# Test 5: Image size validation
@test("5. Image size validation works")
def test_image_validation():
    from main import validate_image_size

    # Small image (valid)
    small_image = b"x" * 1000  # 1KB
    is_valid, error = validate_image_size(small_image)
    assert is_valid, "Small image should be valid"
    assert error == "", "Should not have error message"

    # Large image (invalid - over 5MB after base64)
    large_image = b"x" * (5 * 1024 * 1024)  # 5MB raw = ~6.67MB base64
    is_valid, error = validate_image_size(large_image)
    assert not is_valid, "Large image should be invalid"
    assert "too large" in error.lower(), "Should have size error message"

test_image_validation()


# Test 6: Model names updated with vision indicators
@test("6. Model names indicate vision support")
def test_model_names():
    with open('main.py', 'r') as f:
        content = f.read()

    # Check for vision indicators in model names
    assert 'Vision' in content, "Should mention Vision in model names"
    assert 'Opus 4.5 (Best + Vision)' in content, "Opus should indicate vision"
    assert 'Sonnet 4.5 (Balanced + Vision)' in content, "Sonnet should indicate vision"
    assert 'Haiku 3.5 (Fastest + Vision)' in content, "Haiku should indicate vision"

test_model_names()


# Test 7: Image upload UI components
@test("7. Image upload UI exists")
def test_upload_ui():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'file_uploader' in content, "Should have file uploader"
    assert 'Upload images' in content, "Should have upload label"
    assert 'jpg' in content.lower(), "Should support JPG"
    assert 'png' in content.lower(), "Should support PNG"
    assert 'webp' in content.lower(), "Should support WebP"
    assert 'gif' in content.lower(), "Should support GIF"

test_upload_ui()


# Test 8: Process message handles images
@test("8. process_message accepts images parameter")
def test_process_message_signature():
    import inspect
    from main import process_message

    sig = inspect.signature(process_message)
    params = list(sig.parameters.keys())

    assert 'user_message' in params, "Should have user_message parameter"
    assert 'uploaded_images' in params, "Should have uploaded_images parameter"

test_process_message_signature()


# Test 9: Render message handles array content
@test("9. render_message handles array content")
def test_render_message():
    with open('main.py', 'r') as f:
        content = f.read()

    # Check for array content handling
    assert 'isinstance(content, list)' in content, "Should check for list content"
    assert 'item.get("type") == "text"' in content, "Should handle text type"
    assert 'item.get("type") == "image"' in content, "Should handle image type"

test_render_message()


# Test 10: Message converter handles images
@test("10. Message converter supports images")
def test_message_converter():
    with open('core/message_converter.py', 'r') as f:
        content = f.read()

    # Check that it handles content arrays
    assert 'isinstance(content, list)' in content, "Should handle content arrays"
    assert 'convert_image_format' in content, "Should have image format conversion"

test_message_converter()


# Test 11: Session state includes uploaded_images
@test("11. Session state initialized for images")
def test_session_state():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'uploaded_images' in content, "Should initialize uploaded_images in session state"

test_session_state()


# Test 12: Caption updated with vision support
@test("12. App caption mentions vision")
def test_caption():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'Vision' in content, "Caption should mention vision support"
    assert '👁️' in content or '📸' in content, "Should have vision emoji"

test_caption()


# Test 13: Image preview in UI
@test("13. Image preview functionality")
def test_image_preview():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'st.image' in content, "Should display images"
    assert 'image(s) ready to send' in content, "Should show count of images"
    assert 'cols' in content or 'columns' in content, "Should use columns for preview"

test_image_preview()


# Test 14: PIL import for image handling
@test("14. PIL/Pillow imported")
def test_pil_import():
    import main
    assert hasattr(main, 'Image'), "Should import PIL.Image"

test_pil_import()


# Test 15: Base64 import
@test("15. Base64 module imported")
def test_base64_import():
    import main
    assert hasattr(main, 'base64'), "Should import base64 module"

test_base64_import()


# Summary
print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print(f"Total: {tests_passed + tests_failed}")
print()

if tests_failed == 0:
    print("🎉 All Phase 6 tests passed!")
    print()
    print("Phase 6 Features Verified:")
    print("  ✅ Image processing functions (encode, validate, create)")
    print("  ✅ Media type detection (jpg, png, webp, gif)")
    print("  ✅ Image size validation (5MB limit)")
    print("  ✅ Image upload UI with previews")
    print("  ✅ Message display with images")
    print("  ✅ Vision indicators in model names")
    print("  ✅ Claude-formatted image content")
    print()
    print("Ready to test with actual Claude API!")
    print()
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Please review the errors above.")
    sys.exit(1)
