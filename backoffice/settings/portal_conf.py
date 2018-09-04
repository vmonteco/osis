from collections.__init__ import namedtuple

from django.utils.translation import ugettext_lazy as _

# the parameter labels is a list of string and tuple
# labels=['welcome_introduction',
#         ('caap', 'specific,custom')]
# second parameter can have few values:
# specific
# common
# specific,common
# Used base.views.education_groups.detail.EducationGroupGeneralInformation#get_sections_with_translated_labels
Section = namedtuple('Section', 'title labels')

SECTION_LIST = [
    Section(title=_('Teaching profile'),
            labels=[
                ('welcome_introduction', 'specific'),
                ('welcome_profil', 'specific'),
                ('welcome_job', 'specific'),
                ('welcome_programme', 'specific'),
                ('welcome_parcours', 'specific'),
                ('comp_acquis', 'specific'),
                ('structure', 'specific')
            ]),
    Section(title=_('Detailed programme'),
            labels=[
                ('options', 'specific'),
                ('finalites_didactiques', 'common'),
                ('caap', 'specific,common'),
             ]),
    Section(title=_('Admission'),
            labels=[
                ('module_complementaire', 'specific,custom')
            ]),
    Section(title=_('Benefits and organization'),
            labels=[
                ('pedagogie', 'specific'),
                ('evaluation', 'specific'),
                ('mobilite', 'specific'),
                ('formations_accessibles', 'specific'),
                ('certificats', 'specific')
            ]),
    Section(title=_('In practice'),
            labels=[
                ('contacts', 'specific')
            ]),
]