from django.utils.translation import gettext_lazy as _

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
    (EQUAL, _("Equal to")),
    (LESS_THAN, _("Less than")),
    (LESS_THAN_EQUAL, _("Less than or equal to")),
    (GREATER_THAN, _("Greater than")),
    (GREATER_THAN_EQUAL, _("Greater than or equal to")),
)

STRING_OPERATORS = (
    (EQUAL, _("Equal to")),
    (CONTAIN, _("Contain")),
)

SELECT_OPERATORS = (
    (IS, _("Is")),
    (IS_NOT, _("Is not")),
    (IS_VALID, _("Is valid")),
    (IS_NOT_VALID, _("Is not valid")),
)
