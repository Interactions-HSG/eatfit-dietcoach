import xlsxwriter
import os
from SaltTrackerService.settings import STATIC_ROOT
from api.models import ProfileData
from api.models import FoodRecord, StudyDay, SaltTrackerUser, FoodRecordSupplement
import xlrd
from datetime import datetime
import hashlib


NUMBER_OF_STUDY_DAYS = 4
ADDED_SALT_CATEGORY_NAME = "Nachsalzen"
FOODTRACKER_PROFILE_DATA_KEYS = []


def export_user_demographics(output, path_to_input, wb = None, user_list = None):
    if not user_list:
        user_list = __get_users(path_to_input)
    if not wb:
        wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('User Demographics')
    column = 0
    style = wb.add_format()
    style.set_bold(True)
    style.set_align("center")
    ws.write(0,0, "User", style)
    ws.write(0,1, "UserHash", style)
    ws.write(0,2, "Nickname", style)
    ws.write(0,3, "Birthyear", style)
    ws.write(0,4, "Weight", style)
    ws.write(0,5, "Height", style)
    ws.write(0,6, "Gender", style)
    row = 1
    matching_users = SaltTrackerUser.objects.filter(user__username__in = user_list)
    for user in matching_users:
        print("user exists")
        username = user.user.username
        hashed_username = __hash_user_name(username)
        ws.write(row,column, username)
        ws.write(row,column+1, hashed_username)
        ws.write(row,column+2, user.nickname)
        ws.write(row,column+3, user.date_of_birth.year)
        ws.write(row,column+4, round(user.weight, 1))
        ws.write(row,column+5, round(user.height, 1))
        ws.write(row,column+6, user.sex)
        row = row + 1
    return wb

def export_user_data_food_tracker(output, path_to_input):
    user_list = __get_users(path_to_input)
    FOODTRACKER_PROFILE_DATA_KEYS = __read_food_tracker_profile_data_keys()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('User Surveys')
    ws.set_column(0, 200, 30)
    style = wb.add_format()
    style.set_bold(True)
    style.set_align("center")
    ws.write(0,0, "User", style)
    ws.write(0,1, "UserHash", style)
    ws.write(0,2, "Name", style)
    ws.write(0,3, "DateOfBirth", style)
    ws.write(0,4, "Gender", style)
    ws.write(0,5, "Weight", style)
    ws.write(0,6, "Height", style)
    column = 6
    for profile_data_key in FOODTRACKER_PROFILE_DATA_KEYS:
        ws.write(0, column, profile_data_key, style)
        column = column + 1
    matching_users = SaltTrackerUser.objects.filter(user__username__in = user_list).prefetch_related("user__profiledata_set")
    row = 1
    for user in matching_users:
        column = 0
        username = user.user.username
        hashed_username = __hash_user_name(username)
        ws.write(row, column, username)
        ws.write(row, column+1, hashed_username)
        ws.write(row, column+2, user.nickname)
        ws.write(row, column+3, user.date_of_birth.year)
        ws.write(row, column+4, user.sex)
        ws.write(row, column+5, round(user.weight, 1))
        ws.write(row, column+6, round(user.height, 1))
        profile_data_entries = __prepare_profile_data(user.user)
        column = 6
        for profile_data_key in FOODTRACKER_PROFILE_DATA_KEYS:
            __write_profile_data_entry(profile_data_entries, profile_data_key, ws, row, column)
            column = column + 1
        row = row + 1
    return wb

def export_user_surveys(output, path_to_input, profile_data_type, wb = None, user_list = None):
    if not user_list:
        user_list = __get_users(path_to_input)
    if not wb:
        wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('User Surveys')
    column = 0
    style = wb.add_format()
    style.set_bold(True)
    style.set_align("center")
    ws.write(0,0, "User", style)
    ws.write(0,1, "UserHash", style)
    ws.write(0,2, "Profile Data Key", style)
    ws.write(0,3, "Profile Data Value", style)
    ws.write(0,4, "Category", style)
    row = 1
    matching_users = SaltTrackerUser.objects.filter(user__username__in = user_list).prefetch_related("user__profiledata_set")
    for user in matching_users:
        print("user exists")
        username = user.user.username
        hashed_username = __hash_user_name(username)
        for profile_data in user.user.profiledata_set.all():
            if profile_data.profile_data_type == profile_data_type:
                ws.write(row,column, username)
                ws.write(row,column+1, hashed_username)
                ws.write(row,column+2, profile_data.name)
                ws.write(row,column+3, profile_data.value)
                ws.write(row,column+4, profile_data.profile_data_type)
                row = row + 1
    return wb

def export_added_salt(output, path_to_input, wb = None, user_list = None):
    if not user_list:
        user_list = __get_users(path_to_input)
    if not wb:
        wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Added Salt')
    column = 0
    style = wb.add_format()
    style.set_bold(True)
    style.set_align("center")
    ws.write(0,0, "User", style)
    ws.write(0,1, "UserHash", style)
    ws.write(0,2, "Date", style)
    ws.write(0,3, "Meal", style)
    ws.write(0,4, "Added", style)
    row = 1
    matching_users = SaltTrackerUser.objects.filter(user__username__in = user_list)
    for user in matching_users:
        print("user exists")
        hashed_username = __hash_user_name(user.user.username)
        food_records = FoodRecord.objects.filter(user=user.user, food_item__category__name = ADDED_SALT_CATEGORY_NAME).select_related("food_item").order_by("date")
        for food_record in food_records:
             ws.write(row,column, user.user.username)
             ws.write(row,column+1, hashed_username)
             ws.write(row,column+2, str(food_record.date))
             ws.write(row,column+3, food_record.daytime)
             ws.write(row,column+4, food_record.food_item.name)
             row = row + 1
    return wb

