import gspread
import pandas as pd 
import re
import datetime
from datetime import timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

confidential =  open("confidential.txt", "r")
spreadsheetID = confidential.readline().strip()
breck_email = confidential.readline().strip()
garrick_email = confidential.readline().strip()
devin_email = confidential.readline().strip()
shift_description = confidential.readline().strip()
tm_description = confidential.readline().strip()
wesley_email = confidential.readline().strip()
confidential.close()

agents = { 
    # example:
    # "agent name" : ["time/zone", "email@address.com"], NOTE (if "email@address.com" is set to "email", it will skip the agent.)
    "Zo" : ["America/New_York", "zohaibk1204@gmail.com"], 
    "Kofi" : ["America/New_York", "kodarfour@gmail.com"],
    "Breck" : ["America/Los_Angeles", breck_email], 
    "Garrick" : ["America/Los_Angeles", garrick_email], 
    "Elijah" : ["America/Los_Angeles",  "email"],
    "Devin" : ["America/New_York",  devin_email],  
    "Wesley" : ["America/Los_Angeles", wesley_email], 
    "Jay" : ["America/Los_Angeles", "email"] ,
}

tm_whitelist = ["Zo", "Kofi"] # agents who want team meetings pushed to personal emails

agent_schedule = {
    "America/New_York": dict(),         # Eastern Time
    "America/Los_Angeles": dict(),      # Pacific Time
    "America/Chicago": dict(),          # Central Time
    "America/Denver": dict(),           # Mountain Time
    "America/Anchorage": dict(),        # Alaska
    "Pacific/Honolulu": dict(),         # Hawaii
    "America/Phoenix": dict(),          # Arizona
    "America/Puerto_Rico": dict(),      # Puerto Rico
    "Pacific/Guam": dict(),             # Guam
    "Pacific/Pago_Pago": dict(),        # American Samoa
    "Northern_Mariana_Islands": dict(), # Northern Mariana Islands
    "America/St_Thomas": dict()         # Virgin Islands
}

for agent_name, agent_info in agents.items(): # populate agent_schedule with agent names
    time_zone = agent_info[0]
    agent_schedule[time_zone] = {**agent_schedule[time_zone], agent_name : dict()} 

"""
example agent_schedule dictionary structure ^^^
{
    Eastern : { 
        agent1 : {
            date1 : [shift set, shift set, team meeting period, shift set],
            date2 : [shift set, shift set, team meeting period, shift set]
            },
        agent2 : {
            date1 : [shift set, shift set, team meeting period, shift set],
            date2 : [shift set, shift set, team meeting period, shift set]
            }
        }
    },
        

    Pacific : { 
        agent1 : {
            date1 : [shift set, shift set, team meeting period, shift set],
            date2 : [shift set, shift set, team meeting period, shift set]
            },
        agent2 : {
            date1 : [shift set, shift set, team meeting period, shift set],
            date2 : [shift set, shift set, team meeting period, shift set]
            }
        }
    }
}
"""

