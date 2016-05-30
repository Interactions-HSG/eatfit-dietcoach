"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext
from datetime import datetime
from trustbox_connector import *
from TrustBoxAPI import database, tasks, reebate_connector

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

def test_reebate(request):
    reebate_connector.get_customer_trace()
    return HttpResponse("ok")

def reebate_excel_to_db(request):
    reebate_connector.excel_trace_to_db()
    return HttpResponse("ok")

