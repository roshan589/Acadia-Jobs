from django.apps import AppConfig


class LoginsignupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loginSignup'
    def ready(self):
        import loginSignup.signals  # import signals so Django registers them




