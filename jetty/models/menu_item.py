from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class MenuSettings(models.Model):
    items = models.TextField(
        verbose_name=_('items'),
        blank=True,
        default=''
    )
    date_add = models.DateTimeField(
        verbose_name=_('date added'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('menu settings')
        verbose_name_plural = _('menu settings')

    def __str__(self):
        return '{}'.format(self.date_add)
