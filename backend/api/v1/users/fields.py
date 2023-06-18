import base64
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            image = Image.open(BytesIO(base64.b64decode(imgstr)))

            max_size = (600, 600)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.ANTIALIAS)

            output = BytesIO()
            image.save(output, format=ext)
            output.seek(0)
            data = ContentFile(output.read(), name='temp.' + ext)
        return super().to_internal_value(data)
