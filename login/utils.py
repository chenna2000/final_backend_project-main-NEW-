from django.contrib.auth import get_user_model # type: ignore
from django.http import JsonResponse # type: ignore
from googleapiclient.discovery import build # type: ignore
from google.oauth2.service_account import Credentials # type: ignore
from datetime import datetime

# Determine the base directory
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Path to the service account key file
# SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'collegecue-910d0-firebase-adminsdk-bvx8y-971424b217.json')

SERVICE_ACCOUNT_FILE = "D:\\BHARATHTECH TASKS\\collegcue-firebase-adminsdk-p63yc-498e419897.json"


# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate using the service account
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of the spreadsheet to update
SPREADSHEET_ID = '1X5ZlDRLaMs4uxLQ4VjP9bYV7IiDHIzyex_70XMzZZr0'

def create_subadmin(username, password):
    User = get_user_model()
    user = User.objects.create_user(username=username, password=password)
    user.is_staff = True
    user.is_superuser = False
    user.is_subadmin = True
    user.save()
    return user

def is_superadmin(user):
    return user.is_superuser 

def send_data_to_google_sheets(first_name, last_name, email, country_code, phone_number, password, sheetname):
    if sheetname != "Sheet1":
        return JsonResponse({'message': "Invalid sheet name"}, safe=False)

    formatted_date = datetime.now().strftime("%d/%m/%Y")

    row_data = [first_name, last_name, email, country_code, phone_number, password, formatted_date]

    body = {'values': [row_data]}
    sheet_range = f"{sheetname}!A1"

    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    updated_cells = result.get('updates', {}).get('updatedCells', 0)
    return JsonResponse({'message': f"{updated_cells} cells updated in {sheetname}."}, safe=False)


def send_data_to_google_sheet2(companyname, officialmale, country_code, mobilenumber, password, linkedinprofile, company_person_name, agreed_to_terms, sheetname):
    if sheetname != "Sheet2":
        return JsonResponse({'message': "Invalid sheet name"}, safe=False)

    formatted_date = datetime.now().strftime("%d/%m/%Y")

    row_data = [
        companyname, officialmale, country_code, mobilenumber, password,
        linkedinprofile, company_person_name, agreed_to_terms, formatted_date
    ]
    sheet_range = f"{sheetname}!A1"
    body = {'values': [row_data]}

    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    updated_cells = result.get('updates', {}).get('updatedCells', 0)
    return JsonResponse({'message': f"{updated_cells} cells updated in {sheetname}."}, safe=False)


def send_data_to_google_sheet3(university, officialmale, country_code, mobilenumber, password, linkedinprofile, college_person_name, agreed_to_terms, sheetname):
    if sheetname != "Sheet3":
        return JsonResponse({'message': "Invalid sheet name"}, safe=False)

    formatted_date = datetime.now().strftime("%d/%m/%Y")

    row_data = [
        university, officialmale, country_code, mobilenumber, password,
        linkedinprofile, college_person_name, agreed_to_terms, formatted_date
    ]
    sheet_range = f"{sheetname}!A1"
    body = {'values': [row_data]}

    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    updated_cells = result.get('updates', {}).get('updatedCells', 0)
    return JsonResponse({'message': f"{updated_cells} cells updated in {sheetname}."}, safe=False)


def send_data_to_google_sheet4(consultant_name, official_email, country_code, mobile_number, password, linkedin_profile, consultant_person_name, agreed_to_terms, sheetName):
    if sheetName != "Sheet4":
        return JsonResponse({'message': "Invalid sheet name"}, safe=False)

    formatted_date = datetime.now().strftime("%d/%m/%Y")

    row_data = [
        consultant_name, official_email, country_code, mobile_number, password,
        linkedin_profile, consultant_person_name, agreed_to_terms, formatted_date
    ]
    sheet_range = f"{sheetName}!A1"
    body = {'values': [row_data]}

    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    updated_cells = result.get('updates', {}).get('updatedCells', 0)
    return JsonResponse({'message': f"{updated_cells} cells updated in {sheetName}."}, safe=False)


def send_data_to_google_sheet5(first_name, last_name, email, country_code, mobile_number, password, agreed_to_terms, sheetname):
    if sheetname != "Sheet5":
        return JsonResponse({'message': "Invalid sheet name"}, safe=False)

    formatted_date = datetime.now().strftime("%d/%m/%Y")

    row_data = [
        first_name, last_name, email, country_code, mobile_number,
        password, agreed_to_terms, formatted_date
    ]
    sheet_range = f"{sheetname}!A1"

    body = {'values': [row_data]}

    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    updated_cells = result.get('updates', {}).get('updatedCells', 0)
    return JsonResponse({'message': f"{updated_cells} cells updated in {sheetname}."}, safe=False)


def send_data_to_google_sheet6(university, officialmale, country_code, mobilenumber, password, linkedinprofile, college_person_name, agreed_to_terms, sheetname):
    if sheetname != "Sheet6":
        return JsonResponse({'message': "Invalid sheet name"}, safe=False)

    formatted_date = datetime.now().strftime("%d/%m/%Y")

    row_data = [
        university, officialmale, country_code, mobilenumber, password,
        linkedinprofile, college_person_name, agreed_to_terms, formatted_date
    ]
    sheet_range = f"{sheetname}!A1"
    body = {'values': [row_data]}

    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    updated_cells = result.get('updates', {}).get('updatedCells', 0)
    return JsonResponse({'message': f"{updated_cells} cells updated in {sheetname}."}, safe=False)



