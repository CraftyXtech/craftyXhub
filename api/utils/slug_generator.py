import re
import unicodedata
import secrets
import string


def generate_slug(title: str, max_length: int = 50, add_random_suffix: bool = True) -> str:
    if not title or not title.strip():
        return generate_random_slug()

    slug = title.lower().strip()

    # Remove accents and normalize unicode characters
    slug = unicodedata.normalize('NFKD', slug)
    slug = ''.join(c for c in slug if not unicodedata.combining(c))

    # Replace spaces and multiple whitespace with underscores
    slug = re.sub(r'\s+', '_', slug)

    # Remove special characters, keep only alphanumeric, underscores, and hyphens
    slug = re.sub(r'[^a-z0-9_-]', '', slug)

    # Replace multiple underscores/hyphens with single underscore
    slug = re.sub(r'[_-]+', '_', slug)

    # Remove leading/trailing underscores or hyphens
    slug = slug.strip('_-')

    # If slug is empty after cleaning, generate a random one
    if not slug:
        return generate_random_slug()

    # Truncate to max length, ensuring we don't cut in the middle of a word
    if len(slug) > max_length:
        slug = slug[:max_length]
        # Find the last underscore to avoid cutting words
        last_underscore = slug.rfind('_')
        if last_underscore > max_length * 0.7:  # Only if it's not too short
            slug = slug[:last_underscore]

    # Add random suffix for uniqueness if requested
    if add_random_suffix:
        random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
        # Ensure total length doesn't exceed max_length
        if len(slug) + len(random_suffix) + 1 > max_length:
            slug = slug[:max_length - len(random_suffix) - 1]
        slug = f"{slug}_{random_suffix}"

    return slug


def generate_random_slug(length: int = 8) -> str:
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length))
