from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from socials.models import HelpType

from .serializers import (HelpTypeSerializer, NeedHelpSerializer,
                          SpecialistsSerializer)
from .utils import user_param

User = get_user_model()


class HelpViewSet(APIView):

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: HelpTypeSerializer},
        manual_parameters=[user_param]
    )
    def get(self, request):
        queryset = HelpType.objects.all()
        user_id = self.request.query_params.get('user')

        if user_id:
            queryset = queryset.filter(role__isnull=True)
            try:
                user = User.objects.get(id=user_id)

                if not user.is_hr and not user.is_chief:
                    data = {
                        'detail': ('Запрашиваемый пользователь должен быть '
                                   'Руководителем или HR.')
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

                role = user.role
                queryset = queryset | HelpType.objects.filter(role=role)
            except User.DoesNotExist:
                data = {'detail': 'Пользователь не найден.'}
                return Response(data, status=status.HTTP_404_NOT_FOUND)

        serializer = HelpTypeSerializer(queryset, many=True)
        return Response(serializer.data)


class SpecialistsView(APIView):

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: SpecialistsSerializer},
    )
    def get(self, request):
        user = self.request.user
        if user.is_employee:
            queryset = User.objects.filter(
                Q(role='hr') | Q(role='chief') & Q(department=user.department)
            ).exclude(id=user.id)
        else:
            queryset = User.objects.filter(role='hr').exclude(id=user.id)
        serializer = SpecialistsSerializer(queryset, many=True)
        return Response(serializer.data)


class NeedHelpView(APIView):

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: NeedHelpSerializer},
        request_body=NeedHelpSerializer
    )
    def post(self, request):
        serializer = NeedHelpSerializer(
            data=request.data,
            context={'request': request._request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
