def get_jwt(client, mobile):
    client.post("/auth/signup", json={"mobile": mobile})
    resp = client.post("/auth/send-otp", json={"mobile": mobile})
    otp = resp.json()["otp"]
    resp = client.post("/auth/verify-otp", json={"mobile": mobile, "otp": otp})
    return resp.json()["token"]

def test_subscription_status(client):
    mobile = "+1234567877"
    token = get_jwt(client, mobile)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/subscription/status", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["tier"] == "basic" 