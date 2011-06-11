# Separated criteria and criteria_objects to prevent cyclic import:
# PaymentMethod -> CriteriaObjects | PaymentCriteria -> PaymentMethod
from criteria import *
from criteria_objects import *
