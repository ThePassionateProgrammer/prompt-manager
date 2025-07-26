def test_concatenation():
    assert "Hello, " + "world!" == "Hello, world!"

def test_uppercase():
    assert "ai is great".upper() == "AI IS GREAT"

def test_strip_whitespace():
    assert "  padded  ".strip() == "padded"