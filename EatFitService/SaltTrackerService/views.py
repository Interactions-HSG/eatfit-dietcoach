from django.shortcuts import render
from django.http.response import HttpResponse
from SaltTrackerService.models import SaltTrackerUser, MigrosItem
from SaltTrackerService import reebate_connector
from django.contrib.auth.decorators import login_required

@login_required
def test(request):
    reebate_connector.fill_db()
    return HttpResponse("")