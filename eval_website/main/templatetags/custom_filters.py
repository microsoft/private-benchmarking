# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from django import template

register = template.Library()

@register.filter(name='get_range')
def get_range(value):
    return range(1, value + 1)
