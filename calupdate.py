# read a csv file from the filesystem
# update google calendar
# subject,startdate,starttime,description
import sys
import csv
import datetime
from google_calendar import get_google_calendar

FILE = sys.argv[1]
CALENDAR = sys.argv[2]

# if not (FILE or CALENDAR):
#   print("filename or google calendar name not provided. exiting.")
#   sys.exit()

service = None

def main():
  rows = parse_csv(FILE)
  get_calendar_service()
  calendarId = get_calendarId()

  if calendarId:
    print(f"Processing {len(rows)} rows...")
    for row in rows:
      process_event_row(calendarId, row)

def parse_csv(filename):
  rows = []
  print(f"Parsing CSV: {filename}...")
  with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile) 

    keys = []
    for i,row in enumerate(csvreader):
      if i == 0:
        keys = row
      else:
        row_dict = {}
        for col,value in enumerate(row):
          row_dict[keys[col]] = value
        rows.append(row_dict)
  print("CSV parsing complete")
  return rows

def process_event_row(calId, eventRow):
  # if cal contains subject
  events_result = service.events().list(calendarId=calId, q=eventRow["Subject"]).execute()
  events = events_result.get('items', [])
  requestBody = formatRequestBody(eventRow)
  if(events):
    update_event(calId, events[0].id, requestBody)
  else:
    add_event(calId, requestBody)

def get_calendar_service():
  global service
  service = get_google_calendar()

def get_calendarId():
  calendars_list_results = service.calendarList().list().execute()
  calendars_list = calendars_list_results.get('items', [])
  
  # calendar = next((x for x in calendars_list if x.summary == CALENDAR), None)
  calendar = None
  for cal in calendars_list:
    if cal['summary'] == CALENDAR:
      calendar = cal
      break
  else:
    cal = None

  if calendar:
    print("CALENDAR YES")
    return calendar['id']
  else:
    print("CALENDAR NO")
    return None

def formatDate(date,time):
  return datetime.datetime.strptime(f"{date}T{time}", "%m/%d/%yT%I:%M %p").strftime('%Y-%m-%dT%H:%M:%S-04:00')

def formatRequestBody(eventRow):
  print("EVENT ROW", eventRow)
  body = {
    "summary": eventRow["Subject"],
    "start": {
      "dateTime": formatDate(eventRow["Start Date"], eventRow["Start Time"])
    },
    "description": eventRow["Description"]
  }
  return body

def update_event(calId, eventId, body):
  service.events().update(calendarId=calId, eventId=eventId, body=body)

def add_event(calId, body):
  service.events().insert(calendarId=calId, body=body)


main()