from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, F, IntegerField, Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.v1.metrics.filters import (ActivityAverageFilter,
                                    CompletedSurveyFilter, ConditionFilter)
from api.v1.metrics.serializers import (ActivityAverageSerializer,
                                        ActivityTrackerCreateSerializer,
                                        ActivityTrackerSerializer,
                                        ActivityTypeSerializer,
                                        BurnoutSerializer,
                                        CompletedSurveyCreateSerializer,
                                        CompletedSurveySerializer,
                                        ConditionReadSerializer,
                                        ConditionWriteSerializer,
                                        LifeBalanceCreateSerializer,
                                        LifeBalanceSerializer,
                                        LifeDirectionSerializer,
                                        MentalStateReadSerializer,
                                        MonthlyBurnoutSerializer,
                                        ShortSurveySerializer,
                                        SurveySerializer)
from api.v1.permissions import (ChiefSafePermission, EmployeeSafePermission,
                                HRAllPermission)
from metrics.models import (ActivityRate, ActivityTracker, ActivityType,
                            BurnoutTracker, CompletedSurvey, Condition,
                            LifeDirection, Survey, UserLifeBalance)
from users.models import MentalState

from .filters import ActivityFilter, SurveyFilter

User = get_user_model()


@method_decorator(name='create', decorator=swagger_auto_schema(
    responses={status.HTTP_201_CREATED: ConditionReadSerializer},
))
class ConditionViewSet(ModelViewSet):
    queryset = Condition.objects.select_related('employee').all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ConditionFilter
    http_method_names = ('get', 'post',)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConditionReadSerializer
        return ConditionWriteSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (HRAllPermission,)
            my_conditions = self.request.query_params.get('my_conditions')
            if my_conditions:
                self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class LifeDirectionListView(ListAPIView):
    queryset = LifeDirection.objects.all()
    serializer_class = LifeDirectionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class BurnoutViewSet(ModelViewSet):
    queryset = BurnoutTracker.objects.select_related(
        'employee', 'mental_state'
    ).all()
    serializer_class = BurnoutSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('employee', 'mental_state')
    http_method_names = ('get',)
    permission_classes = [
        HRAllPermission | EmployeeSafePermission | ChiefSafePermission
    ]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_hr:
            return BurnoutTracker.objects.select_related(
                'employee', 'mental_state').all()
        return BurnoutTracker.objects.filter(
            employee=self.request.user.id).select_related(
            'employee', 'mental_state')

    def get_yearly_burnout_percentage(self, queryset):
        now = timezone.now()
        queryset = queryset.filter(date__year=(now.year))

        month_names = {
            1: 'янв',
            2: 'фев',
            3: 'март',
            4: 'апр',
            5: 'май',
            6: 'июнь',
            7: 'июль',
            8: 'авг',
            9: 'сент',
            10: 'окт',
            11: 'ноя',
            12: 'дек',
        }

        serialized_data = []

        for month in range(1, 13):
            filtered_queryset = queryset.filter(date__month=month)
            count_by_level = (
                filtered_queryset
                .values('mental_state__level')
                .annotate(count=Count('id'))
            )
            total_count = sum(item['count'] for item in count_by_level)
            percentage = {
                1: 0,
                2: 50,
                3: 100,
            }
            burnout_percentage = 0.0
            if total_count > 0:
                burnout_percentage = sum(
                    percentage[item['mental_state__level']] * item['count']
                    for item in count_by_level) / total_count
            month_name = month_names[month]
            serialized_data.append({
                'month': month_name,
                'percentage': burnout_percentage
            })

        return serialized_data

    @swagger_auto_schema(responses={
        status.HTTP_200_OK: MonthlyBurnoutSerializer(many=True)
    })
    @action(
        detail=False,
        methods=['get'],
        url_path='graph_data',
        serializer_class=MonthlyBurnoutSerializer
    )
    def graph_data(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if self.request.user.is_authenticated and self.request.user.is_hr:
            burnout_data = self.get_yearly_burnout_percentage(queryset)
        else:
            filtered_queryset = queryset.filter(employee=self.request.user.id)
            burnout_data = self.get_yearly_burnout_percentage(
                filtered_queryset
            )

        return Response(self.get_serializer(burnout_data, many=True).data)


@method_decorator(name='create', decorator=swagger_auto_schema(
    responses={status.HTTP_201_CREATED: LifeBalanceCreateSerializer},
))
class LifeBalanceViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ('get', 'post',)
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('employee', 'set_priority',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LifeBalanceSerializer
        return LifeBalanceCreateSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_hr:
            return UserLifeBalance.objects.all()
        return UserLifeBalance.objects.filter(employee=self.request.user.id)


@swagger_auto_schema(responses={status.HTTP_200_OK: SurveySerializer})
class SurveyViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SurveyFilter
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)
    serializer_class = ShortSurveySerializer
    detail_serializer_class = SurveySerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None

        queryset = (
            Survey.objects
            .filter(
                Q(author=self.request.user)
                | Q(for_all=True)
                | Q(department=self.request.user.department)
            )
            .select_related('author', 'type')
            .prefetch_related('department', 'questions')
        )

        return queryset.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class

        return super(SurveyViewSet, self).get_serializer_class()


@method_decorator(name='create', decorator=swagger_auto_schema(
    responses={status.HTTP_201_CREATED: CompletedSurveySerializer}
))
class CompletedSurveyViewSet(ModelViewSet):
    queryset = CompletedSurvey.objects.select_related(
        'employee', 'survey', 'mental_state'
    ).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CompletedSurveyFilter
    http_method_names = ('get', 'post',)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (HRAllPermission,)
            my_results = self.request.query_params.get('my_results')
            if my_results:
                self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CompletedSurveySerializer
        return CompletedSurveyCreateSerializer


class MentalStateViewSet(ListAPIView):
    queryset = MentalState.objects.all()
    pagination_class = None
    serializer_class = MentalStateReadSerializer
    permission_classes = (IsAuthenticated,)


class ActivityTypeListView(ListAPIView):
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None


@method_decorator(name='create', decorator=swagger_auto_schema(
    responses={status.HTTP_201_CREATED: ActivityTrackerSerializer},
))
class ActivityViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ActivityFilter
    http_method_names = ('get', 'post',)
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('employee',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ActivityTrackerSerializer
        return ActivityTrackerCreateSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_hr:
            return (
                ActivityTracker.objects
                .select_related('employee')
                .prefetch_related('activity_rates')
                .all()
            )
        return (
            ActivityTracker.objects
            .filter(employee=self.request.user.id)
            .select_related('employee')
            .prefetch_related('activity_rates')
        )


class ActivityAveragePercentageViewSet(ModelViewSet):
    queryset = ActivityRate.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ActivityAverageFilter
    serializer_class = ActivityAverageSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get',)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        average_percentages = (
            queryset
            .values(type_name=F('type__name'))
            .annotate(average_percentage=(Avg(
                'percentage', output_field=IntegerField()
            )))
            .order_by('type__key', 'type__id')
        )

        return Response(average_percentages, status=status.HTTP_200_OK)

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_hr:
            return self.queryset
        return self.queryset.filter(tracker__employee=self.request.user.id)

# оставлю пока не дойду то эндпоинтов конструктора
#     def perform_create(self, serializer):
#         questions_list = serializer.validated_data.pop('questions')
#         instance = serializer.save(author=self.request.user)
#         Question.objects.bulk_create(
#             Question(
#                 survey=instance, text=obj['text']
#             ) for obj in questions_list
#         )

#     def perform_update(self, serializer):
#         questions_list = serializer.validated_data.pop('questions', None)
#         instance = serializer.save()
#         if questions_list:
#             Question.objects.bulk_create(
#                 Question(
#                     survey=instance, text=obj['text']
#                 ) for obj in questions_list
#             )
