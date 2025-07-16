def test_signup_and_otp(client):
    mobile = "+1234567899"
    # Signup
    resp = client.post("/auth/signup", json={"mobile": mobile})
    assert resp.status_code == 200
    # Send OTP
    resp = client.post("/auth/send-otp", json={"mobile": mobile})
    assert resp.status_code == 200
    otp = resp.json()["otp"]
    # Verify OTP
    resp = client.post("/auth/verify-otp", json={"mobile": mobile, "otp": otp})
    assert resp.status_code == 200
    assert "token" in resp.json() 