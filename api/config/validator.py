
import re
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from urllib.parse import urlparse
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


class ValidationRule:
    
    
    def __init__(
        self,
        name: str,
        validator: Callable[[Any], bool],
        error_message: str,
        severity: str = "error",
        applies_to: Optional[List[str]] = None
    ):
        
        self.name = name
        self.validator = validator
        self.error_message = error_message
        self.severity = severity
        self.applies_to = applies_to or ["development", "staging", "production"]


class ValidationResult:
    
    def __init__(self):
        
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.passed_rules: List[str] = []
        self.failed_rules: List[str] = []
    
    def add_error(self, message: str, rule_name: str = None) -> None:
        
        self.errors.append(message)
        if rule_name:
            self.failed_rules.append(rule_name)
    
    def add_warning(self, message: str, rule_name: str = None) -> None:
        
        self.warnings.append(message)
        if rule_name:
            self.failed_rules.append(rule_name)
    
    def add_info(self, message: str, rule_name: str = None) -> None:
        
        self.info.append(message)
    
    def add_passed(self, rule_name: str) -> None:
        
        self.passed_rules.append(rule_name)
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
    
    @property
    def has_warnings(self) -> bool:        
        return len(self.warnings) > 0
    
    def summary(self) -> Dict[str, Any]:
        
        return {
            "is_valid": self.is_valid,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "info_count": len(self.info),
            "passed_rules": len(self.passed_rules),
            "failed_rules": len(self.failed_rules),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info
        }


