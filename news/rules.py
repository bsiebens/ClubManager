import rules
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


@rules.predicate
def is_author(user: AbstractUser | None, item) -> bool:
    from .models import NewsItem, Attachment

    if item is not None:
        if isinstance(item, NewsItem):
            return item.author == user

        if isinstance(item, Attachment):
            return item.news_item.author == user

    return True


@rules.predicate
def is_released(user: AbstractUser | None, item) -> bool:
    from .models import NewsItem, Attachment

    if item is not None:
        if isinstance(item, NewsItem):
            return item.status == NewsItem.StatusChoices.RELEASED and item.publish_on <= timezone.now()

        if isinstance(item, Attachment):
            return item.news_item.status == NewsItem.StatusChoices.RELEASED and item.news_item.publish_on <= timezone.now()

    return False


is_editor = rules.is_group_member("editors")
