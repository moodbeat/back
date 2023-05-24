from rest_framework.routers import DefaultRouter


class OptionalSlashRouter(DefaultRouter):
    # https://stackoverflow.com/questions/46163838/

    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'
