from abc import ABC, abstractmethod
from math import sqrt

from .models import MentalState, Question


class BaseCalculate(ABC):

    def __init__(self, instance: object):
        self.instance = instance
        self.values = [i['variant_value'] for i in self.instance.results]
        self.questions = Question.objects.filter(
            id__in=[i['question_id'] for i in self.instance.results]
        )

    @staticmethod
    def level_words(
        level: int,
        reverse: bool = False,
        endings: int = 1
    ) -> str:
        """
        Определяет текст шкалы в зависимости от уровня выгорания.

        Args:
            level (int): уровень выгорания.
            reverse (bool, optional): в обратном порядке. Defaults to False.
            endings (int, optional): 1 муж. род, 2 жен. род, 3 ср. род.
            Defaults to 1.

        Returns:
            str: строка с уровнем выгорания.
        """
        words = {
            1: ['низкий', 'низкая', 'низкое'],
            2: ['средний', 'средняя', 'среднее'],
            3: ['высокий', 'высокая', 'высокое']
        }

        if reverse:
            words = {k: v[::-1] for k, v in words.items()}

        return words[level][endings - 1]

    @abstractmethod
    def calculate(self):
        pass


class YesNoCalculate(BaseCalculate):
    """
    Тест с положительными/отрицательными вариантами.

    Подсчет ведется по проценту положительных вариантов.

    Args:
        BaseCalculate (_type_): _description_
    """

    def calculate(self):

        result_in_persent = (
            self.values.count(1) / self.questions.count() * 100
        )
        self.instance.set_mental_state(result_in_persent)


class MBICalculate(BaseCalculate):
    """
    Опросник выгорания Маслач.

    Args:
        BaseCalculate (_type_): _description_
    """

    def calculate(self):

        ee = self.questions.filter(key=1).values_list('id', flat=True)
        ee_max = 6 * ee.count() + 6
        ee_sum = 0

        dp = self.questions.filter(key=2).values_list('id', flat=True)
        dp_max = 6 * dp.count()
        dp_sum = 0

        pa = self.questions.filter(key=3).values_list('id', flat=True)
        pa_max = 6 * pa.count()
        pa_sum = 0

        # по методике 1 вариант инвертирован, ему даем ключ 4
        inverted = self.questions.filter(key=4).values_list('id', flat=True)

        for value in self.instance.results:
            if value['question_id'] in inverted:
                invert = 6 - value['variant_value']
                ee_sum += invert
            if value['question_id'] in ee:
                ee_sum += value['variant_value']
            if value['question_id'] in dp:
                dp_sum += value['variant_value']
            if value['question_id'] in pa:
                pa_sum += value['variant_value']

        index = sqrt(((ee_sum / ee_max)**2 + (dp_sum / dp_max)**2
                      + (1 - pa_sum / pa_max)**2) / 3)
        index = round(index, 2)

        if 0 <= ee_sum <= 15:
            ee_level = 1
        elif 16 <= ee_sum <= 24:
            ee_level = 2
        else:
            ee_level = 3

        if 0 <= dp_sum <= 5:
            dp_level = 1
        elif 6 <= dp_sum <= 10:
            dp_level = 2
        else:
            dp_level = 3

        if 0 <= pa_sum <= 30:
            pa_level = 3
        elif 31 <= pa_sum <= 36:
            pa_level = 2
        else:
            pa_level = 1

        level = max([ee_level, dp_level, pa_level])

        mental_state = MentalState.objects.filter(level=level).first()
        self.instance.mental_state = mental_state
        self.instance.employee.mental_state = mental_state
        self.instance.employee.save()

        graphs_colors = {
            1: 'green',
            2: 'yellow',
            3: 'red'
        }

        # TODO это в отдельную функцию
        summary = {
            "graphs": [
                {
                    "title": "Значение индекса системного выгорания",
                    "size": "big",
                    "color": "blue",
                    "value": index,
                    "min_value": 0,
                    "max_value": 1
                },
                {
                    "title": "Эмоциональное истощение",
                    "text": self.level_words(level=ee_level, endings=3),
                    "size": "medium",
                    "color": graphs_colors[ee_level],
                    "value": ee_sum,
                    "min_value": 0,
                    "max_value": ee_max
                },
                {
                    "title": "Личностное отдаление",
                    "text": self.level_words(level=dp_level, endings=3),
                    "size": "medium",
                    "color": graphs_colors[dp_level],
                    "value": dp_sum,
                    "min_value": 0,
                    "max_value": dp_max
                },
                {
                    "title": "Редукция личных достижений",
                    "text": self.level_words(
                        level=pa_level,
                        reverse=True,
                        endings=2
                    ),
                    "size": "medium",
                    "color": graphs_colors[pa_level],
                    "value": pa_sum,
                    "min_value": 0,
                    "max_value": pa_max
                },
            ]
        }
        self.instance.summary = summary
