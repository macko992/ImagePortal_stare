from django.apps import AppConfig


class ImagesConfig(AppConfig):
    name = 'images'
    verbose_name = 'Dodawanie obrazów'

    def ready(self):
        #import procedury sygnalow
        import images.signals
