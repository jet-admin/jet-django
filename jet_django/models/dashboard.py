from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Dashboard(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255
    )
    ordering = models.PositiveIntegerField(
        verbose_name=_('ordering'),
        default=0
    )
    date_add = models.DateTimeField(
        verbose_name=_('date added'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')
        ordering = ('ordering',)

    def __str__(self):
        return str(self.name)
