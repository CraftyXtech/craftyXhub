import pytest

from core.config import settings

VALID_EXCERPT = (
    "A concise article summary that captures the full story, the main argument, "
    "and the reason a reader should continue on CraftyXHub."
)


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
            "excerpt": (
                "This is the excerpt that should appear in the share card and it "
                "summarizes the full article clearly for readers coming from social."
            ),
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
async def test_short_share_alias_renders_same_metadata(
    client_author,
    client_public,
    monkeypatch,
):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://craftyxhub.com")

    create = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Short Alias Post",
            "content": "<p>Body for the short alias route.</p>",
            "excerpt": VALID_EXCERPT,
            "meta_description": "Short alias description.",
            "is_published": "true",
        },
    )
    assert create.status_code == 201, create.text
    post = create.json()

    response = await client_public.get(f"/s/{post['uuid']}")
    assert response.status_code == 200, response.text
    html = response.text
    assert '<meta property="og:description" content="Short alias description."' in html
    assert f'https://craftyxhub.com/post/{post["slug"]}' in html


@pytest.mark.asyncio
async def test_share_page_supports_head_requests(
    client_author,
    client_public,
    monkeypatch,
):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://craftyxhub.com")

    create = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Head Request Post",
            "content": "<p>Body for head request coverage.</p>",
            "excerpt": VALID_EXCERPT,
            "is_published": "true",
        },
    )
    assert create.status_code == 201, create.text
    post = create.json()

    response = await client_public.head(f"/share/posts/{post['slug']}")
    assert response.status_code == 200, response.text
    assert response.headers["x-robots-tag"] == "noindex,follow"
    assert response.headers["content-type"].startswith("text/html")

    short_response = await client_public.head(f"/s/{post['uuid']}")
    assert short_response.status_code == 200, short_response.text
    assert short_response.headers["x-robots-tag"] == "noindex,follow"


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
            "excerpt": (
                "Fallback excerpt for social previews that still captures the full "
                "article and gives readers a useful reason to click through."
            ),
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
        '<meta property="og:description" content="Fallback excerpt for social previews that still captures the full article and gives readers a useful reason to click through."'
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
