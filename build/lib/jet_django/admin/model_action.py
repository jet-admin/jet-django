from django import forms
from django.utils.text import camel_case_to_spaces


class JetAdminModelAction(forms.Form):
    _ids = forms.CharField(label='object ids')

    class Meta:
        pass

    @classmethod
    def init_meta(cls):
        name = camel_case_to_spaces(cls.__name__).replace(' ', '_')
        verbose_name = getattr(cls.Meta, 'verbose_name', name)
        cls._meta = cls.Meta
        cls._meta.name = name
        cls._meta.verbose_name = verbose_name

    def clean__ids(self):
        return self.cleaned_data['_ids'].split(',')

    def get_fields(self):
        fields = self.fields.copy()
        del fields['_ids']
        return fields

    def filer_queryset(self, queryset):
        return queryset.filter(pk__in=self.cleaned_data['_ids'])

    def save(self, queryset):
        raise NotImplementedError
