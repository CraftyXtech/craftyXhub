import asyncio
import json
import pytest
from uuid import uuid4

from sqlalchemy import select

from models import Category, Post
from models.content_intelligence import PostQualityReview
from core.config import settings

VALID_EXCERPT = (
    "A publish-ready summary that captures the full article, highlights the "
    "main takeaway, and gives readers a clear reason to keep reading on the site."
)


async def create_publish_category(test_session):
    suffix = uuid4().hex[:8]
    category = Category(name=f"Publishing {suffix}", slug=f"publishing-{suffix}")
    test_session.add(category)
    await test_session.commit()
    await test_session.refresh(category)
    return category


@pytest.mark.asyncio
async def test_create_post_published_immediately(client_author, test_session):
    category = await create_publish_category(test_session)
    data = {
        "title": "My First Post",
        "content": "<p>Hello world</p>",
        "excerpt": VALID_EXCERPT,
        "is_published": "true",
        "category_id": str(category.id),
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
async def test_update_post_toggle_publish(client_author, test_session):
    category = await create_publish_category(test_session)
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
        "category_id": str(category.id),
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
async def test_update_published_post_keeps_original_published_at(client_author, test_session):
    category = await create_publish_category(test_session)
    create = await client_author.post("/v1/posts/", data={
        "title": "Published Post",
        "content": "<p>Original content</p>",
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
        "is_published": "true",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    original_published_at = post["published_at"]
    original_updated_at = post["updated_at"]

    await asyncio.sleep(0.01)

    update = await client_author.put(f"/v1/posts/{post['uuid']}", data={
        "title": "Published Post Updated",
        "content": "<p>Updated content</p>",
        "is_published": "true",
    })
    assert update.status_code == 200, update.text
    body = update.json()

    assert body["is_published"] is True
    assert body["published_at"] == original_published_at
    assert body["updated_at"] != original_updated_at


@pytest.mark.asyncio
async def test_publish_reruns_stale_quality_review_after_draft_edit(
    client_author,
    test_session,
    monkeypatch,
):
    monkeypatch.setattr(settings, "CONTENT_INTELLIGENCE_ENABLED", True)
    category = await create_publish_category(test_session)
    create = await client_author.post("/v1/posts/", data={
        "title": "Draft With Old Review",
        "content": "<p>Original content without review warnings.</p>",
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
        "is_published": "false",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    db_post_id = (
        await test_session.execute(select(Post.id).where(Post.uuid == post["uuid"]))
    ).scalar_one()
    test_session.add(PostQualityReview(
        post_id=db_post_id,
        checks={"warnings": [], "critical_failures": []},
        needs_human_review=False,
        score=100,
        status="passed",
    ))
    await test_session.commit()

    update = await client_author.put(f"/v1/posts/{post['uuid']}", data={
        "content": (
            "<p>Research shows 75% of teams need better publishing controls "
            "before scaling editorial operations.</p>"
        ),
    })
    assert update.status_code == 200, update.text

    publish = await client_author.put(f"/v1/posts/{post['uuid']}/publish")
    assert publish.status_code == 409, publish.text
    assert publish.json()["detail"]["quality_status"] == "needs_review"

    db_post = (
        await test_session.execute(select(Post).where(Post.uuid == post["uuid"]))
    ).scalar_one()
    assert db_post.is_published is False


@pytest.mark.asyncio
async def test_rejected_published_edit_does_not_commit_content(
    client_author,
    test_session,
    monkeypatch,
):
    monkeypatch.setattr(settings, "CONTENT_INTELLIGENCE_ENABLED", True)
    category = await create_publish_category(test_session)
    original_content = "<p>Original published content.</p>"
    create = await client_author.post("/v1/posts/", data={
        "title": "Published Quality Gate",
        "content": original_content,
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
        "is_published": "true",
    })
    assert create.status_code == 201, create.text
    post = create.json()

    update = await client_author.put(f"/v1/posts/{post['uuid']}", data={
        "content": (
            "<p>Research shows 75% of teams need better publishing controls "
            "before scaling editorial operations.</p>"
        ),
        "is_published": "true",
    })
    assert update.status_code == 409, update.text
    assert update.json()["detail"]["quality_status"] == "needs_review"

    db_post = (
        await test_session.execute(select(Post).where(Post.uuid == post["uuid"]))
    ).scalar_one()
    assert db_post.is_published is True
    assert db_post.content == original_content


@pytest.mark.asyncio
async def test_publish_endpoint_still_works(client_author, test_session):
    category = await create_publish_category(test_session)
    create = await client_author.post("/v1/posts/", data={
        "title": "Draft 2",
        "content": "<p>Draft 2</p>",
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
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
async def test_publish_bypasses_quality_gate_when_content_intelligence_disabled(
    client_author,
    test_session,
    monkeypatch,
):
    monkeypatch.setattr(settings, "CONTENT_INTELLIGENCE_ENABLED", False)
    category = await create_publish_category(test_session)
    create = await client_author.post("/v1/posts/", data={
        "title": "Draft Without CI Gate",
        "content": (
            "<p>Research shows 75% of teams need better publishing controls "
            "before scaling editorial operations.</p>"
        ),
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
        "is_published": "false",
    })
    assert create.status_code == 201, create.text
    post = create.json()

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
async def test_admin_flag_unpublishes(client_admin, client_author, test_session):
    category = await create_publish_category(test_session)
    # author creates published post
    create = await client_author.post("/v1/posts/", data={
        "title": "Flaggable",
        "content": "<p>Flag me</p>",
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
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
async def test_delete_permissions(client_author, client_admin, test_session):
    category = await create_publish_category(test_session)
    # author creates
    create = await client_author.post("/v1/posts/", data={
        "title": "Delete Me",
        "content": "<p>bye</p>",
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
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
        "category_id": str(category.id),
        "is_published": "true",
    })
    assert create2.status_code == 201, create2.text
    post2 = create2.json()

    del_by_admin = await client_admin.delete(f"/v1/posts/{post2['uuid']}")
    assert del_by_admin.status_code == 204, del_by_admin.text


@pytest.mark.asyncio
async def test_record_post_view_counts_once_per_client_window(client_author, test_session):
    category = await create_publish_category(test_session)
    create = await client_author.post("/v1/posts/", data={
        "title": "View Count Test",
        "content": "<p>Count me</p>",
        "excerpt": VALID_EXCERPT,
        "category_id": str(category.id),
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
