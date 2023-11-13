import os 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from datetime import datetime


class FixturesView(APIView):
    def get(self, request):
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        # The ID and range of a sample spreadsheet.
        SAMPLE_SPREADSHEET_ID = '13S4ukA-LM4WA75Ip7CaNKYyYfbbIHBMjsdt28H1azYM'
        SAMPLE_RANGE_NAME = 'fixtures!A2:G'
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'google_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
                return

            fixtures_result_before = []
            fixtures_result_after = []
            ind_fixtures = {}
            
            current_time = datetime.now().strftime("%H:%M")
            current_date = datetime.now().strftime("%d/%m/%Y")
            numOffixturesInserted = 0
            
            print(current_date)
            for row in values:
                
                if any(cell is None for cell in row) or len(row) < 7:
                    continue
                
                team_1 = str(row[0]).upper().strip()
                team_2 = str(row[1]).upper().strip()
                match_time_str = str(row[2]).upper().strip()
                match_date = str(row[3]).upper().strip()
                match_venue = str(row[4]).upper().strip()
                match_level = str(row[5]).upper().strip()
                match_item = str(row[6]).upper().strip()
                
                match_time = datetime.strptime(match_time_str, '%H:%M')
                
                if current_date == match_date and match_time > datetime.strptime(current_time, '%H:%M'):
                    print("Today's match - before")
                    numOffixturesInserted += 1
                else:
                    print("Not today's match - before")
                    continue
                
                
                ind_fixtures = {
                    'team_1': team_1,
                    'team_2': team_2,
                    'match_time': match_time_str,
                    'match_date': match_date,
                    'match_venue': match_venue,
                    'match_level': match_level,
                    'match_item': match_item
                }
                
                fixtures_result_before.append(ind_fixtures)
                
            if numOffixturesInserted == len(values):
                print("All fixtures inserted")
                
                if len(fixtures_result_before) > 0:
                    fixtures_result_before = sorted(fixtures_result_before, key=lambda x: (int(x['match_time'].split(':')[0]), int(x['match_time'].split(':')[1])))
                
            
                print(current_time)
                return Response({"fixture_result": fixtures_result_before}, status=status.HTTP_200_OK)
            
            else:
                for row in values:
                    
                    if any(cell is None for cell in row) or len(row) < 7:
                        continue
                    
                    team_1 = str(row[0]).upper().strip()
                    team_2 = str(row[1]).upper().strip()
                    match_time_str = str(row[2]).upper().strip()
                    match_date = str(row[3]).upper().strip()
                    match_venue = str(row[4]).upper().strip()
                    match_level = str(row[5]).upper().strip()
                    match_item = str(row[6]).upper().strip()
                    
                    match_time = datetime.strptime(match_time_str, '%H:%M')
                    
                    if current_date == match_date and match_time < datetime.strptime(current_time, '%H:%M'):
                        print("Today's match after")
                        numOffixturesInserted += 1
                    else:
                        print("Not today's match after")
                        continue
                    
                    
                    ind_fixtures = {
                        'team_1': team_1,
                        'team_2': team_2,
                        'match_time': match_time_str,
                        'match_date': match_date,
                        'match_venue': match_venue,
                        'match_level': match_level,
                        'match_item': match_item
                    }
                    
                    fixtures_result_after.append(ind_fixtures)
                    
                if numOffixturesInserted == len(values):                
                    print("All fixtures inserted after")
                
                    if len(fixtures_result_before) > 0:
                        fixtures_result_after = sorted(fixtures_result_after, key=lambda x: (int(x['match_time'].split(':')[0]), int(x['match_time'].split(':')[1])))
                    
            fixtures_result = fixtures_result_before + fixtures_result_after  
            print(current_time)
            return Response({"fixture_result": fixtures_result}, status=status.HTTP_200_OK)
                    
            
            

        except HttpError as err:
            print(err)