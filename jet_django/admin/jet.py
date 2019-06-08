from jet_django.admin.model_description import JetAdminModelDescription


class JetAdmin(object):
    models = []
    message_handlers = {}

    def register(self, Model, fields=None, hidden=False):
        self.models.append(JetAdminModelDescription(Model, fields, hidden))

    def register_related_models(self):
        def model_key(x):
            return x['model']
        registered = set(map(lambda x: model_key(x.get_model()), self.models))

        for models_description in self.models:
            for item in models_description.get_related_models():
                key = model_key(item['model_info'])

                if key in registered:
                    continue

                self.register(item['model'], hidden=True)
                registered.add(key)

    def add_message_handler(self, message_name, func):
        self.message_handlers[message_name] = func

    def get_message_handler(self, message_name):
        return self.message_handlers.get(message_name)

jet = JetAdmin()
