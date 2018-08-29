from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class ModelDescription(models.Model):
    app_label = models.CharField(
        verbose_name=_('app_label'),
        max_length=255
    )
    model = models.CharField(
        verbose_name=_('model'),
        max_length=255,
        blank=True,
        default=''
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
        verbose_name = _('model description')
        verbose_name_plural = _('model descriptions')

    def __str__(self):
        return '{} {}'.format(self.app_label, self.model)
