from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Widget(models.Model):
    dashboard = models.ForeignKey(
        to='jet_django.Dashboard',
        verbose_name=_('dashboard'),
        related_name='widgets'
    )
    widget_type = models.CharField(
        verbose_name=_('type'),
        max_length=255
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255
    )
    x = models.PositiveSmallIntegerField(
        verbose_name=_('x')
    )
    y = models.PositiveSmallIntegerField(
        verbose_name=_('y')
    )
    width = models.PositiveSmallIntegerField(
        verbose_name=_('width'),
        default=1
    )
    height = models.PositiveSmallIntegerField(
        verbose_name=_('height'),
        default=1
    )
    params = models.TextField(
        verbose_name=_('params'),
        blank=True,
        default=''
    )
    date_add = models.DateTimeField(
        verbose_name=_('date added'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('widget')
        verbose_name_plural = _('widgets')
        ordering = ('y', 'x')

    def __str__(self):
        return str(self.name)
