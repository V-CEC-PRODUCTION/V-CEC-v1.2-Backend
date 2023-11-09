from celery import shared_task
from live_update_board.models import TeamScore, TeamItems
import os 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .consumers import RealTimeConsumer
from .consumers_team import TeamRealTimeConsumer

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '13S4ukA-LM4WA75Ip7CaNKYyYfbbIHBMjsdt28H1azYM'
SAMPLE_RANGE_NAME = 'item point!A2:E'

@shared_task()
def RealTimeTask():
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

               
        for row in values:
            
            if row[0] == '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] == '':
                continue
            
            
            team_name= str.upper(row[2]).strip()
            
            team_item_instance = TeamItems.objects.filter(item_id=row[0]).first()
            
            if team_item_instance:
                team_item_instance.item = row[1]
                team_item_instance.team = team_name
                team_item_instance.points = row[3]
                team_item_instance.position = row[4]
                team_item_instance.save()
                
                print("Updated the item score")
                
                team_item_all_score = TeamItems.objects.filter(team=team_name).all()
                
                total_team_score = 0
                
                for team_item in team_item_all_score:
                    total_team_score += int(team_item.points)
                    
                team_score_instance = TeamScore.objects.filter(team=team_name).first()
                
                if team_score_instance:
                    team_score_instance.score = total_team_score
                    team_score_instance.save()
                    
                    print("Updated the team score")
                
                team_item_update_socket = TeamRealTimeConsumer()
                
                team_item_update_socket.team_score_changed(instance=team_item_instance)
                
                team_score_update = RealTimeConsumer()
                
                team_score_update.team_score_changed(instance=team_score_instance)
                    
                    
            else:
                TeamItems.objects.create(item_id=row[0],item=row[1],team=team_name,points=row[3],position=row[4])
                
                team_item_all_score = TeamItems.objects.filter(team=team_name).all()
                
                total_team_score = 0
                
                for team_item in team_item_all_score:
                    total_team_score += int(team_item.points)
                    
                team_score_instance = TeamScore.objects.filter(team=team_name).first()
                
                if team_score_instance:
                    team_score_instance.score = total_team_score
                    team_score_instance.save()
                else:
                    pass
                
                team_score_update = RealTimeConsumer()
                
                team_score_update.team_score_changed(instance=team_score_instance)
        
   
    except HttpError as err:
        print(err)
        
        
# if __name__ == '__main__':
#     RealTimeTask()