from django.shortcuts import render
from django.http.response import HttpResponse
from SaltTrackerService.models import SaltTrackerUser
from SaltTrackerService import reebate_connector


def test(request):
    reebate_connector.fill_db()
    return HttpResponse("")