def setup_catalog(client):
    category = client.post("/api/v1/categories", json={"name": "Regulators"})
    assert category.status_code == 201
    member = client.post("/api/v1/members", json={
        "first_name": "Alex", "last_name": "Diver"
    })
    assert member.status_code == 201
    item = client.post("/api/v1/equipment", json={
        "name": "Club regulator", "category_id": category.json()["id"]
    })
    assert item.status_code == 201
    return member.json(), item.json()


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_create_and_list_equipment(client):
    _, item = setup_catalog(client)
    assert item["status"] == "AVAILABLE"
    assert item["uuid"]
    assert len(client.get("/api/v1/equipment").json()) == 1


def test_checkout_and_return(client):
    member, item = setup_catalog(client)
    checkout = client.post("/api/v1/loans/checkout", json={
        "equipment_uuid": item["uuid"], "member_id": member["id"]
    })
    assert checkout.status_code == 201
    assert client.get("/api/v1/equipment").json()[0]["status"] == "BORROWED"

    duplicate = client.post("/api/v1/loans/checkout", json={
        "equipment_uuid": item["uuid"], "member_id": member["id"]
    })
    assert duplicate.status_code == 409

    returned = client.post("/api/v1/loans/return", json={
        "equipment_uuid": item["uuid"], "note": "Returned in good condition"
    })
    assert returned.status_code == 200
    assert returned.json()["returned_at"] is not None
    assert client.get("/api/v1/equipment").json()[0]["status"] == "AVAILABLE"
