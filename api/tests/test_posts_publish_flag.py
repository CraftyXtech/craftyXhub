import json
import pytest


@pytest.mark.asyncio
async def test_create_post_published_immediately(client_author):
    data = {
        "title": "My First Post",
        "content": "<p>Hello world</p>",
        "is_published": "true",
        "content_blocks": json.dumps({"blocks": [{"type": "paragraph", "text": "Hello"}]}),
    }

    response = await client_author.post("/v1/posts/", data=data)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["is_published"] is True
    assert body["published_at"] is not None
    assert body["slug"]


@pytest.mark.asyncio
async def test_update_post_toggle_publish(client_author):
    # create draft
    create = await client_author.post("/v1/posts/", data={
        "title": "Draft Post",
        "content": "<p>Draft</p>",
        "is_published": "false",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    # publish via update
    resp = await client_author.put(f"/v1/posts/{post['uuid']}", data={
        "is_published": "true"
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["is_published"] is True
    assert body["published_at"] is not None

    # unpublish via update
    resp2 = await client_author.put(f"/v1/posts/{post['uuid']}", data={
        "is_published": "false"
    })
    assert resp2.status_code == 200, resp2.text
    body2 = resp2.json()
    assert body2["is_published"] is False
    assert body2["published_at"] is None


@pytest.mark.asyncio
async def test_publish_endpoint_still_works(client_author):
    create = await client_author.post("/v1/posts/", data={
        "title": "Draft 2",
        "content": "<p>Draft 2</p>",
        "is_published": "false",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    # publish via endpoint
    resp = await client_author.put(f"/v1/posts/{post['uuid']}/publish")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["is_published"] is True
    assert body["published_at"] is not None


@pytest.mark.asyncio
async def test_admin_flag_unpublishes(client_admin, client_author):
    # author creates published post
    create = await client_author.post("/v1/posts/", data={
        "title": "Flaggable",
        "content": "<p>Flag me</p>",
        "is_published": "true",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    # admin flags it
    flag = await client_admin.put(f"/v1/posts/{post['uuid']}/flag", params={"flag": "true"})
    assert flag.status_code == 200, flag.text
    flagged = flag.json()
    assert flagged["is_flagged"] is True
    assert flagged["is_published"] is False
    assert flagged["published_at"] is None


@pytest.mark.asyncio
async def test_delete_permissions(client_author, client_admin):
    # author creates
    create = await client_author.post("/v1/posts/", data={
        "title": "Delete Me",
        "content": "<p>bye</p>",
        "is_published": "true",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    # author deletes
    del_resp = await client_author.delete(f"/v1/posts/{post['uuid']}")
    assert del_resp.status_code == 204, del_resp.text

    # create another and let admin delete (author fixture still same user)
    create2 = await client_author.post("/v1/posts/", data={
        "title": "Delete Me 2",
        "content": "<p>bye2</p>",
        "is_published": "true",
    })
    assert create2.status_code == 201, create2.text
    post2 = create2.json()

    del_by_admin = await client_admin.delete(f"/v1/posts/{post2['uuid']}")
    assert del_by_admin.status_code == 204, del_by_admin.text
