from enum import Enum


class StatusEnum(str, Enum):
    """Список доступных статусов для объявления"""

    PUBLISHED = "published"
    DELETED = "deleted"
    UNDER_MODERATION = "under_moderation"
    DRAFT = "draft"