# What each time slot index corresponds to depending on time zone
time_indexes = {
    'America/New_York': [
        '08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', 
        '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', 
        '16:00-17:00', '17:00-18:00', '18:00-19:00', '19:00-20:00', 
        '20:00-21:00', '21:00-22:00', '22:00-23:00', '23:00-00:00', 
        '00:00-01:00', '01:00-02:00'
    ],
    'America/Los_Angeles': [
        '05:00-06:00', '06:00-07:00', '07:00-08:00', '08:00-09:00', 
        '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', 
        '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', 
        '17:00-18:00', '18:00-19:00', '19:00-20:00', '20:00-21:00', 
        '21:00-22:00', '22:00-23:00'
    ],
    'America/Chicago': [
        '07:00-08:00', '08:00-09:00', '09:00-10:00', '10:00-11:00', 
        '11:00-12:00', '12:00-13:00', '13:00-14:00', '14:00-15:00', 
        '15:00-16:00', '16:00-17:00', '17:00-18:00', '18:00-19:00', 
        '19:00-20:00', '20:00-21:00', '21:00-22:00', '22:00-23:00', 
        '23:00-00:00', '00:00-01:00'
    ],
    'America/Denver': [
        '06:00-07:00', '07:00-08:00', '08:00-09:00', '09:00-10:00', 
        '10:00-11:00', '11:00-12:00', '12:00-13:00', '13:00-14:00', 
        '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00', 
        '18:00-19:00', '19:00-20:00', '20:00-21:00', '21:00-22:00', 
        '22:00-23:00', '23:00-00:00'
    ],
    "America/Anchorage": [
        "04:00-05:00", "05:00-06:00", "06:00-07:00", "07:00-08:00",
        "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
        "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00",
        "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00",
        "20:00-21:00", "21:00-22:00"
    ],
    "Pacific/Honolulu": [
        "03:00-04:00", "04:00-05:00", "05:00-06:00", "06:00-07:00",
        "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00",
        "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00",
        "15:00-16:00", "16:00-17:00", "17:00-18:00", "18:00-19:00",
        "19:00-20:00", "20:00-21:00"
    ],
    "America/Phoenix": [
        "04:00-05:00", "05:00-06:00", "06:00-07:00", "07:00-08:00",
        "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
        "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00",
        "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00",
        "20:00-21:00", "21:00-22:00"
    ],
    "America/Puerto_Rico": [
        "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
        "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00",
        "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00",
        "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-00:00",
        "00:00-01:00", "01:00-02:00"
    ],
    "Pacific/Guam": [
        "23:00-00:00 (PREV DAY)", "00:00-01:00", "01:00-02:00", "02:00-03:00",
        "03:00-04:00", "04:00-05:00", "05:00-06:00", "06:00-07:00",
        "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00",
        "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00",
        "15:00-16:00", "16:00-17:00"
    ],
    "Pacific/Pago_Pago": [
        "21:00-22:00 (PREV DAY)", "22:00-23:00 (PREV DAY)", "23:00-00:00", "00:00-01:00",
        "01:00-02:00", "02:00-03:00", "03:00-04:00", "04:00-05:00",
        "05:00-06:00", "06:00-07:00", "07:00-08:00", "08:00-09:00",
        "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
        "13:00-14:00", "14:00-15:00"
    ],
    "Northern_Mariana_Islands": [
        "23:00-00:00 (PREV DAY)", "00:00-01:00", "01:00-02:00", "02:00-03:00",
        "03:00-04:00", "04:00-05:00", "05:00-06:00", "06:00-07:00",
        "07:00-08:00", "08:00-09:00", "09:00-10:00", "10:00-11:00",
        "11:00-12:00", "12:00-13:00", "13:00-14:00", "14:00-15:00",
        "15:00-16:00", "16:00-17:00"
    ],
    "America/St_Thomas": [
        "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
        "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00",
        "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00",
        "20:00-21:00", "21:00-22:00", "22:00-23:00", "23:00-00:00",
        "00:00-01:00", "01:00-02:00"
    ]
}

today = datetime.date.today()
month_now = str(today.month)
year_now = today.year
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None

