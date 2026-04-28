import pytest
from sqlalchemy import select

from models import Category, Notification, Post
from models.user import User, UserRole
from schemas.notification import NotificationType
from services.user.notification import NotificationService


@pytest.mark.asyncio
async def test_reported_post_notifies_admin_moderator_and_super_admin(test_session, author_user):
    reporter = User(
        email="reporter@example.com",
        username="reporter",
        full_name="Reporter",
        password="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    admin = User(
        email="notify-admin@example.com",
        username="notifyadmin",
        full_name="Notify Admin",
        password="hashed",
        role=UserRole.ADMIN,
        is_active=True,
    )
    moderator = User(
        email="notify-mod@example.com",
        username="notifymod",
        full_name="Notify Moderator",
        password="hashed",
        role=UserRole.MODERATOR,
        is_active=True,
    )
    super_admin = User(
        email="notify-super@example.com",
        username="notifysuper",
        full_name="Notify Super",
        password="hashed",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    category = Category(name="Reports", slug="reports")
    post = Post(
        title="Reported Post",
        slug="reported-post",
        content="<p>Reported content</p>",
        author_id=author_user.id,
        category=category,
    )
    test_session.add_all([reporter, admin, moderator, super_admin, category, post])
    await test_session.commit()
    await test_session.refresh(post)
    await test_session.refresh(reporter)

    await NotificationService.notify_post_reported(
        test_session,
        post=post,
        reporter_id=reporter.id,
    )

    result = await test_session.execute(
        select(Notification).where(
            Notification.notification_type == NotificationType.POST_REPORTED
        )
    )
    notifications = result.scalars().all()
    recipient_ids = {notification.recipient_id for notification in notifications}

    assert recipient_ids == {admin.id, moderator.id, super_admin.id}
