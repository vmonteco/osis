from django.views.generic import DetailView

from base.models.learning_unit_year import LearningUnitYear


class LearningUnitUtilization(DetailView):
    model = LearningUnitYear
    template_name = "education_group/learning_unit/tab_utilization.html"

    pk_url_kwarg = 'learning_unit_year_id'