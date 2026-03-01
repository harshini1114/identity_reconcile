import requests

BASE_URL = "http://127.0.0.1:5000"


# Test: missing both email and phone number
def test_identify_missing_fields():
    payload = {}
    response = requests.post(f"{BASE_URL}/identify", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


# Test: invalid JSON
def test_identify_invalid_json():
    response = requests.post(f"{BASE_URL}/identify", data="not a json")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


# Test: valid email and phone number
def test_identify_valid_email_and_phone():
    response = requests.post(f"{BASE_URL}/reset")
    assert response.status_code == 200

    payload = {"email": "lorraine@hillvalley.edu", "phoneNumber": "123456"}
    response = requests.post(f"{BASE_URL}/identify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    results = data["contacts"]
    assert results["emails"][0] == "lorraine@hillvalley.edu"
    assert results["phoneNumbers"][0] == "123456"
    assert results["primaryContactId"] == 1
    assert len(results["secondaryContactIds"]) == 0

    payload = {"email": "lorraine@hillvalley.edu", "phoneNumber": None}
    response = requests.post(f"{BASE_URL}/identify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    results = data["contacts"]
    assert results["emails"][0] == "lorraine@hillvalley.edu"
    assert results["phoneNumbers"][0] == "123456"
    assert results["primaryContactId"] == 1
    assert len(results["secondaryContactIds"]) == 0

    payload = {"email": None, "phoneNumber": "123456"}
    response = requests.post(f"{BASE_URL}/identify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    results = data["contacts"]
    assert results["emails"][0] == "lorraine@hillvalley.edu"
    assert results["phoneNumbers"][0] == "123456"
    assert results["primaryContactId"] == 1
    assert len(results["secondaryContactIds"]) == 0

    payload = {"email": "mcfly@hillvalley.edu", "phoneNumber": "123456"}
    response = requests.post(f"{BASE_URL}/identify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    results = data["contacts"]
    assert len(results["secondaryContactIds"]) == 1
    assert results["secondaryContactIds"][0] == 2
    assert len(results["emails"]) == 2
    assert len(results["phoneNumbers"]) == 1
    assert results["primaryContactId"] == 1

    payload = {"email": None, "phoneNumber": "123456"}
    response = requests.post(f"{BASE_URL}/identify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    results = data["contacts"]
    assert len(results["secondaryContactIds"]) == 1
    assert results["secondaryContactIds"][0] == 2
    assert len(results["emails"]) == 2
    assert len(results["phoneNumbers"]) == 1
    assert results["primaryContactId"] == 1

    response = requests.post(f"{BASE_URL}/reset")
    assert response.status_code == 200


if __name__ == "__main__":
    test_identify_missing_fields()
    test_identify_invalid_json()
    test_identify_valid_email_and_phone()
    print("All tests passed!")
