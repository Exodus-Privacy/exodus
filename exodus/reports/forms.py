from django import forms
from django.http import Http404

from trackers.models import Tracker


class TrackerForm(forms.Form):
    try:
        trackers = Tracker.objects.order_by('name')
    except Tracker.DoesNotExist:
        raise Http404("trackers does not exist")

    options = []
    for t in trackers:
        options.append((t.id, t.name))

    trackers = forms.MultipleChoiceField(choices=options)
