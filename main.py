import gspread
import pandas as pd 
import re

confidential =  open("confidential.txt", "r")
spreadsheetID = confidential.readline().strip()
breck_email = confidential.readline().strip()
garrick_email = confidential.readline().strip()
devin_email = confidential.readline().strip()
confidential.close()

agents = {
    #example:
    #"agent name" : ["time/zone", "email@address.com"],
    "Zo" : ["America/New_York", "zohaibk1204@gmail.com"],
    "Kofi" : ["America/New_York", "kodarfour@gmail.com"],
    "Breck" : ["America/Los_Angeles", breck_email],
    "Garrick" : ["America/Los_Angeles",  garrick_email],
    "Elijah" : ["America/Los_Angeles",  "email"],
    "Devin" : ["America/New_York",  devin_email],
    "Wesley" : ["America/Los_Angeles",  "email"],
    "Jay" : ["America/Los_Angeles", "email"] ,
}

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
            date1 : [shift period, shift period, team meeting period, shift period],
            date2 : [shift period, shift period, team meeting period, shift period]
            },
        agent2 : {
            date1 : [shift period, shift period, team meeting period, shift period],
            date2 : [shift period, shift period, team meeting period, shift period]
            }
        }
    },
        

    Pacific : { 
        agent1 : {
            date1 : [shift period, shift period, team meeting period, shift period],
            date2 : [shift period, shift period, team meeting period, shift period]
            },
        agent2 : {
            date1 : [shift period, shift period, team meeting period, shift period],
            date2 : [shift period, shift period, team meeting period, shift period]
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

gc = gspread.service_account(filename="credentials.json")
sh = gc.open_by_key(spreadsheetID)

worksheet = sh.worksheet("Dec 2023")

data = worksheet.get_all_values()

df = pd.DataFrame(data)

structured_df = df.drop(columns=[9, 10, 11, 12, 13, 14]) #minimizes to only needed columns in spreadsheet

weeks = list()

for week_index in range(0, len(structured_df), 19):
    thisWeek_df = structured_df.iloc[week_index:week_index+19, :]
    weeks.append(thisWeek_df)

currentWeek_df = weeks[-1]

for agent_name, agent_info in agents.items(): # algorithim that groups shifts within each date
    time_zone = agent_info[0]
    for i in range(1, 8): 
        time_slots = list(currentWeek_df.iloc[1:, i]) 
        current_date = list(currentWeek_df.iloc[:1, i])[0]
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
                    if slot_index - prev_slot_index < 0: #if team meeting period is first in shift set
                        shift_count += 1                        
                else: # if custom minutes isn't found for team meeting period
                    if slot_index - prev_slot_index > 0:
                        shift_count += 1
                    agent_schedule[time_zone][agent_name][current_date].append(list())
                    agent_schedule[time_zone][agent_name][current_date][shift_count].append(time_indexes[time_zone][slot_index] + " (TM)")
                    if slot_index - prev_slot_index < 0: 
                        shift_count += 1
       
for time_zone in agent_schedule:
    if len(list(agent_schedule[time_zone].keys())) == 0: #if there are no agents in current time_zone skip
        pass
    else:
        for agent_name in agent_schedule[time_zone]:
            print(agent_name + " (" + time_zone + "):")
            for current_date in agent_schedule[time_zone][agent_name]:
                if len(agent_schedule[time_zone][agent_name][current_date]) == 0: #if there are no shifts for this day skip
                    pass
                else:
                    print("  " + current_date + ": ", end="")
                    for current_shift_set in agent_schedule[time_zone][agent_name][current_date]:
                        if len(current_shift_set) == 1: # single hour shift
                            print(current_shift_set[0], end=", ") 
                        else: # multiple hour shift
                            start_time = current_shift_set[0][:5]
                            end_time = current_shift_set[-1][6:]
                            print(start_time + "-" + end_time, end=", ") 
                    print()