try:
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
except Exception as e:
    flow = InstalledAppFlow.from_client_secrets_file('calendar_credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

try:
    service = build('calendar', 'v3', credentials=creds)
except Exception as e:
    print(f"ERROR: {e}\nFailed to build Calendar service")
    exit()

try:
    gc = gspread.service_account(filename="credentials.json")
    sh = gc.open_by_key(spreadsheetID)
except Exception as e:
    print(f"ERROR: {e}\nFailed to open Sheet")
    exit()

spreadsheet_info = sh.worksheets()
worksheet_titles = [sheet.title for sheet in spreadsheet_info]

regex_years = (year_now, year_now+1)
regex_pattern = "^\w{3,8}\s%d|%d$" 
# selects latest title under the parameters of:
# 1. character size 3-8 (smallest month name is 3 largest is 8) takin in account for abreviations
# 2. one single white space
# 3. either the current year or one year after
# NOTE: MAKE SURE THAT LEAD IS AWARE OF NAMING CONVENTION/ENSURING TARGET SCHEDULING WORKSHEET IS BEFORE ALL OTHER SCHEDULE RELATED WORKSHEETS

for title in worksheet_titles: 
    formatted_regex_pattern = regex_pattern % regex_years
    match = re.search(formatted_regex_pattern, title)
    if match:
        latest_title = title
        break

latest_worksheet = sh.worksheet(latest_title)
data = latest_worksheet.get_all_values()
df = pd.DataFrame(data)
structured_df = df[[0, 1, 2, 3, 4, 5,6,7,8]] # minimizes to only needed columns in spreadsheet
weeks = list()

for week_index in range(0, len(structured_df), 19):
    thisWeek_df = structured_df.iloc[week_index:week_index+19, :]
    not_empty = 'Team meeting' in thisWeek_df.to_string()
    if not_empty:
        weeks.append(thisWeek_df)

try:
    currentWeek_df = weeks[-1]
except Exception as e:
    print(f"ERROR: {e}\nCheck if sheet is empty!")
    exit()

for agent_name, agent_info in agents.items(): # algorithm that groups shifts within each date
    time_zone = agent_info[0]
    for i in range(1, 8): 
        time_slots = list(currentWeek_df.iloc[1:, i]) 
        current_date_unformatted = list(currentWeek_df.iloc[:1, i])[0]
        current_month = current_date_unformatted[:current_date_unformatted.index('/')]
        if month_now == current_month or str(int(month_now)+1) == current_month:
            current_date_unformatted += "/" + str(year_now)
        elif month_now == "12" and current_month == "1":
            current_date_unformatted += "/" + str(year_now + 1)
        elif month_now == "1" and current_month == "12":
            current_date_unformatted += "/" + str(year_now - 1)
        current_date = str(datetime.datetime.strptime(current_date_unformatted, "%m/%d/%Y").date())
        agent_schedule[time_zone][agent_name] = {**agent_schedule[time_zone][agent_name], current_date : list()}
        prev_slot_index = 100000000000000000
        shift_count = 0
        for slot_index in range(len(time_slots)):
            current_slot = time_slots[slot_index]
            if agent_name in current_slot:
                match = re.search(":..", current_slot) # checking for custom start times
                if match: # if custom minutes found for shift period
                    custom_minutes = match.group()
                    if slot_index - prev_slot_index < 0: # if period is first in shift set
                        agent_schedule[time_zone][agent_name][current_date].append(list())
                        first_hour = time_indexes[time_zone][slot_index][:2] 
                        remaining_time = time_indexes[time_zone][slot_index][5:]
                        agent_schedule[time_zone][agent_name][current_date][shift_count].append(first_hour + custom_minutes  + remaining_time) 
                        prev_slot_index = slot_index
                    elif slot_index - prev_slot_index == 1: # if shift period isn't first AND concurrent in shift set
                        time_before_custom_minutes = time_indexes[time_zone][slot_index][:8]
                        agent_schedule[time_zone][agent_name][current_date][shift_count].append(time_before_custom_minutes + custom_minutes)
                        prev_slot_index = slot_index
                    else: # if not in current shift set
                        shift_count += 1
                        agent_schedule[time_zone][agent_name][current_date].append(list())
                        first_hour = time_indexes[time_zone][slot_index][:3] 
                        remaining_time = time_indexes[time_zone][slot_index][5:]
                        agent_schedule[time_zone][agent_name][current_date][shift_count].append(first_hour + custom_minutes  + remaining_time) 
                        prev_slot_index = slot_index
                else: # if custom minutes isn't found for shift period
                    if slot_index - prev_slot_index == 1: 
                        agent_schedule[time_zone][agent_name][current_date][shift_count].append(time_indexes[time_zone][slot_index])
                        prev_slot_index = slot_index
                    else: 
                        if slot_index - prev_slot_index > 1: # if not in current shift set
                            shift_count += 1
                        agent_schedule[time_zone][agent_name][current_date].append(list())
                        agent_schedule[time_zone][agent_name][current_date][shift_count].append(time_indexes[time_zone][slot_index])
                        prev_slot_index = slot_index
            elif "Team meeting" in current_slot:
                match = re.search(":..", current_slot)
                if match: # if custom minutes found for team meeting period
                    custom_minutes = match.group()
                    if slot_index - prev_slot_index > 0: # if there is a shift  already in shift set, must create new shift  for TM
                        shift_count += 1
                    agent_schedule[time_zone][agent_name][current_date].append(list())
                    first_hour = time_indexes[time_zone][slot_index][:2] 
                    second_hour = time_indexes[time_zone][slot_index][6:8]
                    agent_schedule[time_zone][agent_name][current_date][shift_count].append(first_hour + custom_minutes + "-" + second_hour + custom_minutes + " (TM)")
                    if slot_index - prev_slot_index < 0: # if team meeting period is first in shift set
                        shift_count += 1                        
                else: # if custom minutes isn't found for team meeting period
                    if slot_index - prev_slot_index > 0:
                        shift_count += 1
                    agent_schedule[time_zone][agent_name][current_date].append(list())
                    agent_schedule[time_zone][agent_name][current_date][shift_count].append(time_indexes[time_zone][slot_index] + " (TM)")
                    if slot_index - prev_slot_index < 0: 
                        shift_count += 1

for time_zone in agent_schedule:
    if len(list(agent_schedule[time_zone].keys())) == 0: # if there are no agents in current time_zone skip
        pass
    else:
        for agent_name in agent_schedule[time_zone]:
            if agents[agent_name][-1] == "email":
                pass
            else:
                agent_emal = agents[agent_name][-1]
                for current_date in agent_schedule[time_zone][agent_name]:
                    if len(agent_schedule[time_zone][agent_name][current_date]) == 0: # if there are no shifts for this day skip
                        pass
                    elif len(agent_schedule[time_zone][agent_name][current_date]) > 0:
                        for current_shift_set in agent_schedule[time_zone][agent_name][current_date]:
                            if len(current_shift_set) == 1: # single hour shift
                                start_time = current_date + "T" + current_shift_set[0][:5] + ":00" 
                                end_time = current_date + "T" + current_shift_set[0][6:11] + ":00"
                                if "(TM)" in current_shift_set[0] and agent_name in tm_whitelist:
                                    team_meeting = { # reset values
                                        'summary': '',
                                        'location': 'Zoom',
                                        'description': tm_description,
                                        'start': {
                                            'dateTime': '',
                                            'timeZone': '',
                                        },
                                        'end': {
                                            'dateTime': '',
                                            'timeZone': '',
                                        },
                                        'attendees': [],
                                        'reminders': {
                                            'useDefault': False,
                                            'overrides': [
                                            {'method': 'email', 'minutes': 15},
                                            {'method': 'popup', 'minutes': 5},
                                            ],
                                        },
                                    }
                                    team_meeting['summary'] = 'Team Meeting: ' + current_date
                                    team_meeting['start']['dateTime'] = start_time
                                    team_meeting['start']['timeZone'] = time_zone
                                    team_meeting['end']['dateTime'] = end_time
                                    team_meeting['end']['timeZone'] = time_zone
                                    attendee = dict()
                                    attendee['email'] = agent_emal
                                    team_meeting['attendees'].append(attendee)
                                    try:
                                        created_event = service.events().insert(calendarId='primary', body=team_meeting).execute()
                                        print("Team Meeting Event created for " +  agent_name + " on " + current_date + " from " + current_shift_set[0][:5] + " - " + current_shift_set[0][6:11] + ": ", end = '')
                                        print(f" {created_event.get('htmlLink')}\n")
                                    except Exception as e:
                                        print(f"ERROR: {e}\nFailed to create Team Meeting Event for " +  agent_name + " on " + current_date + " from " + current_shift_set[0][:5] + " - " + current_shift_set[0][6:11]+"\n")
                                elif "(TM)" not in current_shift_set[0]: 
                                    regular_shift = { # reset values
                                        'summary': '',
                                        'location': 'Zendesk',
                                        'description': shift_description,
                                        'start': {
                                            'dateTime': '',
                                            'timeZone': '',
                                        },
                                        'end': {
                                            'dateTime': '',
                                            'timeZone': '',
                                        },
                                        'attendees': [],
                                        'reminders': {
                                            'useDefault': False,
                                            'overrides': [
                                            {'method': 'email', 'minutes': 15},
                                            {'method': 'popup', 'minutes': 5},
                                            ],
                                        },
                                    }
                                    regular_shift['summary'] = 'Shift: ' + current_date
                                    regular_shift['start']['dateTime'] = start_time
                                    regular_shift['start']['timeZone'] = time_zone
                                    regular_shift['end']['dateTime'] = end_time
                                    regular_shift['end']['timeZone'] = time_zone
                                    attendee = dict()
                                    attendee['email'] = agent_emal
                                    regular_shift['attendees'].append(attendee)
                                    try:
                                        created_event = service.events().insert(calendarId='primary', body=regular_shift).execute()
                                        print("Regular Shift Event created for " +  agent_name + " on " + current_date + " from " + current_shift_set[0][:5] + " - " + current_shift_set[0][6:11] + ": ", end = '')
                                        print(f" {created_event.get('htmlLink')}\n")
                                    except Exception as e:
                                        print(f"ERROR: {e}\nFailed to create Regular Shift Event for " +  agent_name + " on " + current_date + " from " + current_shift_set[0][:5] + " - " + current_shift_set[0][6:11]+"\n")
                            else: # multiple hour shift
                                start_time = current_date + "T" + current_shift_set[0][:5] + ":00"
                                starting_hours = int(current_shift_set[0][:2]) # the "hh" part of the "hh:mm:ss" time format for start time
                                ending_hours = int(current_shift_set[-1][6:8]) # the "hh" part of the "hh:mm:ss" time format for end time
                                if starting_hours < ending_hours: 
                                    end_time = current_date + "T" + current_shift_set[-1][6:] + ":00"
                                elif starting_hours > ending_hours:
                                    old_date = current_date
                                    old_date_obj = datetime.datetime.strptime(old_date, "%Y-%m-%d").date()
                                    next_day = old_date_obj + timedelta(days=1)
                                    new_current_date = str(next_day)
                                    end_time = new_current_date + "T" + current_shift_set[-1][6:] + ":00"
                                regular_shift = { # reset values
                                    'summary': '',
                                    'location': 'Zendesk',
                                    'description': shift_description,
                                    'start': {
                                        'dateTime': '',
                                        'timeZone': '',
                                    },
                                    'end': {
                                        'dateTime': '',
                                        'timeZone': '',
                                    },
                                    'attendees': [],
                                    'reminders': {
                                        'useDefault': False,
                                        'overrides': [
                                        {'method': 'email', 'minutes': 15},
                                        {'method': 'popup', 'minutes': 5},
                                        ],
                                    },
                                }
                                regular_shift['summary'] = 'Shift: ' + current_date
                                regular_shift['start']['dateTime'] = start_time
                                regular_shift['start']['timeZone'] = time_zone
                                regular_shift['end']['dateTime'] = end_time
                                regular_shift['end']['timeZone'] = time_zone
                                attendee = dict()
                                attendee['email'] = agent_emal
                                regular_shift['attendees'].append(attendee)
                                try:
                                    created_event = service.events().insert(calendarId='primary', body=regular_shift).execute()
                                    print("Regular Shift Event created for " +  agent_name + " on " + current_date + " from " + current_shift_set[0][:5] + " - " + current_shift_set[-1][6:] + ": ", end = '')
                                    print(f" {created_event.get('htmlLink')}\n")
                                except Exception as e:
                                        print(f"ERROR: {e}\nFailed to create Team Meeting Event for " +  agent_name + " on " + current_date + " from " + current_shift_set[0][:5] + " - " + current_shift_set[0][6:11]+"\n")