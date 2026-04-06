import pytest


VALID_EXCERPT = (
    "A publish-ready summary that captures the core article, explains why it "
    "matters now, and gives readers a clear reason to keep reading."
)


async def _create_category(client_admin, *, name: str, slug: str, parent_id=None):
    payload = {"name": name, "slug": slug}
    if parent_id is not None:
        payload["parent_id"] = parent_id
    response = await client_admin.post("/v1/posts/categories/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def _create_tag(
    client_admin,
    *,
    name: str,
    slug: str,
    category_id=None,
    is_active=True,
    canonical_tag_id=None,
):
    payload = {
        "name": name,
        "slug": slug,
        "category_id": category_id,
        "is_active": is_active,
        "canonical_tag_id": canonical_tag_id,
    }
    response = await client_admin.post("/v1/posts/tags/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_post_seo_keywords_round_trip_create_and_update(client_admin, client_author):
    category = await _create_category(client_admin, name="Tech Tests", slug="tech-tests")
    tag = await _create_tag(
        client_admin,
        name="Automation",
        slug="automation",
        category_id=category["id"],
    )

    create_response = await client_author.post(
        "/v1/posts/",
        data={
            "title": "SEO Metadata Draft",
            "content": "<p>Hello metadata</p>",
            "excerpt": VALID_EXCERPT,
            "category_id": str(category["id"]),
            "tag_ids": str(tag["id"]),
            "seo_keywords": "automation, workflows, automation",
            "is_published": "true",
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["seo_keywords"] == ["automation", "workflows"]

    update_response = await client_author.put(
        f"/v1/posts/{created['uuid']}",
        data={
            "seo_keywords": "product launch, automation",
            "is_published": "true",
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["seo_keywords"] == ["product launch", "automation"]


@pytest.mark.asyncio
async def test_deprecated_tags_are_hidden_and_resolve_to_canonical_tag_on_save(
    client_admin,
    client_author,
):
    category = await _create_category(client_admin, name="Career Tests", slug="career-tests")
    canonical = await _create_tag(
        client_admin,
        name="Freelancing",
        slug="freelancing",
        category_id=category["id"],
    )
    deprecated = await _create_tag(
        client_admin,
        name="Upwork",
        slug="upwork",
        category_id=category["id"],
        is_active=False,
        canonical_tag_id=canonical["id"],
    )

    list_response = await client_author.get("/v1/posts/tags/")
    assert list_response.status_code == 200, list_response.text
    tag_names = {tag["name"] for tag in list_response.json()["tags"]}
    assert "Freelancing" in tag_names
    assert "Upwork" not in tag_names

    create_response = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Legacy Tag Draft",
            "content": "<p>Trying to use a deprecated tag.</p>",
            "excerpt": VALID_EXCERPT,
            "tag_ids": f"{deprecated['id']},{canonical['id']}",
            "is_published": "true",
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert [tag["name"] for tag in created["tags"]] == ["Freelancing"]


@pytest.mark.asyncio
async def test_inactive_tags_without_canonical_replacement_are_rejected(client_admin, client_author):
    category = await _create_category(client_admin, name="Rejected Tags", slug="rejected-tags")
    inactive = await _create_tag(
        client_admin,
        name="Legacy Platform",
        slug="legacy-platform",
        category_id=category["id"],
        is_active=False,
    )

    create_response = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Unavailable Tag Draft",
            "content": "<p>Trying to use an inactive tag without a replacement.</p>",
            "excerpt": VALID_EXCERPT,
            "tag_ids": str(inactive["id"]),
            "is_published": "true",
        },
    )
    assert create_response.status_code == 400, create_response.text
    assert create_response.json()["detail"] == "One or more selected tags are unavailable"


@pytest.mark.asyncio
async def test_tags_must_belong_to_selected_category_branch(client_admin, client_author):
    tech = await _create_category(client_admin, name="Tech Root", slug="tech-root")
    products = await _create_category(
        client_admin,
        name="Products & Platforms",
        slug="products-and-platforms",
        parent_id=tech["id"],
    )
    security = await _create_category(
        client_admin,
        name="Cybersecurity & Privacy",
        slug="cybersecurity-and-privacy",
        parent_id=tech["id"],
    )
    security_tag = await _create_tag(
        client_admin,
        name="Cybersecurity",
        slug="cybersecurity",
        category_id=security["id"],
    )

    create_response = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Mismatched Taxonomy Draft",
            "content": "<p>Trying to mix sibling taxonomy branches.</p>",
            "excerpt": VALID_EXCERPT,
            "category_id": str(products["id"]),
            "tag_ids": str(security_tag["id"]),
            "is_published": "true",
        },
    )
    assert create_response.status_code == 400, create_response.text
    assert create_response.json()["detail"] == "Selected tags must belong to the chosen category branch"


@pytest.mark.asyncio
async def test_parent_category_accepts_descendant_branch_tags(client_admin, client_author):
    tech = await _create_category(client_admin, name="Tech Parent", slug="tech-parent")
    automation = await _create_category(
        client_admin,
        name="Automation",
        slug="automation",
        parent_id=tech["id"],
    )
    automation_tag = await _create_tag(
        client_admin,
        name="Workflow Automation",
        slug="workflow-automation",
        category_id=automation["id"],
    )

    create_response = await client_author.post(
        "/v1/posts/",
        data={
            "title": "Parent Branch Draft",
            "content": "<p>Parent categories should accept descendant tags.</p>",
            "excerpt": VALID_EXCERPT,
            "category_id": str(tech["id"]),
            "tag_ids": str(automation_tag["id"]),
            "is_published": "true",
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["category"]["id"] == tech["id"]
    assert [tag["name"] for tag in created["tags"]] == ["Workflow Automation"]


@pytest.mark.asyncio
async def test_category_slug_resolution_supports_legacy_redirects(client_admin, client_public):
    created = await _create_category(
        client_admin,
        name="Products and Platforms",
        slug="products-platforms",
    )

    update_response = await client_admin.put(
        f"/v1/posts/categories/{created['id']}",
        json={"slug": "products-and-platforms"},
    )
    assert update_response.status_code == 200, update_response.text

    legacy_response = await client_public.get(
        "/v1/posts/categories/resolve/products-platforms"
    )
    assert legacy_response.status_code == 200, legacy_response.text
    legacy_payload = legacy_response.json()
    assert legacy_payload["matched_slug"] == "products-platforms"
    assert legacy_payload["canonical_slug"] == "products-and-platforms"
    assert legacy_payload["redirect_required"] is True

    canonical_response = await client_public.get(
        "/v1/posts/categories/resolve/products-and-platforms"
    )
    assert canonical_response.status_code == 200, canonical_response.text
    canonical_payload = canonical_response.json()
    assert canonical_payload["redirect_required"] is False
    assert canonical_payload["canonical_slug"] == "products-and-platforms"


@pytest.mark.asyncio
async def test_category_name_update_keeps_existing_slug_until_explicit_slug_change(client_admin):
    created = await _create_category(
        client_admin,
        name="Business Signals",
        slug="business-signals",
    )

    rename_response = await client_admin.put(
        f"/v1/posts/categories/{created['id']}",
        json={"name": "Business Market Signals"},
    )
    assert rename_response.status_code == 200, rename_response.text
    renamed = rename_response.json()
    assert renamed["name"] == "Business Market Signals"
    assert renamed["slug"] == "business-signals"


@pytest.mark.asyncio
async def test_tag_can_be_deprecated_into_canonical_tag_and_hidden_from_default_list(client_admin, client_author):
    category = await _create_category(
        client_admin,
        name="Automation Tests",
        slug="automation-tests",
    )
    canonical = await _create_tag(
        client_admin,
        name="Automation",
        slug="automation",
        category_id=category["id"],
    )
    legacy = await _create_tag(
        client_admin,
        name="Zapier",
        slug="zapier",
        category_id=category["id"],
    )

    update_response = await client_admin.put(
        f"/v1/posts/tags/{legacy['id']}",
        json={"canonical_tag_id": canonical["id"], "is_active": False},
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["canonical_tag_id"] == canonical["id"]
    assert updated["is_active"] is False

    public_tags = await client_author.get("/v1/posts/tags/")
    assert public_tags.status_code == 200, public_tags.text
    public_names = {tag["name"] for tag in public_tags.json()["tags"]}
    assert "Automation" in public_names
    assert "Zapier" not in public_names

    admin_tags = await client_admin.get("/v1/posts/tags/", params={"include_inactive": "true"})
    assert admin_tags.status_code == 200, admin_tags.text
    legacy_payload = next(tag for tag in admin_tags.json()["tags"] if tag["id"] == legacy["id"])
    assert legacy_payload["canonical_tag_id"] == canonical["id"]
    assert legacy_payload["is_active"] is False


@pytest.mark.asyncio
async def test_grouped_tags_hide_deprecated_variants_from_selector(client_admin, client_public):
    tech = await _create_category(client_admin, name="Tech Selector", slug="tech-selector")
    software = await _create_category(
        client_admin,
        name="Software Development",
        slug="software-development",
        parent_id=tech["id"],
    )
    canonical = await _create_tag(
        client_admin,
        name="Backend Development",
        slug="backend-development",
        category_id=software["id"],
    )
    await _create_tag(
        client_admin,
        name="Python",
        slug="python",
        category_id=software["id"],
        is_active=False,
        canonical_tag_id=canonical["id"],
    )

    grouped_response = await client_public.get("/v1/posts/tags/grouped/")
    assert grouped_response.status_code == 200, grouped_response.text
    groups = grouped_response.json()["groups"]
    tech_group = next(group for group in groups if group["category_name"] == "Tech Selector")
    tag_names = {tag["name"] for tag in tech_group["tags"]}
    assert "Backend Development" in tag_names
    assert "Python" not in tag_names


@pytest.mark.asyncio
async def test_grouped_tags_show_generalized_canonical_tags_after_mobile_cleanup(
    client_admin,
    client_public,
):
    tech = await _create_category(client_admin, name="Apps Selector", slug="apps-selector")
    software = await _create_category(
        client_admin,
        name="Software Development",
        slug="software-development",
        parent_id=tech["id"],
    )
    canonical = await _create_tag(
        client_admin,
        name="App Development",
        slug="app-development",
        category_id=software["id"],
    )
    await _create_tag(
        client_admin,
        name="Mobile Apps",
        slug="mobile-apps",
        category_id=software["id"],
        is_active=False,
        canonical_tag_id=canonical["id"],
    )

    grouped_response = await client_public.get("/v1/posts/tags/grouped/")
    assert grouped_response.status_code == 200, grouped_response.text
    groups = grouped_response.json()["groups"]
    tech_group = next(group for group in groups if group["category_name"] == "Apps Selector")
    tag_names = {tag["name"] for tag in tech_group["tags"]}
    assert "App Development" in tag_names
    assert "Mobile Apps" not in tag_names
