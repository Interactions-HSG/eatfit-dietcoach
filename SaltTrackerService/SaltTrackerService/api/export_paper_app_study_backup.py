import xlsxwriter
from api.models import FoodRecord, StudyDay, SaltTrackerUser, FoodRecordSupplement
import xlrd
from datetime import datetime
import hashlib


NUMBER_OF_STUDY_DAYS = 3

def export_to_excel(output, path_to_input):
    user_list = __get_users_and_dates(path_to_input)
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Results')
    column = 0
    style = wb.add_format()
    style.set_bold(True)
    style.set_align("center")
    ws.write(0,0, "User", style)
    ws.write(0,1, "Date", style)
    ws.write(0,2, "Method", style)
    ws.write(0,3, "Meal", style)
    ws.write(0,4, "FoodItem", style)
    ws.write(0,5, "RedCapID", style)
    ws.write(0,6, "Sodium in mg per 100g", style)
    ws.write(0,7, "Reference Portion in g", style)
    ws.write(0,8, "Quantity", style)
    row = 1
    for user in user_list:
        matching_users = SaltTrackerUser.objects.filter(user__username = user["username"])
        if matching_users.exists():
            print("user exists")
            username = matching_users[0].user.username
            hashed_username = __hash_user_name(username)
            food_record_dict = {}
            food_records = FoodRecord.objects.filter(user=matching_users[0].user.pk, date__in=user["dates"]).select_related("food_item").order_by("date")
            food_records_supplements = FoodRecordSupplement.objects.filter(food_record__user=matching_users[0].user.pk, food_record__date__in=user["dates"]).select_related("food_item_supplement").order_by("date")
            for food_record in food_records:
                if not food_record.date in food_record_dict:
                    food_record_dict[food_record.date] =  []
                food_record_dict[food_record.date].append(food_record)
            for date in food_record_dict:
                for record in food_record_dict[date]:
                    #ws.set_column(column, column + 1, 30)
                    ws.write(row,column, hashed_username)
                    ws.write(row,column+1, str(date))
                    ws.write(row,column+2, "appFRCL")
                    ws.write(row, column+3, record.daytime)
                    ws.write(row, column+4, record.food_item.name)
                    ws.write(row, column +5, record.food_item.red_cap_id)
                    ws.write(row, column+6, record.food_item.sodium)
                    ws.write(row, column+7, record.food_item.reference_portion)
                    ws.write(row, column+8, record.numberOfPortions)
                    row = row + 1
                    supplements = FoodRecordSupplement.objects.filter(food_record=record).select_related("food_item_supplement")
                    if supplements.exists():
                        for supplement in supplements:
                            ws.write(row,column, hashed_username)
                            ws.write(row,column+1, str(date))
                            ws.write(row,column+2, "appFRCL")
                            ws.write(row, column+3, record.daytime)
                            ws.write(row, column+4, supplement.food_item_supplement.name)
                            ws.write(row, column +5, supplement.food_item_supplement.red_cap_id)
                            ws.write(row, column+6, supplement.food_item_supplement.sodium)
                            ws.write(row, column+7, supplement.food_item_supplement.reference_portion)
                            ws.write(row, column+8, record.numberOfPortions)
                            row = row + 1
        else:
            print("user does not exist: " + user["username"])
        
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

def __hash_user_name(username):
    hash_object = hashlib.sha1(username)
    hex_dig = hash_object.hexdigest()
    return hex_dig