from django.utils.translation import ugettext_lazy as _

EQUAL = 0
LESS_THAN = 1
LESS_THAN_EQUAL = 2
GREATER_THAN = 3
GREATER_THAN_EQUAL = 4
CONTAIN = 5

IS = 10
IS_NOT = 11
IS_VALID = 12
IS_NOT_VALID = 13

NUMBER_OPERATORS = (
    (EQUAL, _(u"Equal to")),
    (LESS_THAN, _(u"Less than")),
    (LESS_THAN_EQUAL, _(u"Less than or equal to")),
    (GREATER_THAN, _(u"Greater than")),
    (GREATER_THAN_EQUAL, _(u"Greater than or equal to")),
)

STRING_OPERATORS = (
    (EQUAL, _(u"Equal to")),
    (CONTAIN, _(u"Contain")),
)

SELECT_OPERATORS = (
    (IS, _(u"Is")),
    (IS_NOT, _(u"Is not")),
    (IS_VALID, _(u"Is valid")),
    (IS_NOT_VALID, _(u"Is not valid")),
)
