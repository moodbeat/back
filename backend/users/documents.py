from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from .models import Hobby


@registry.register_document
class HobbyDocument(Document):

    class Index:
        name = 'hobbies'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Hobby

        fields = [
            'name',
        ]
