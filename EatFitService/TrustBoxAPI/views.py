"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext
from datetime import datetime
from trustbox_connector import *
from TrustBoxAPI import database, tasks

#database.setup_database() 

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def test_celery(request):
    tasks.add.delay(4,5)
    return HttpResponse("ok")

def fill_db(request):
    load_changed_data()
    return HttpResponse("asdasd")

