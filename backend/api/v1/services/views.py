import os

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class DownloadLogView(APIView):
    """Скачивание файла error.log."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'error.log')

        if os.path.exists(log_file_path):
            with open(log_file_path, 'rb') as file:
                response = Response(file.read(), content_type='text/plain')
                response['Content-Disposition'] = (
                    'attachment; filename=error.log'
                )
                return response

        return Response(
            {'error': 'Файл не найден.'},
            status=status.HTTP_404_NOT_FOUND
        )
