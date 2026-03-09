import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Notification, Post
from models.ai_draft import AIDraft
from models.user import Media, MediaType, Profile, User, UserRole, UserRoleChange
from schemas.notification import NotificationType
from services.user.auth import AuthService


@pytest.mark.asyncio
async def test_admin_can_list_users(client_admin, test_session: AsyncSession):
    extra_user = User(
        email="listuser@example.com",
        username="listuser",
        full_name="List User",
        password="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(extra_user)
    await test_session.commit()

    response = await client_admin.get("/v1/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(user["email"] == "listuser@example.com" for user in data["users"])


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_users(client_author):
    response = await client_author.get("/v1/admin/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_toggle_user_status(client_admin, test_session: AsyncSession):
    target = User(
        email="toggle@example.com",
        username="toggle",
        full_name="Toggle User",
        password="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    response = await client_admin.patch(
        f"/v1/admin/users/{target.uuid}/status", json={"is_active": False}
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_admin_can_change_user_role(client_admin, test_session: AsyncSession):
    target = User(
        email="rolechange@example.com",
        username="rolechange",
        full_name="Role Change",
        password="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    response = await client_admin.patch(
        f"/v1/admin/users/{target.uuid}/role", json={"role": "moderator"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "moderator"


@pytest.mark.asyncio
async def test_admin_cannot_promote_to_admin_or_super_admin(
    client_admin, test_session: AsyncSession
):
    target = User(
        email="rolepromote@example.com",
        username="rolepromote",
        full_name="Role Promote",
        password="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    # Attempt to promote to admin
    response_admin = await client_admin.patch(
        f"/v1/admin/users/{target.uuid}/role", json={"role": "admin"}
    )
    assert response_admin.status_code == 403

    # Attempt to promote to super_admin
    response_super_admin = await client_admin.patch(
        f"/v1/admin/users/{target.uuid}/role", json={"role": "super_admin"}
    )
    assert response_super_admin.status_code == 403


@pytest.mark.asyncio
async def test_admin_cannot_change_admin_or_super_admin(
    client_admin, test_session: AsyncSession
):
    target_admin = User(
        email="target-admin@example.com",
        username="targetadmin",
        full_name="Target Admin",
        password="hashed",
        role=UserRole.ADMIN,
        is_active=True,
    )
    target_super_admin = User(
        email="target-superadmin@example.com",
        username="targetsuperadmin",
        full_name="Target Super Admin",
        password="hashed",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    test_session.add_all([target_admin, target_super_admin])
    await test_session.commit()
    await test_session.refresh(target_admin)
    await test_session.refresh(target_super_admin)

    # Admin attempting to change another admin
    response_admin = await client_admin.patch(
        f"/v1/admin/users/{target_admin.uuid}/role", json={"role": "user"}
    )
    assert response_admin.status_code == 403

    # Admin attempting to change a super-admin
    response_super_admin = await client_admin.patch(
        f"/v1/admin/users/{target_super_admin.uuid}/role", json={"role": "user"}
    )
    assert response_super_admin.status_code == 403


@pytest.mark.asyncio
async def test_super_admin_can_change_admin_role_and_logs_history(
    client_super_admin, test_session: AsyncSession, super_admin_user: User
):
    target = User(
        email="admin-to-demote@example.com",
        username="admindemote",
        full_name="Admin To Demote",
        password="hashed",
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    # Super-admin changes admin to moderator with a reason
    reason = "Restructuring responsibilities"
    response = await client_super_admin.patch(
        f"/v1/admin/users/{target.uuid}/role",
        json={"role": "moderator", "reason": reason},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "moderator"

    # Fetch role history via API
    history_response = await client_super_admin.get(
        f"/v1/admin/users/{target.uuid}/role-history"
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["total"] >= 1
    first_change = history["changes"][0]
    assert first_change["old_role"] == "admin"
    assert first_change["new_role"] == "moderator"
    assert first_change["reason"] == reason
    assert first_change["changed_by"]["email"] == super_admin_user.email


@pytest.mark.asyncio
async def test_admin_user_stats_endpoint(client_admin, test_session: AsyncSession):
    active_user = User(
        email="stat-active@example.com",
        username="statactive",
        full_name="Stat Active",
        password="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    inactive_user = User(
        email="stat-inactive@example.com",
        username="statinactive",
        full_name="Stat Inactive",
        password="hashed",
        role=UserRole.MODERATOR,
        is_active=False,
    )
    test_session.add_all([active_user, inactive_user])
    await test_session.commit()

    response = await client_admin.get("/v1/admin/users/stats")
    assert response.status_code == 200
    data = response.json()
    for key in [
        "total_users",
        "active_users",
        "inactive_users",
        "admin_count",
        "moderator_count",
        "user_count",
        "recent_registrations",
    ]:
        assert key in data


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_admin_account(
    client_admin, test_session: AsyncSession
):
    target_admin = User(
        email="target-admin-status@example.com",
        username="targetadminstatus",
        full_name="Target Admin Status",
        password="hashed",
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_session.add(target_admin)
    await test_session.commit()
    await test_session.refresh(target_admin)

    response = await client_admin.patch(
        f"/v1/admin/users/{target_admin.uuid}/status", json={"is_active": False}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_reset_regular_user_password(
    client_admin, test_session: AsyncSession
):
    target = User(
        email="password-user@example.com",
        username="passworduser",
        full_name="Password User",
        password=AuthService.get_password_hash("oldpassword123"),
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    response = await client_admin.put(
        f"/v1/admin/users/{target.uuid}/password",
        json={"new_password": "newpassword123", "confirm_password": "newpassword123"},
    )
    assert response.status_code == 200
    await test_session.refresh(target)
    assert AuthService.verify_password("newpassword123", target.password)


@pytest.mark.asyncio
async def test_admin_cannot_reset_admin_password(
    client_admin, test_session: AsyncSession
):
    target = User(
        email="password-admin@example.com",
        username="passwordadmin",
        full_name="Password Admin",
        password=AuthService.get_password_hash("oldpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    response = await client_admin.put(
        f"/v1/admin/users/{target.uuid}/password",
        json={"new_password": "newpassword123", "confirm_password": "newpassword123"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_super_admin_can_reset_admin_password(
    client_super_admin, test_session: AsyncSession
):
    target = User(
        email="password-admin-super@example.com",
        username="passwordadminsuper",
        full_name="Password Admin Super",
        password=AuthService.get_password_hash("oldpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    response = await client_super_admin.put(
        f"/v1/admin/users/{target.uuid}/password",
        json={"new_password": "newpassword123", "confirm_password": "newpassword123"},
    )
    assert response.status_code == 200
    await test_session.refresh(target)
    assert AuthService.verify_password("newpassword123", target.password)


@pytest.mark.asyncio
async def test_admin_can_permanently_delete_regular_user_and_owned_content(
    client_admin,
    test_session: AsyncSession,
    admin_user: User,
    tmp_path,
):
    avatar_path = tmp_path / "avatar.png"
    avatar_path.write_text("avatar")
    media_path = tmp_path / "media.txt"
    media_path.write_text("media")
    featured_path = tmp_path / "featured.jpg"
    featured_path.write_text("featured")

    target = User(
        email="purge-user@example.com",
        username="purgeuser",
        full_name="Purge User",
        password=AuthService.get_password_hash("oldpassword123"),
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    profile = Profile(user_id=target.id, avatar=str(avatar_path))
    post = Post(
        title="Purge Post",
        slug="purge-post",
        content="content",
        author_id=target.id,
        featured_image=str(featured_path),
    )
    draft = AIDraft(user_id=target.id, name="Draft", content="draft content")
    media = Media(
        user_id=target.id,
        file_path=str(media_path),
        file_name="media.txt",
        file_type=MediaType.DOCUMENT,
        file_size=5,
        mime_type="text/plain",
    )
    notification = Notification(
        recipient_id=target.id,
        sender_id=admin_user.id,
        notification_type=NotificationType.WELCOME,
        title="Welcome",
        message="hello",
    )
    role_change = UserRoleChange(
        user_id=target.id,
        changed_by_id=admin_user.id,
        old_role="user",
        new_role="moderator",
    )
    test_session.add_all([profile, post, draft, media, notification, role_change])
    await test_session.commit()
    await test_session.refresh(post)

    response = await client_admin.delete(f"/v1/admin/users/{target.uuid}/permanent")
    assert response.status_code == 200
    body = response.json()
    assert body["deleted_user_uuid"] == target.uuid
    assert body["deleted_counts"]["users"] == 1
    assert body["deleted_counts"]["posts"] == 1
    assert body["deleted_counts"]["ai_drafts"] == 1
    assert body["deleted_counts"]["profiles"] == 1
    assert body["deleted_counts"]["media"] == 1
    assert body["deleted_counts"]["user_role_changes"] == 1
    assert body["failed_file_cleanup"] == []
    assert not avatar_path.exists()
    assert not media_path.exists()
    assert not featured_path.exists()

    deleted_user = await test_session.get(User, target.id)
    assert deleted_user is None
    posts = (await test_session.execute(select(Post).where(Post.author_id == target.id))).scalars().all()
    assert posts == []


@pytest.mark.asyncio
async def test_admin_cannot_permanently_delete_admin_account(
    client_admin, test_session: AsyncSession
):
    target = User(
        email="purge-admin@example.com",
        username="purgeadmin",
        full_name="Purge Admin",
        password=AuthService.get_password_hash("oldpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_session.add(target)
    await test_session.commit()
    await test_session.refresh(target)

    response = await client_admin.delete(f"/v1/admin/users/{target.uuid}/permanent")
    assert response.status_code == 403
