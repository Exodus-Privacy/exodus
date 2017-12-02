# coding=utf-8
from django import template
import subprocess as sp

register = template.Library()

hash = sp.check_output(['git', 'rev-parse', '--short', 'HEAD'])

@register.simple_tag(name='commit_hash')
def commit_hash():
    return hash
