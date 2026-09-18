from app import generate_secure_password, estimate_crack_time

def test_generate_secure_password():
    pwd = generate_secure_password(16)
    assert len(pwd) == 16
    assert any(c.islower() for c in pwd)
    assert any(c.isupper() for c in pwd)
    assert any(c.isdigit() for c in pwd)

def test_generate_secure_password_custom_length():
    # Verify custom length parameter works correctly
    pwd = generate_secure_password(24)
    assert len(pwd) == 24

def test_estimate_crack_time():
    score, text = estimate_crack_time("weak")
    assert score > 0
    assert "❌" in text

def test_estimate_crack_time_empty():
    # Verify empty string edge case returns safe default values
    score, text = estimate_crack_time("")
    assert score == 0.0
    assert text == ""

def test_estimate_crack_time_strong():
    # Verify a robust password hits high security thresholds
    score, text = estimate_crack_time("Tr0ub4d0ur&9#XyZ!pQ")
    assert score == 1.0
    assert "+ de 1000 ans" in text