import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRole


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