class ConfigValidator:
    def __init__(self):
        
        self.rules: List[ValidationRule] = []
        self._setup_builtin_rules()
    
    def add_rule(self, rule: ValidationRule) -> None:
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False
    
    def validate(self, config: Dict[str, Any], environment: str = "development") -> ValidationResult:
        result = ValidationResult()
        
        for rule in self.rules:
            if environment not in rule.applies_to:
                continue
            
            try:
                if rule.validator(config):
                    result.add_passed(rule.name)
                else:
                    if rule.severity == "error":
                        result.add_error(rule.error_message, rule.name)
                    elif rule.severity == "warning":
                        result.add_warning(rule.error_message, rule.name)
                    else:
                        result.add_info(rule.error_message, rule.name)
            except Exception as e:
                result.add_error(f"Rule '{rule.name}' failed with exception: {e}", rule.name)
        
        logger.info(f"Configuration validation completed: {result.summary()}")
        return result
    
    def _setup_builtin_rules(self) -> None:
        
        self.rules.extend([
            ValidationRule(
                name="secret_key_length",
                validator=lambda config: len(config.get("secret_key", "")) >= 32,
                error_message="Secret key must be at least 32 characters long",
                severity="error"
            ),
            
            ValidationRule(
                name="secret_key_strength_production",
                validator=lambda config: len(config.get("secret_key", "")) >= 64,
                error_message="Production secret key must be at least 64 characters long",
                severity="error",
                applies_to=["production"]
            ),
            
            ValidationRule(
                name="debug_disabled_production",
                validator=lambda config: not config.get("debug", False),
                error_message="Debug mode must be disabled in production",
                severity="error",
                applies_to=["production"]
            ),
            
            ValidationRule(
                name="https_only_production",
                validator=lambda config: all(
                    url.startswith("https://") for url in config.get("cors_origins", [])
                ),
                error_message="All CORS origins must use HTTPS in production",
                severity="error",
                applies_to=["production"]
            ),
            
            ValidationRule(
                name="no_localhost_production",
                validator=lambda config: not any(
                    "localhost" in str(value) or "127.0.0.1" in str(value)
                    for key, value in config.items()
                    if key.endswith("_url") and isinstance(value, str)
                ),
                error_message="Production configuration cannot use localhost URLs",
                severity="error",
                applies_to=["production"]
            ),
        ])
        
        # Database rules
        self.rules.extend([
            ValidationRule(
                name="database_url_required",
                validator=lambda config: bool(config.get("database_url")),
                error_message="Database URL is required",
                severity="error"
            ),
            
            ValidationRule(
                name="database_url_format",
                validator=lambda config: self._validate_database_url(config.get("database_url", "")),
                error_message="Database URL format is invalid",
                severity="error"
            ),
            
            ValidationRule(
                name="database_ssl_production",
                validator=lambda config: config.get("database_ssl_mode", "") in ["require", "verify-full"],
                error_message="Database SSL must be required in production",
                severity="error",
                applies_to=["production"]
            ),
            
            ValidationRule(
                name="database_pool_size",
                validator=lambda config: 1 <= config.get("database_pool_size", 5) <= 100,
                error_message="Database pool size must be between 1 and 100",
                severity="warning"
            ),
        ])
        
        # Cache rules
        self.rules.extend([
            ValidationRule(
                name="cache_backend_valid",
                validator=lambda config: config.get("cache_backend", "memory") in [
                    "memory", "redis", "memcached", "dummy"
                ],
                error_message="Cache backend must be one of: memory, redis, memcached, dummy",
                severity="error"
            ),
            
            ValidationRule(
                name="redis_url_when_redis_backend",
                validator=lambda config: (
                    config.get("cache_backend") != "redis" or 
                    bool(config.get("redis_url"))
                ),
                error_message="Redis URL is required when using Redis cache backend",
                severity="error"
            ),
        ])
        
        # JWT rules
        self.rules.extend([
            ValidationRule(
                name="jwt_algorithm_secure",
                validator=lambda config: config.get("jwt_algorithm", "HS256") in [
                    "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"
                ],
                error_message="JWT algorithm should be asymmetric (RS256, ES256, etc.) for production",
                severity="warning",
                applies_to=["production"]
            ),
            
            ValidationRule(
                name="jwt_private_key_required",
                validator=lambda config: (
                    config.get("jwt_algorithm", "HS256").startswith(("RS", "ES")) and
                    bool(config.get("jwt_private_key"))
                ) or not config.get("jwt_algorithm", "HS256").startswith(("RS", "ES")),
                error_message="JWT private key is required for asymmetric algorithms",
                severity="error"
            ),
            
            ValidationRule(
                name="jwt_token_expiry_reasonable",
                validator=lambda config: (
                    1 <= config.get("jwt_access_token_expire_minutes", 15) <= 60 and
                    1 <= config.get("jwt_refresh_token_expire_days", 7) <= 30
                ),
                error_message="JWT token expiry times should be reasonable (access: 1-60 min, refresh: 1-30 days)",
                severity="warning"
            ),
        ])
        
        # Email rules
        self.rules.extend([
            ValidationRule(
                name="email_backend_valid",
                validator=lambda config: config.get("email_backend", "console") in [
                    "console", "smtp", "sendgrid", "mailgun", "ses"
                ],
                error_message="Email backend must be one of: console, smtp, sendgrid, mailgun, ses",
                severity="error"
            ),
            
            ValidationRule(
                name="smtp_config_when_smtp_backend",
                validator=lambda config: (
                    config.get("email_backend") != "smtp" or (
                        bool(config.get("smtp_host")) and
                        bool(config.get("smtp_username")) and
                        bool(config.get("smtp_password"))
                    )
                ),
                error_message="SMTP host, username, and password are required when using SMTP backend",
                severity="error"
            ),
            
            ValidationRule(
                name="email_from_address_valid",
                validator=lambda config: self._validate_email(config.get("default_from_email", "")),
                error_message="Default from email address is invalid",
                severity="warning"
            ),
        ])
        
        # File upload rules
        self.rules.extend([
            ValidationRule(
                name="upload_size_reasonable",
                validator=lambda config: 1024 <= config.get("max_upload_size", 5242880) <= 104857600,  # 1KB to 100MB
                error_message="Max upload size should be between 1KB and 100MB",
                severity="warning"
            ),
            
            ValidationRule(
                name="upload_path_exists",
                validator=lambda config: self._validate_upload_path(config.get("upload_path", "")),
                error_message="Upload path does not exist or is not writable",
                severity="warning"
            ),
        ])
        
        # Rate limiting rules
        self.rules.extend([
            ValidationRule(
                name="rate_limits_format",
                validator=lambda config: self._validate_rate_limits(config),
                error_message="Rate limit format is invalid (should be 'count/period' like '100/hour')",
                severity="error"
            ),
            
            ValidationRule(
                name="production_rate_limits_strict",
                validator=lambda config: self._validate_production_rate_limits(config),
                error_message="Production rate limits should be stricter",
                severity="warning",
                applies_to=["production"]
            ),
        ])
        
        # Logging rules
        self.rules.extend([
            ValidationRule(
                name="log_level_valid",
                validator=lambda config: config.get("log_level", "INFO") in [
                    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
                ],
                error_message="Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL",
                severity="error"
            ),
            
            ValidationRule(
                name="production_log_level",
                validator=lambda config: config.get("log_level", "INFO") in ["INFO", "WARNING", "ERROR"],
                error_message="Production log level should be INFO, WARNING, or ERROR",
                severity="warning",
                applies_to=["production"]
            ),
        ])
    
    def _validate_database_url(self, url: str) -> bool:
        
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _validate_email(self, email: str) -> bool:
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_upload_path(self, path: str) -> bool:
        if not path:
            return True
        
        try:
            upload_path = Path(path)
            return upload_path.exists() and upload_path.is_dir()
        except Exception:
            return False
    
    def _validate_rate_limits(self, config: Dict[str, Any]) -> bool:
        
        rate_limit_keys = [
            "rate_limit_login", "rate_limit_api", "rate_limit_registration",
            "rate_limit_password_reset"
        ]
        
        pattern = r'^\d+/(second|minute|hour|day)s?$'
        
        for key in rate_limit_keys:
            value = config.get(key)
            if value and not re.match(pattern, value):
                return False
        
        return True
    
    def _validate_production_rate_limits(self, config: Dict[str, Any]) -> bool:
        
        limits = {
            "rate_limit_login": (5, "15minutes"),  # Max 5 attempts per 15 minutes
            "rate_limit_registration": (3, "hour"),  # Max 3 registrations per hour
            "rate_limit_password_reset": (3, "hour"),  # Max 3 resets per hour
        }
        
        for key, (max_count, period) in limits.items():
            value = config.get(key, "")
            if not value:
                continue
            
            try:
                count_str = value.split("/")[0]
                count = int(count_str)
                if count > max_count:
                    return False
            except (ValueError, IndexError):
                continue
        
        return True


