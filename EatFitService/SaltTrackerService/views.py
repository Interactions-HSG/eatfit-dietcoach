from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponse
from SaltTrackerService import reebate_connector
from django.contrib.auth.decorators import login_required
from SaltTrackerService import result_calculation
import datetime
from SaltTrackerService.models import SaltTrackerUser


def get_shopping_results(request, user_pk):
    user = get_object_or_404(SaltTrackerUser.objects.using("salttracker").all(), pk=user_pk)
    result_calculation.calculate_shopping_results(user)
    return HttpResponse("ok")