def export_to_excel(output, path_to_input, wb = None, user_list = None):
    if not user_list:
        user_list = __get_users(path_to_input)
    if not wb:
        wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Results')
    column = 0
    style = wb.add_format()
    style.set_bold(True)
    style.set_align("center")
    ws.write(0,0, "User", style)
    ws.write(0,1, "UserHash", style)
    ws.write(0,2, "Date", style)
    ws.write(0,3, "Day_Number", style)
    ws.write(0,4, "Method", style)
    ws.write(0,5, "Meal", style)
    ws.write(0,6, "FoodItem", style)
    ws.write(0,7, "RedCapID", style)
    ws.write(0,8, "Sodium in mg per 100g", style)
    ws.write(0,9, "Reference Portion in g", style)
    ws.write(0,10, "Quantity", style)
    row = 1
    for user in user_list:
        matching_users = SaltTrackerUser.objects.filter(user__username = user)
        if matching_users.exists():
            print("user exists")
            username = matching_users[0].user.username
            hashed_username = __hash_user_name(username)
            food_record_dict = {}
            food_records = FoodRecord.objects.filter(user=matching_users[0].user.pk).select_related("food_item").order_by("date")
            food_records_supplements = FoodRecordSupplement.objects.filter(food_record__user=matching_users[0].user.pk).select_related("food_item_supplement").order_by("date")
            for food_record in food_records:
                if not food_record.date in food_record_dict:
                    food_record_dict[food_record.date] =  []
                food_record_dict[food_record.date].append(food_record)
            day_count = 0
            for date in food_record_dict:
                day_count = day_count + 1
                for record in food_record_dict[date]:
                    #ws.set_column(column, column + 1, 30)
                    ws.write(row,column, username)
                    ws.write(row,column+1, hashed_username)
                    ws.write(row,column+2, str(date))
                    ws.write(row,column+3, day_count)
                    ws.write(row,column+4, "appFRCL")
                    ws.write(row, column+5, record.daytime)
                    ws.write(row, column+6, record.food_item.name)
                    ws.write(row, column+7, record.food_item.red_cap_id)
                    ws.write(row, column+8, record.food_item.sodium)
                    ws.write(row, column+9, record.food_item.reference_portion)
                    ws.write(row, column+10, record.numberOfPortions)
                    row = row + 1
                    supplements = FoodRecordSupplement.objects.filter(food_record=record).select_related("food_item_supplement")
                    if supplements.exists():
                        for supplement in supplements:
                            ws.write(row,column, username)
                            ws.write(row,column+1, hashed_username)
                            ws.write(row,column+2, str(date))
                            ws.write(row,column+3, day_count)
                            ws.write(row,column+4, "appFRCL")
                            ws.write(row, column+5, record.daytime)
                            ws.write(row, column+6, supplement.food_item_supplement.name)
                            ws.write(row, column+7, supplement.food_item_supplement.red_cap_id)
                            ws.write(row, column+8, supplement.food_item_supplement.sodium)
                            ws.write(row, column+9, supplement.food_item_supplement.reference_portion)
                            ws.write(row, column+10, record.numberOfPortions)
                            row = row + 1
        else:
            print("user does not exist: " + user)
        
    return wb

def __get_users_and_dates(input_path):
    user_list = []
    xl_workbook = xlrd.open_workbook(file_contents=input_path.read())
    xl_sheet = xl_workbook.sheet_by_index(0)
    for row in range(0, xl_sheet.nrows):
        user_dict = {}
        user_dict["username"] = xl_sheet.cell_value(row, 0)
        user_dict["dates"] = []
        for column in range(1, NUMBER_OF_STUDY_DAYS+1):
            date_value = xl_sheet.cell_value(row, column)
            date = datetime(*xlrd.xldate_as_tuple(date_value, xl_workbook.datemode))
            user_dict["dates"].append(date.date())
        user_list.append(user_dict)
    return user_list


def __get_users(input_path):
    user_list = []
    xl_workbook = xlrd.open_workbook(file_contents=input_path.read())
    xl_sheet = xl_workbook.sheet_by_index(0)
    for row in range(0, xl_sheet.nrows):
        user_list.append(xl_sheet.cell_value(row, 0))
    xl_workbook.release_resources()
    del xl_workbook
    return user_list

def __hash_user_name(username):
    hash_object = hashlib.sha1(username)
    hex_dig = hash_object.hexdigest()
    return hex_dig

def __prepare_profile_data(user):
    profile_data_entries = {}
    profile_data = ProfileData.objects.filter(user = user)
    for data in profile_data:
        profile_data_entries[data.name] = data.value
    return profile_data_entries

def __write_profile_data_entry(profile_data_entries, key, ws, row, column):
    if key in profile_data_entries:
        if __is_number(key):
            value = int(profile_data_entries[key])
        else:
            value = profile_data_entries[key]
            if value == "False":
                value = 0
            elif value == "True":
                value = 1
    else:
        value =  0
    ws.write(row,column, value)

def __read_food_tracker_profile_data_keys():
    value_list = []
    xl_workbook = xlrd.open_workbook(os.path.join(STATIC_ROOT, 'files/FOODTRACKER_PROFILE_DATA_KEYS.xlsx'))
    xl_sheet = xl_workbook.sheet_by_index(0)
    for row in range(0, xl_sheet.nrows):
        value_list.append(xl_sheet.cell_value(row, 0))
    xl_workbook.release_resources()
    del xl_workbook
    return value_list


def __is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False