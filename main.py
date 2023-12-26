import gspread
import pandas as pd 
import dtale 
import re

confidential =  open("confidential.txt", "r")
spreadsheetID = confidential.readline().strip()
confidential.close()

agents = {
    "Zo" : "America/New_York",
    "Kofi" : "America/New_York",
    "Breck" : "America/Los_Angeles",
    "Garrick" : "America/Los_Angeles",
    "Elijah" : "America/Los_Angeles",
    "Devin" : "America/New_York",
    "Wesley" : "America/Los_Angeles",
    "Jay" : "America/Los_Angeles"
}

agents_email = {
    "Zo" : "zohaibk1204@gmail.com",
    "Kofi" : "kodarfour@gmail.com",
    "Breck" : ".com",
    "Garrick" : ".com",
    "Elijah" : ".com",
    "Devin" : ".com",
    "Wesley" : ".com",
    "Jay" : ".com"
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

# Dictionary to hold the final shift times
shifts =  dict()
for agent in agents.keys():
    shifts[agent] = dict()

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

for agent_name, time_zone in agents.items():
    agent_schedule[time_zone] = {**agent_schedule[time_zone], agent_name : dict()}  #update timezone(key) value pair with a new key:value pair (agent name : {date : shifts})

"""
agent_schedule dictionary structure
{
    Eastern : { 
        agent1 : {
            date1 : [shifts],
            date2 : [shifts]
            },
        agent2 : {
            date1 : [shifts],
            date2 : [shifts]
            }
        }
    },
        

    Pacific : { 
        agent1 : {
            date1 : [shifts],
            date2 : [shifts]
            },
        agent2 : {
            date1 : [shifts],
            date2 : [shifts]
            }
        }
    }
}
"""

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

for agent_name, time_zone in agents.items():
    for i in range(1, 8): 
        time_slots = list(currentWeek_df.iloc[1:, i]) 
        current_date = list(currentWeek_df.iloc[:1, i])[0]
        agent_schedule[time_zone][agent_name] = {**agent_schedule[time_zone][agent_name], current_date : list()}
        shifts[agent_name] = {**shifts[agent_name], current_date : list()}
            
        for slot_index in range(len(time_slots)):
            current_slot = time_slots[slot_index]
            if agent_name in current_slot:
                match = re.search(":..", current_slot) # checking for unusual start times
                if match:
                    agent_schedule[time_zone][agent_name][current_date].append(time_indexes[time_zone][slot_index] + " (" + match.group() + ")") 
                else:
                    agent_schedule[time_zone][agent_name][current_date].append(time_indexes[time_zone][slot_index])
            elif "Team meeting" in current_slot:
                match = re.search(":..", current_slot)
                if match:
                    agent_schedule[time_zone][agent_name][current_date].append(time_indexes[time_zone][slot_index] + " (TM)(" + match.group() + ")") 
                else:
                    agent_schedule[time_zone][agent_name][current_date].append(time_indexes[time_zone][slot_index] + " (TM)")
    # Deleted if statement for time zone because the loop in each was the same 
                
# print("Debug Marker")  
# for zone in agent_schedule:
#     for agent in agent_schedule[zone]:
#         print(agent, agent_schedule[zone][agent])


for time_zone in agent_schedule:
    for agent_name in agent_schedule[time_zone]:
        for date in agent_schedule[time_zone][agent_name]:
            times = agent_schedule[time_zone][agent_name][date]
            searching = False 
            new_time = "00:00AM-00:00AM" # Starter values for before the loop
            last_time = "00:00" # new_time is the shift hours, last_time checks if we are still in a series
            for period in times:
                match = re.search("\(:..\)", period) # Looks for unusual shift times, match is further used to change minute times
                if "(TM)" in period: # Team meetings are considered a separate shift for everyone
                    if match:
                        new_period = period[:3] + match.group()[2:4] + period[5:9] + match.group()[2:4]
                        
                        shifts[agent_name][date].append(new_period+" (TM)") # Added with a (TM) marker to differentiate
                    else:
                        shifts[agent_name][date].append(period[:15]+" (TM)") # added without changing minute times
                    continue
                if not searching: # starting a new series of sequential time periods (beginning of shift)
                    new_time = period
                    if match:
                        new_time = period[:3] + match.group()[2:4] + period[5:15]
                    last_time = period[8:15]
                    searching = True
                    continue
                if searching and period[:7] != last_time: # When we come to the end of a sequential time period (end of shift)
                    shifts[agent_name][date].append(new_time) # This method also accounts for multiple shifts on the same day
                    searching = False # Resets variables to the original starting values to start a fresh shift
                    new_time = "00:00AM-00:00AM"
                    last_time = "00:00AM"
                else: # If we are still "in" the shift, it will update the second half of the new_time variable (with unusual minute values if needed)
                    if match:
                        new_time = new_time[:8] + period[:3] + match.group()[2:4] + period[5:7]
                    else:
                        new_time = new_time[:8] + period[8:15]
                    last_time = period[8:15]
            if new_time != "00:00AM-00:00AM": # Ensures sure the placeholder shift is not added
                shifts[agent_name][date].append(new_time)
            if not shifts[agent_name][date]: # Deletes any days with no shifts from the dictionary
                del shifts[agent_name][date]

for agent in shifts: # Printing out shifts to check
    print(agent+":")
    for date in shifts[agent]:
        print("  ",date+":",shifts[agent][date])

       

                   
# dtale.show(
#     currentWeek_df,
#     host= 'localhost', 
#     port = 4000, 
#     subprocess = False, 
#     force = True 
#     )