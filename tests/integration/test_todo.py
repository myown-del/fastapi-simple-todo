import pytest
from app.models.todo import List, Item


@pytest.mark.asyncio
async def test_create_list_saves_to_database(client, registered_user):
    email, password = registered_user
    
    list_data = {"list_name": "List 1"}
    response = client.post(
        "/api/v1/list",
        json=list_data,
        auth=(email, password)
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["list_name"] == "List 1"
    assert "list_id" in response_data
    list_id = response_data["list_id"]
    
    list_in_db = await List.filter(id=list_id).first()
    assert list_in_db is not None
    assert list_in_db.name == "List 1"
    assert list_in_db.id == list_id


@pytest.mark.asyncio
async def test_view_list_returns_database_items(client, registered_user):
    email, password = registered_user
    
    list_obj = await List.create(name="List 1")
    list_obj = await List.create(name="List 1")
    
    item1 = await Item.create(list_id=list_obj.id, name="Item 1")
    item2 = await Item.create(list_id=list_obj.id, name="Item 2")
    
    response = client.get(
        f"/api/v1/list/{list_obj.id}",
        auth=(email, password)
    )
    
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    
    item_names = [item["todo_item_name"] for item in items]
    assert "Item 1" in item_names
    assert "Item 2" in item_names
    
    item_ids = [item["todo_item_id"] for item in items]
    assert item1.id in item_ids
    assert item2.id in item_ids


@pytest.mark.asyncio
async def test_add_item_creates_in_database(client, registered_user):
    email, password = registered_user
    
    list_obj = await List.create(name="List 1")
    list_obj = await List.create(name="List 1")
    
    item_data = {"todo_item_name": "Item 1"}
    response = client.post(
        f"/api/v1/list/{list_obj.id}",
        json=item_data,
        auth=(email, password)
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["todo_item_name"] == "Item 1"
    assert "todo_item_id" in response_data
    item_id = response_data["todo_item_id"]
    
    item_in_db = await Item.filter(id=item_id, list_id=list_obj.id).first()
    assert item_in_db is not None
    assert item_in_db.name == "Item 1"
    assert item_in_db.list_id == list_obj.id


@pytest.mark.asyncio
async def test_update_item_modifies_database(client, registered_user):
    email, password = registered_user
    
    list_obj = await List.create(name="List 1")
    list_obj = await List.create(name="List 1")
    item_obj = await Item.create(list_id=list_obj.id, name="Item 1")
    
    updated_data = {"todo_item_name": "Item 2"}
    response = client.put(
        f"/api/v1/list/{list_obj.id}/{item_obj.id}",
        json=updated_data,
        auth=(email, password)
    )
    
    assert response.status_code == 204
    
    item_in_db = await Item.filter(id=item_obj.id).first()
    assert item_in_db is not None
    assert item_in_db.name == "Item 2"
    assert item_in_db.name != "Item 1"


@pytest.mark.asyncio
async def test_delete_item_removes_from_database(client, registered_user):
    email, password = registered_user
    
    list_obj = await List.create(name="List 1")
    list_obj = await List.create(name="List 1")
    item1 = await Item.create(list_id=list_obj.id, name="Item 1")
    item2 = await Item.create(list_id=list_obj.id, name="Item 2")
    
    response = client.delete(
        f"/api/v1/list/{list_obj.id}/{item2.id}",
        auth=(email, password)
    )
    
    assert response.status_code == 204
    
    deleted_item = await Item.filter(id=item2.id).first()
    assert deleted_item is None
    
    remaining_item = await Item.filter(id=item1.id).first()
    assert remaining_item is not None
    assert remaining_item.name == "Item 1"


@pytest.mark.asyncio
async def test_delete_list_removes_list_and_items_from_database(client, registered_user):
    email, password = registered_user
    
    list_obj = await List.create(name="List 1")
    list_obj = await List.create(name="List 1")
    item1 = await Item.create(list_id=list_obj.id, name="Item 1")
    item2 = await Item.create(list_id=list_obj.id, name="Item 2")
    item3 = await Item.create(list_id=list_obj.id, name="Item 3")
    
    items_before = await Item.filter(list_id=list_obj.id).count()
    assert items_before == 3
    
    response = client.delete(
        f"/api/v1/list/{list_obj.id}",
        auth=(email, password)
    )
    
    assert response.status_code == 204
    
    list_in_db = await List.filter(id=list_obj.id).first()
    assert list_in_db is None
    
    items_after = await Item.filter(list_id=list_obj.id).count()
    assert items_after == 0
    
    for item_id in [item1.id, item2.id, item3.id]:
        item = await Item.filter(id=item_id).first()
        assert item is None
