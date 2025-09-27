from PIL import Image
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from rules import is_superuser
from rules.contrib.models import RulesModel

from teams.models import Team
from .rules import is_author, is_released, is_editor


class NewsItem(RulesModel):
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

    class Meta:
        verbose_name = _("News item")
        verbose_name_plural = _("News items")
        ordering = ["-created"]
        rules_permissions = {
            "add": is_superuser | is_author | is_editor,
            "view": is_superuser | is_author | is_released | is_editor,
            "change": is_superuser | is_author | is_editor,
            "delete": is_superuser | is_author | is_editor,
            "release": is_superuser | is_editor,
        }

    def __str_(self):
        return self.title

    def formatted(self) -> str:
        return markdownify(self.text)

    def main_picture(self) -> "Attachment | None":
        try:
            return self.attachments.get(main_picture=True)
        except Attachment.DoesNotExist:
            return None


class Attachment(RulesModel):
    news_item = models.ForeignKey(NewsItem, on_delete=models.CASCADE, related_name="attachments", verbose_name=_("News item"))

    file = models.FileField(_("file"), upload_to="news/")
    picture = models.BooleanField(_("picture"), default=False)
    main_picture = models.BooleanField(_("main picture"), default=False, help_text=_("The main picture is the picture shown on the cover of the news item"))

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    rules_permissions = {
        "add": is_superuser | is_author | is_editor,
        "view": is_superuser | is_author | is_released | is_editor,
        "change": is_superuser | is_author | is_editor,
        "delete": is_superuser | is_author | is_editor,
    }

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        constraints = [
            models.UniqueConstraint(
                fields=["news_item", "main_picture"],
                condition=models.Q(main_picture=True),
                name="news_item_main_picture_unique",
                violation_error_message=_("Only one picture can be the main picture for a news item"),
            )
        ]

    def save(self, *args, **kwargs):
        self.picture = self._is_picture()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name

    def _is_picture(self) -> bool:
        """
        Determines if the entity is of a picture type or not.

        This method checks internal attributes and conditions to
        determine if the entity can be classified as a picture.

        :return: A boolean value indicating whether the entity is a
            picture (True) or not (False).
        :rtype: bool
        """
        if not self.file:
            return False

        try:
            with Image.open(self.file.path) as img:
                img.verify()
            return True
        except Exception:
            return False
