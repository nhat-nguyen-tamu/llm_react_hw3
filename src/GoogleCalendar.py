from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import datetime

class CalendarHandler():
    def __init__(self):
        self.creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                print("loaded creds")
                self.creds = pickle.load(token)
            
        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_event(self):
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        print("got events", events)

        event_strings = [f"'current_time': {now}, 'found_events': {len(events)}"]
        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            #print(start, event['summary'])
            event_strings.append(f"'summary': '{event['summary']}', 'description': '{event['description']}', 'start': '{event['start']['dateTime']}, 'end': '{event['end']['dateTime']}'")
        return '\n'.join(event_strings)

    def add_event(self, start_time_iso, title, description, event_duration_minutes = 60):
        try:
            event_date = datetime.datetime.fromisoformat(start_time_iso)
            start = event_date.isoformat()

            end = (event_date + datetime.timedelta(minutes=event_duration_minutes)).isoformat()

            print(start, end)

            if False:
                return (
                    f"Calendar submit successful!\n"
                    f"start time: {start}\n"
                    f"end time: {end}\n"
                    f"title: {title}\n"
                    f"description: {description}"
                )

            event_result = self.service.events().insert(
                calendarId='primary',
                body={
                    "summary": title,
                    "description": description,
                    "start": {"dateTime": start, "timeZone": 'America/Chicago'},
                    "end": {"dateTime": end, "timeZone": 'America/Chicago'},
                }
            ).execute()

            result_string = (
                f"Event created successfully:\n"
                f"id: '{event_result['id']}',\n"
                f"summary: '{event_result['summary']}',\n"
                f"starts at: '{event_result['start']['dateTime']}',\n"
                f"ends at: '{event_result['end']['dateTime']}'"
            )
            return result_string
        except Exception as e:
            return f"An error occurred: {str(e)}"
        

# print(CalendarHandler().add_event("2024-11-05T10:30:00", 60))