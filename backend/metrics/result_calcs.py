from math import sqrt

from .models import MentalState, Question


class YesNoCalculate:

    def calculate_results(self, instance):

        values = [item['variant_value'] for item in instance.results]
        result_in_persent = (
            values.count(1) / instance.survey.questions.count() * 100
        )
        instance.set_mental_state(result_in_persent)


class MBICalculate:

    def calculate_results(self, instance):

        # https://psylab.info/Опросник_выгорания_Маслач
        questions = [item['question_id'] for item in instance.results]
        questions = Question.objects.filter(id__in=questions)

        ee = questions.filter(key=1).values_list('id', flat=True)
        ee_max = 6 * ee.count() + 6
        ee_sum = 0
        dp = questions.filter(key=2).values_list('id', flat=True)
        dp_max = 6 * dp.count()
        dp_sum = 0
        pa = questions.filter(key=3).values_list('id', flat=True)
        pa_max = 6 * pa.count()
        pa_sum = 0

        # по методике 1 вариант инвертирован, ему даем ключ 4
        inverted = questions.filter(key=4).values_list('id', flat=True)

        for value in instance.results:
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
        instance.mental_state = mental_state
        instance.employee.mental_state = mental_state
        instance.employee.save()

        graphs_colors = {
            1: 'green',
            2: 'yellow',
            3: 'red'
        }

        summary = {
            "graphs": [
                {
                    "title": "Значение индекса системного выгорания",
                    "size": "big", "color": "blue", "value": index,
                    "min_value": 0, "max_value": 1
                },
                {
                    "title": "Эмоциональное истощение",
                    "size": "medium", "color": graphs_colors[ee_level],
                    "value": ee_sum, "min_value": 0, "max_value": ee_max
                },
                {
                    "title": "Деперсонализация",
                    "size": "medium", "color": graphs_colors[dp_level],
                    "value": dp_sum, "min_value": 0, "max_value": dp_max
                },
                {
                    "title": "Редукция проф.достижений",
                    "size": "medium", "color": graphs_colors[pa_level],
                    "value": pa_sum, "min_value": 0, "max_value": pa_max
                },
            ]
        }
        instance.summary = summary
