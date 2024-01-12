# coding: utf-8
from django.conf import settings


REGISTER_FORM = getattr(settings, "LFS_REGISTER_FORM", "lfs.customer.forms.RegisterForm")
