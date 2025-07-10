from typing import Optional, Dict, List, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from fastapi import HTTPException

from models.audit import Setting
from models.user import User
from schemas.admin.system_management import (
    SettingsResponse, SettingsUpdateRequest,
    EditorPermissionsResponse, EditorPermissionsRequest
)
from .audit_service import AuditService


class SettingsService:
    
    def __init__(self, session: AsyncSession, audit_service: AuditService):
        self.session = session
        self.audit_service = audit_service

    async def get_settings(self, admin_user: User) -> SettingsResponse:
        """Get current site settings."""
        try:
            # Get all settings
            stmt = select(Setting)
            result = await self.session.execute(stmt)
            settings = result.scalars().all()
            
            # Convert to dictionary
            settings_dict = {setting.key: setting.value for setting in settings}
            
            # Apply defaults for missing settings
            settings_dict = await self._apply_default_settings(settings_dict)
            
            # Build editor permissions
            editor_perms = EditorPermissionsResponse(
                can_publish=settings_dict.get("editor_can_publish", "true").lower() == "true",
                requires_approval=settings_dict.get("editor_requires_approval", "false").lower() == "true",
                can_manage_categories=settings_dict.get("editor_can_manage_categories", "true").lower() == "true",
                can_manage_tags=settings_dict.get("editor_can_manage_tags", "true").lower() == "true",
                can_moderate_comments=settings_dict.get("editor_can_moderate_comments", "false").lower() == "true"
            )
            
            response = SettingsResponse(
                site_name=settings_dict.get("site_name", "CraftyXhub"),
                site_description=settings_dict.get("site_description"),
                site_url=settings_dict.get("site_url", "http://localhost:8000"),
                maintenance_mode=settings_dict.get("maintenance_mode", "false").lower() == "true",
                allow_user_registration=settings_dict.get("allow_user_registration", "true").lower() == "true",
                default_user_role=settings_dict.get("default_user_role", "user"),
                require_email_verification=settings_dict.get("require_email_verification", "true").lower() == "true",
                default_editor_permissions=editor_perms,
                max_upload_size=int(settings_dict.get("max_upload_size", "10")),
                allowed_file_types=settings_dict.get("allowed_file_types", "jpg,jpeg,png,gif,pdf").split(","),
                posts_per_page=int(settings_dict.get("posts_per_page", "9")),
                comments_enabled=settings_dict.get("comments_enabled", "true").lower() == "true",
                guest_comments_enabled=settings_dict.get("guest_comments_enabled", "false").lower() == "true",
                auto_approve_comments=settings_dict.get("auto_approve_comments", "false").lower() == "true"
            )
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_view",
                status="success",
                parameters={}
            )
            
            return response
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_view",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

    async def update_settings(self, settings_update: SettingsUpdateRequest, admin_user: User) -> SettingsResponse:
        """Update site settings."""
        try:
            updated_settings = []
            
            # Update individual settings
            if settings_update.site_name is not None:
                await self._update_setting("site_name", settings_update.site_name)
                updated_settings.append("site_name")
                
            if settings_update.site_description is not None:
                await self._update_setting("site_description", settings_update.site_description)
                updated_settings.append("site_description")
                
            if settings_update.site_url is not None:
                await self._update_setting("site_url", settings_update.site_url)
                updated_settings.append("site_url")
                
            if settings_update.maintenance_mode is not None:
                await self._update_setting("maintenance_mode", str(settings_update.maintenance_mode).lower())
                updated_settings.append("maintenance_mode")
                
            if settings_update.allow_user_registration is not None:
                await self._update_setting("allow_user_registration", str(settings_update.allow_user_registration).lower())
                updated_settings.append("allow_user_registration")
                
            if settings_update.default_user_role is not None:
                await self._update_setting("default_user_role", settings_update.default_user_role)
                updated_settings.append("default_user_role")
                
            if settings_update.require_email_verification is not None:
                await self._update_setting("require_email_verification", str(settings_update.require_email_verification).lower())
                updated_settings.append("require_email_verification")
                
            if settings_update.max_upload_size is not None:
                await self._update_setting("max_upload_size", str(settings_update.max_upload_size))
                updated_settings.append("max_upload_size")
                
            if settings_update.allowed_file_types is not None:
                await self._update_setting("allowed_file_types", ",".join(settings_update.allowed_file_types))
                updated_settings.append("allowed_file_types")
                
            if settings_update.posts_per_page is not None:
                await self._update_setting("posts_per_page", str(settings_update.posts_per_page))
                updated_settings.append("posts_per_page")
                
            if settings_update.comments_enabled is not None:
                await self._update_setting("comments_enabled", str(settings_update.comments_enabled).lower())
                updated_settings.append("comments_enabled")
                
            if settings_update.guest_comments_enabled is not None:
                await self._update_setting("guest_comments_enabled", str(settings_update.guest_comments_enabled).lower())
                updated_settings.append("guest_comments_enabled")
                
            if settings_update.auto_approve_comments is not None:
                await self._update_setting("auto_approve_comments", str(settings_update.auto_approve_comments).lower())
                updated_settings.append("auto_approve_comments")
                
            # Update editor permissions
            if settings_update.default_editor_permissions is not None:
                perms = settings_update.default_editor_permissions
                
                if perms.can_publish is not None:
                    await self._update_setting("editor_can_publish", str(perms.can_publish).lower())
                    updated_settings.append("editor_can_publish")
                    
                if perms.requires_approval is not None:
                    await self._update_setting("editor_requires_approval", str(perms.requires_approval).lower())
                    updated_settings.append("editor_requires_approval")
                    
                if perms.can_manage_categories is not None:
                    await self._update_setting("editor_can_manage_categories", str(perms.can_manage_categories).lower())
                    updated_settings.append("editor_can_manage_categories")
                    
                if perms.can_manage_tags is not None:
                    await self._update_setting("editor_can_manage_tags", str(perms.can_manage_tags).lower())
                    updated_settings.append("editor_can_manage_tags")
                    
                if perms.can_moderate_comments is not None:
                    await self._update_setting("editor_can_moderate_comments", str(perms.can_moderate_comments).lower())
                    updated_settings.append("editor_can_moderate_comments")
            
            await self.session.commit()
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_update",
                status="success",
                parameters={"updated_settings": updated_settings}
            )
            
            # Return updated settings
            return await self.get_settings(admin_user)
            
        except Exception as e:
            await self.session.rollback()
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_update", 
                status="failure",
                parameters={"requested_updates": settings_update.model_dump(exclude_none=True)},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

    async def update_single_setting(self, key: str, value: str, admin_user: User) -> Dict[str, Any]:
        """Update a single setting by key."""
        try:
            # Validate setting key
            valid_keys = [
                "site_name", "site_description", "site_url", "maintenance_mode",
                "allow_user_registration", "default_user_role", "require_email_verification",
                "max_upload_size", "allowed_file_types", "posts_per_page",
                "comments_enabled", "guest_comments_enabled", "auto_approve_comments",
                "editor_can_publish", "editor_requires_approval", "editor_can_manage_categories",
                "editor_can_manage_tags", "editor_can_moderate_comments"
            ]
            
            if key not in valid_keys:
                raise HTTPException(status_code=400, detail=f"Invalid setting key: {key}")
            
            old_value = await self._get_setting_value(key)
            await self._update_setting(key, value)
            await self.session.commit()
            
            result = {
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="single_setting_update",
                status="success",
                parameters={"key": key, "old_value": old_value, "new_value": value}
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="single_setting_update",
                status="failure",
                parameters={"key": key, "value": value},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to update setting: {str(e)}")

    async def reset_settings_to_default(self, admin_user: User) -> SettingsResponse:
        """Reset all settings to default values."""
        try:
            # Delete all existing settings
            await self.session.execute(update(Setting).values(value=None))
            
            # Apply defaults
            default_settings = await self._get_default_settings()
            
            for key, value in default_settings.items():
                await self._update_setting(key, value)
            
            await self.session.commit()
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_reset",
                status="success",
                parameters={}
            )
            
            return await self.get_settings(admin_user)
            
        except Exception as e:
            await self.session.rollback()
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_reset",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to reset settings: {str(e)}")

    async def export_settings(self, admin_user: User) -> Dict[str, Any]:
        """Export current settings for backup."""
        try:
            stmt = select(Setting)
            result = await self.session.execute(stmt)
            settings = result.scalars().all()
            
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "exported_by": admin_user.id,
                "settings": {
                    setting.key: {
                        "value": setting.value,
                        "description": setting.description,
                        "created_at": setting.created_at.isoformat() if setting.created_at else None,
                        "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
                    }
                    for setting in settings
                }
            }
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_export",
                status="success",
                parameters={"settings_count": len(settings)}
            )
            
            return export_data
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="settings_export",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to export settings: {str(e)}")

    async def _update_setting(self, key: str, value: str) -> None:
        """Update or create a setting."""
        stmt = select(Setting).where(Setting.key == key)
        result = await self.session.execute(stmt)
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = Setting(
                key=key,
                value=value,
                description=f"System setting: {key}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(setting)

    async def _get_setting_value(self, key: str) -> Optional[str]:
        """Get a setting value by key."""
        stmt = select(Setting.value).where(Setting.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _apply_default_settings(self, settings_dict: Dict[str, str]) -> Dict[str, str]:
        """Apply default values for missing settings."""
        defaults = await self._get_default_settings()
        
        for key, default_value in defaults.items():
            if key not in settings_dict:
                settings_dict[key] = default_value
                
        return settings_dict

    async def _get_default_settings(self) -> Dict[str, str]:
        """Get default settings values."""
        return {
            "site_name": "CraftyXhub",
            "site_description": "A creative blog platform for makers and crafters",
            "site_url": "http://localhost:8000",
            "maintenance_mode": "false",
            "allow_user_registration": "true",
            "default_user_role": "user",
            "require_email_verification": "true",
            "max_upload_size": "10",
            "allowed_file_types": "jpg,jpeg,png,gif,pdf",
            "posts_per_page": "9",
            "comments_enabled": "true",
            "guest_comments_enabled": "false",
            "auto_approve_comments": "false",
            "editor_can_publish": "true",
            "editor_requires_approval": "false",
            "editor_can_manage_categories": "true",
            "editor_can_manage_tags": "true",
            "editor_can_moderate_comments": "false"
        } 