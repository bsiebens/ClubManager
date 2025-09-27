from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Sponsor(models.Model):
    """A sponsor is displayed on the front page."""

    name = models.CharField(_("name"), max_length=250)
    start_date = models.DateField(_("start date"), default=timezone.now, help_text=_("Logo will be visible as of this day"))
    end_date = models.DateField(_("end date"), blank=True, null=True, help_text=_("Logo will no longer be visible as of this date, leave empty to display indefinitly"))
    url = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="sponsors/logo/")
    main_sponsor = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def active(self) -> bool:
        if self.end_date is not None:
            return self.start_date <= timezone.now().date() <= self.end_date

        return self.start_date <= timezone.now().date()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("sponsor")
        verbose_name_plural = _("sponsors")
        ordering = ["name"]