def validate_config(
    config: Dict[str, Any],
    environment: str = "development",
    custom_rules: Optional[List[ValidationRule]] = None
) -> ValidationResult:
    validator = ConfigValidator()
    if custom_rules:
        for rule in custom_rules:
            validator.add_rule(rule)
    
    return validator.validate(config, environment)


def validate_config_file(
    config_file: str,
    environment: str = "development",
    custom_rules: Optional[List[ValidationRule]] = None
) -> ValidationResult:
    
    import json
    from pathlib import Path
    
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            result = ValidationResult()
            result.add_error(f"Configuration file not found: {config_file}")
            return result
        
        with config_path.open("r", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yml", ".yaml"]:
                import yaml
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        
        if isinstance(config, dict) and environment in config:
            config = config[environment]
        
        return validate_config(config, environment, custom_rules)
        
    except Exception as e:
        result = ValidationResult()
        result.add_error(f"Failed to load configuration file: {e}")
        return result



SECURITY_RULES = [
    ValidationRule(
        name="no_default_passwords",
        validator=lambda config: not any(
            str(value).lower() in ["password", "admin", "123456", "secret"]
            for key, value in config.items()
            if "password" in key.lower()
        ),
        error_message="Default or weak passwords detected",
        severity="error"
    ),
    
    ValidationRule(
        name="secure_session_settings",
        validator=lambda config: (
            config.get("session_secure", True) and
            config.get("session_httponly", True)
        ),
        error_message="Session cookies should be secure and HTTP-only",
        severity="warning",
        applies_to=["staging", "production"]
    ),
]

PERFORMANCE_RULES = [
    ValidationRule(
        name="reasonable_worker_count",
        validator=lambda config: 1 <= config.get("worker_processes", 1) <= 16,
        error_message="Worker process count should be reasonable (1-16)",
        severity="warning"
    ),
    
    ValidationRule(
        name="cache_enabled_production",
        validator=lambda config: config.get("cache_backend", "memory") != "dummy",
        error_message="Cache should be enabled in production",
        severity="warning",
        applies_to=["production"]
    ),
]

COMPLIANCE_RULES = [
    ValidationRule(
        name="audit_logging_enabled",
        validator=lambda config: config.get("enable_audit_logging", False),
        error_message="Audit logging should be enabled for compliance",
        severity="warning",
        applies_to=["staging", "production"]
    ),
    
    ValidationRule(
        name="data_retention_configured",
        validator=lambda config: bool(config.get("data_retention_days")),
        error_message="Data retention policy should be configured",
        severity="info",
        applies_to=["production"]
    ),
] 