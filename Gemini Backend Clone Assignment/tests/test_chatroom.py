def get_jwt(client, mobile):
    client.post("/auth/signup", json={"mobile": mobile})
    resp = client.post("/auth/send-otp", json={"mobile": mobile})
    otp = resp.json()["otp"]
    resp = client.post("/auth/verify-otp", json={"mobile": mobile, "otp": otp})
    return resp.json()["token"]

def test_create_and_list_chatroom(client):
    mobile = "+1234567888"
    token = get_jwt(client, mobile)
    headers = {"Authorization": f"Bearer {token}"}
    # Create chatroom
    resp = client.post("/chatroom", json={"name": "Test Room"}, headers=headers)
    assert resp.status_code == 200
    # List chatrooms
    resp = client.get("/chatroom", headers=headers)
    assert resp.status_code == 200
    assert any(c["name"] == "Test Room" for c in resp.json()["chatrooms"]) 