from jet_django.admin.model_description import JetAdminModelDescription


class JetAdmin(object):
    models = []

    def register(self, Model, fields=None, actions=list(), ordering_field=None, hidden=False):
        self.models.append(JetAdminModelDescription(Model, fields, actions, ordering_field, hidden))

    def register_related_models(self):
        def model_key(x):
            return '{}_{}'.format(
                x['app_label'],
                x['model']
            )
        registered = set(map(lambda x: model_key(x.get_model()), self.models))

        for models_description in self.models:
            for item in models_description.get_related_models():
                key = model_key(item['model_info'])

                if key in registered:
                    continue

                self.register(item['model'], hidden=True)
                registered.add(key)

jet = JetAdmin()
