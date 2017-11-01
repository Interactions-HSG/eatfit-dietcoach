from django.contrib.auth.decorators import login_required
from api.export_paper_app_study import __get_users
import xlsxwriter
from django.http.response import HttpResponse
from StringIO import StringIO
from api import export_paper_app_study
from rest_framework.decorators import permission_classes, api_view, parser_classes
from rest_framework import permissions, status
from django.shortcuts import render
from datetime import datetime
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

@api_view(['GET', "POST"])
@permission_classes((permissions.IsAuthenticated,))
@parser_classes((MultiPartParser, FormParser))
def paper_salt_study(request):
    if request.user.is_superuser:
        if request.method == "POST":
            output = StringIO()
            xls = export_paper_app_study.export_to_excel(output, request.data["input_excel"])
            xls.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type="application/ms-excel")
            filename = "Results_" + datetime.now().strftime('_%d_%m_%Y') + ".xlsx"
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        else:
            return render(request, "export_paper_app_study.html")
    return HttpResponse(None, status=status.HTTP_403_FORBIDDEN)



@api_view(['GET', "POST"])
@permission_classes((permissions.IsAuthenticated,))
@parser_classes((MultiPartParser, FormParser))
def user_demographics(request):
    if request.user.is_superuser:
        if request.method == "POST":
            output = StringIO()
            xls = export_paper_app_study.export_user_demographics(output, request.data["input_excel"])
            xls.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type="application/ms-excel")
            filename = "User_Demographics" + datetime.now().strftime('_%d_%m_%Y') + ".xlsx"
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        else:
            return render(request, "user_demographics.html")
    return HttpResponse(None, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', "POST"])
@permission_classes((permissions.IsAuthenticated,))
@parser_classes((MultiPartParser, FormParser))
def user_surveys(request):
    if request.user.is_superuser:
        if request.method == "POST":
            output = StringIO()
            xls = export_paper_app_study.export_user_data_food_tracker(output, request.data["input_excel"])
            xls.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type="application/ms-excel")
            filename = "User_Surveys" + datetime.now().strftime('_%d_%m_%Y') + ".xlsx"
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        else:
            return render(request, "user_survey.html")
    return HttpResponse(None, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', "POST"])
@permission_classes((permissions.IsAuthenticated,))
@parser_classes((MultiPartParser, FormParser))
def export_all(request):
    if request.user.is_superuser:
        if request.method == "POST":
            output = StringIO()
            wb = xlsxwriter.Workbook(output)
            user_list = __get_users(request.data["input_excel"])
            export_paper_app_study.export_user_surveys(output, request.data["input_excel"], request.data["profile_data_type"], wb, user_list)
            export_paper_app_study.export_user_demographics(output, request.data["input_excel"], wb, user_list)
            export_paper_app_study.export_to_excel(output, request.data["input_excel"], wb, user_list)
            export_paper_app_study.export_added_salt(output, request.data["input_excel"], wb, user_list)
            wb.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type="application/ms-excel")
            filename = "All_exports" + datetime.now().strftime('_%d_%m_%Y') + ".xlsx"
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        else:
            return render(request, "export_all.html")
    return HttpResponse(None, status=status.HTTP_403_FORBIDDEN)
