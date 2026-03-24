import json
import pytest
from uuid import uuid4

VALID_EXCERPT = (
    "A publish-ready summary that captures the full article, highlights the "
    "main takeaway, and gives readers a clear reason to keep reading on the site."
)


@pytest.mark.asyncio
async def test_create_post_published_immediately(client_author):
    data = {
        "title": "My First Post",
        "content": "<p>Hello world</p>",
        "excerpt": VALID_EXCERPT,
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
async def test_create_draft_allows_missing_excerpt(client_author):
    response = await client_author.post("/v1/posts/", data={
        "title": "Draft Without Excerpt",
        "content": "<p>Draft body</p>",
        "is_published": "false",
    })

    assert response.status_code == 201, response.text
    assert response.json()["excerpt"] is None


@pytest.mark.asyncio
async def test_create_post_published_immediately_requires_excerpt(client_author):
    response = await client_author.post("/v1/posts/", data={
        "title": "Published Without Excerpt",
        "content": "<p>Hello world</p>",
        "is_published": "true",
    })

    assert response.status_code == 422, response.text
    assert response.json()["detail"] == "Excerpt is required before publishing."


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
        "excerpt": VALID_EXCERPT,
        "is_published": "true",
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
        "excerpt": VALID_EXCERPT,
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
async def test_publish_endpoint_rejects_missing_excerpt(client_author):
    create = await client_author.post("/v1/posts/", data={
        "title": "Draft Missing Excerpt",
        "content": "<p>This draft does not have an excerpt yet.</p>",
        "is_published": "false",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    resp = await client_author.put(f"/v1/posts/{post['uuid']}/publish")
    assert resp.status_code == 422, resp.text
    assert resp.json()["detail"] == "Excerpt is required before publishing."


@pytest.mark.asyncio
async def test_publish_rejects_opening_paragraph_snippet(client_author):
    content = (
        "<p>The first paragraph is deliberately long so it looks like the old "
        "excerpt generator would have used it as a cheap summary instead of a "
        "real editorial summary for the whole piece.</p>"
        "<p>The second paragraph adds the broader context that a proper excerpt "
        "should capture before the article is published.</p>"
    )
    legacy_excerpt = (
        "The first paragraph is deliberately long so it looks like the old "
        "excerpt generator would have used it as a cheap summary instead of a real editorial summary for the whole piece."
    )

    response = await client_author.post("/v1/posts/", data={
        "title": "Reject Legacy Excerpt",
        "content": content,
        "excerpt": legacy_excerpt[:150].strip() + "...",
        "is_published": "true",
    })

    assert response.status_code == 422, response.text
    assert "Opening-paragraph snippets are not allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_flag_unpublishes(client_admin, client_author):
    # author creates published post
    create = await client_author.post("/v1/posts/", data={
        "title": "Flaggable",
        "content": "<p>Flag me</p>",
        "excerpt": VALID_EXCERPT,
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
        "excerpt": VALID_EXCERPT,
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
        "excerpt": VALID_EXCERPT,
        "is_published": "true",
    })
    assert create2.status_code == 201, create2.text
    post2 = create2.json()

    del_by_admin = await client_admin.delete(f"/v1/posts/{post2['uuid']}")
    assert del_by_admin.status_code == 204, del_by_admin.text


@pytest.mark.asyncio
async def test_record_post_view_counts_once_per_client_window(client_author):
    create = await client_author.post("/v1/posts/", data={
        "title": "View Count Test",
        "content": "<p>Count me</p>",
        "excerpt": VALID_EXCERPT,
        "is_published": "true",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    view1 = await client_author.post(f"/v1/posts/{post['uuid']}/view")
    assert view1.status_code == 200, view1.text
    assert view1.json()["counted"] is True

    view2 = await client_author.post(f"/v1/posts/{post['uuid']}/view")
    assert view2.status_code == 200, view2.text
    assert view2.json()["counted"] is False

    fetch = await client_author.get(f"/v1/posts/{post['uuid']}")
    assert fetch.status_code == 200, fetch.text
    assert fetch.json()["view_count"] == 1


@pytest.mark.asyncio
async def test_record_post_view_invalid_uuid_returns_not_counted(client_author):
    resp = await client_author.post(f"/v1/posts/{uuid4()}/view")
    assert resp.status_code == 200, resp.text
    assert resp.json()["counted"] is False
