from django.shortcuts import render
from django.http.response import HttpResponse
from SaltTrackerService.models import SaltTrackerUser, MigrosItem
from SaltTrackerService import reebate_connector


def test(request):
    #reebate_connector.fill_db()
    migros_items_list = MigrosItem.objects.using("salttracker").all()
    return HttpResponse("ok")