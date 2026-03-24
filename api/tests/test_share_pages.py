import pytest

from core.config import settings


@pytest.mark.asyncio
async def test_share_page_renders_social_meta_and_redirects(
    client_author,
    client_public,
    monkeypatch,
):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://craftyxhub.com")
    monkeypatch.setattr(
        settings,
        "DEFAULT_SHARE_IMAGE_URL",
        "https://craftyxhub.com/default-share.png",
    )

    create = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Shareable Post",
            "content": "<p>Body for a shareable post.</p>",
            "excerpt": "This is the excerpt that should appear in the share card.",
            "meta_title": "Custom Share Title",
            "meta_description": "Custom share description for social cards.",
            "featured_image_path": "uploads/posts/share-card.jpg",
            "is_published": "true",
        },
    )
    assert create.status_code == 201, create.text
    post = create.json()

    response = await client_public.get(f"/share/posts/{post['slug']}")
    assert response.status_code == 200, response.text

    html = response.text
    assert '<meta property="og:title" content="Custom Share Title"' in html
    assert (
        '<meta property="og:description" content="Custom share description for social cards."'
        in html
    )
    assert '<meta name="twitter:card" content="summary_large_image"' in html
    assert "http://test/v1/uploads/images/share-card.jpg?folder=posts" in html
    assert f"https://craftyxhub.com/post/{post['slug']}" in html
    assert 'window.location.replace("https://craftyxhub.com/post/' in html
    assert response.headers["x-robots-tag"] == "noindex,follow"


@pytest.mark.asyncio
async def test_share_page_uses_excerpt_and_default_image_when_seo_fields_missing(
    client_author,
    client_public,
    monkeypatch,
):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://craftyxhub.com")
    monkeypatch.setattr(
        settings,
        "DEFAULT_SHARE_IMAGE_URL",
        "https://craftyxhub.com/default-share.png",
    )

    create = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Fallback Share Title",
            "content": "<p>This is the long-form content that backs the fallback share page.</p>",
            "excerpt": "Fallback excerpt for social previews.",
            "is_published": "true",
        },
    )
    assert create.status_code == 201, create.text
    post = create.json()

    response = await client_public.get(f"/share/posts/{post['slug']}")
    assert response.status_code == 200, response.text

    html = response.text
    assert '<meta property="og:title" content="Fallback Share Title"' in html
    assert (
        '<meta property="og:description" content="Fallback excerpt for social previews."'
        in html
    )
    assert "https://craftyxhub.com/default-share.png" in html


@pytest.mark.asyncio
async def test_share_page_rejects_unpublished_posts(client_author, client_public):
    create = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Draft Only",
            "content": "<p>Draft body</p>",
            "is_published": "false",
        },
    )
    assert create.status_code == 201, create.text
    post = create.json()

    response = await client_public.get(f"/share/posts/{post['slug']}")
    assert response.status_code == 404, response.text
