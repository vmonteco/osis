##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from base.forms.search.search_tutor import TutorSearchForm
from base.models.tutor import Tutor
from base.views import layout


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def search_tutors(request):
    tutors_qs = Tutor.objects.none()
    form = TutorSearchForm(data=request.GET)

    if form.is_valid():
        tutors_qs = form.search()

    paginator = Paginator(tutors_qs, 25)

    page = request.GET.get('page')

    try:
        tutors = paginator.page(page)
    except PageNotAnInteger:
        tutors = paginator.page(1)
    except EmptyPage:
        tutors = paginator.page(paginator.num_pages)

    return layout.render(request, "search/search.html", {
        "form": form,
        "tutors": tutors
    })
