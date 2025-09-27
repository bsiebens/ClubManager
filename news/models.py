from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from markdownx.models import MarkdownxField

from teams.models import Team


class NewsItem(models.Model):
    class StatusChoices(models.IntegerChoices):
        DRAFT = 0, _("Draft")
        IN_REVIEW = 1, _("In Review")
        RELEASED = 2, _("Released")

    class NewsItemTypeChoices(models.IntegerChoices):
        INTERNAL = 0, _("Internal")
        EXTERNAL = 1, _("External")
        INTERNAL_EXTERNAL = 2, _("Internal & External")

    title = models.CharField(_("title"), max_length=250)
    text = MarkdownxField(_("text"))
    slug = AutoSlugField(populate_from=["title"], verbose_name=_("slug"))
    author = models.ForeignKey(get_user_model(), verbose_name=_("author"), on_delete=models.PROTECT)
    status = models.IntegerField(_("status"), choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    type = models.IntegerField(_("type"), choices=NewsItemTypeChoices.choices, default=NewsItemTypeChoices.INTERNAL, help_text=_("Internal news is only visible to members after logging in. External news will be published on the website."))
    publish_on = models.DateTimeField(_("Publish on"), default=timezone.now, help_text="Date and time on which this item should be published. Only released items will be posted.")

    teams = models.ManyToManyField(Team, related_name="news_items")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
