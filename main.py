import gspread
import pandas as pd 
import dtale 
import re

confidential =  open("confidential.txt", "r")
spreadsheetID = confidential.readline().strip()
confidential.close()

agents = {
    "Zo" : "Eastern",
    "Kofi" : "Eastern",
    "Breck" : "Pacific",
    "Garrick" : "Pacific",
    "Elijah" : "Pacific",
    "Devin" : "Eastern",
    "Wesley" : "Pacific",
    "Jay" : "Pacific"
}

agent_schedule = {
    "Eastern" : dict(),
    "Pacific" : dict()
}

# Dictionary to hold the final shift times
#NOTE UNHARD CODE
shifts = {
    "Zo" : {},
    "Kofi" : {},
    "Breck" : {},
    "Garrick" : {},
    "Elijah" : {},
    "Devin" : {},
    "Wesley" : {},
    "Jay" : {}
}

# What each time slot index corresponds to depending on time zone
time_indexes = {
    "Eastern" : ["08:00AM-09:00AM", "09:00AM-10:00AM", "10:00AM-11:00AM", "11:00AM-12:00PM",
                 "12:00PM-01:00PM", "01:00PM-02:00PM", "02:00PM-03:00PM", "03:00PM-04:00PM",
                 "04:00PM-05:00PM", "05:00PM-06:00PM", "06:00PM-07:00PM", "07:00PM-08:00PM",
                 "08:00PM-09:00PM", "09:00PM-10:00PM", "10:00PM-11:00PM", "11:00PM-12:00AM",
                 "12:00AM-01:00AM", "01:00AM-02:00AM"], 
    "Pacific" : ["05:00AM-06:00AM", "06:00AM-07:00AM", "07:00AM-08:00AM", "08:00AM-09:00AM",
                 "09:00AM-10:00AM", "10:00AM-11:00AM", "11:00AM-12:00PM", "12:00PM-01:00PM",
                 "01:00PM-02:00PM", "02:00PM-03:00PM", "03:00PM-04:00PM", "04:00PM-05:00PM",
                 "05:00PM-06:00PM", "06:00PM-07:00PM", "07:00PM-08:00PM", "08:00PM-09:00PM",
                 "09:00PM-10:00PM", "10:00PM-11:00PM"]
}

for agent_name, time_zone in agents.items():
    agent_schedule[time_zone] = {**agent_schedule[time_zone], agent_name : dict()}  #update timezone with new key:value pair

"""
agent_schedule dictionary structure
{
    Eastern : { 
        agent1 : {
            date1 : [time_range],
            date2 : [time_range]
            },
        agent2 : {
            date1 : [time_range],
            date2 : [time_range]
            }
        }
    },
        

    Pacific : { 
        agent1 : {
            date1 : [time_range],
            date2 : [time_range]
            },
        agent2 : {
            date1 : [time_range],
            date2 : [time_range]
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

structured_df = df.drop(columns=[9, 10, 11, 12, 13, 14]) # drops all columns except for eastern/pacific times and dates

weeks = list()

for week_index in range(0, len(structured_df), 19):
    thisWeek_df = structured_df.iloc[week_index:week_index+19, :]
    weeks.append(thisWeek_df)

currentWeek_df = weeks[-1]

for agent_name, time_zone in agents.items():
    for i in range(1, 8): # Changed to 8 instead of 7 because python range() isn't inclusive to end
        time_slots = list(currentWeek_df.iloc[1:, i]) # list of all time slots (aka the names or blank spaces) for the "i" day of the week
        this_date = list(currentWeek_df.iloc[:1, i])[0] # the current date of the iteration
        agent_schedule[time_zone][agent_name] = {**agent_schedule[time_zone][agent_name], this_date : list()} #initializes the current date to a list
        shifts[agent_name] = {**shifts[agent_name], this_date : list()}
            
        for slot_index in range(len(time_slots)):
            current_slot = time_slots[slot_index] # the current value of the time slot as we iterate
            if agent_name in current_slot:
                match = re.search(":..", current_slot) # checking for unusual start times
                if match:
                    agent_schedule[time_zone][agent_name][this_date].append(time_indexes[time_zone][slot_index] + " (" + match.group() + ")") # Adds to the list with an extra marker
                else:
                    agent_schedule[time_zone][agent_name][this_date].append(time_indexes[time_zone][slot_index]) # adds index of current slot if it matches agent name
            elif "Team meeting" in current_slot: # Checking for team meetings
                match = re.search(":..", current_slot)
                if match:
                    agent_schedule[time_zone][agent_name][this_date].append(time_indexes[time_zone][slot_index] + " (TM)(" + match.group() + ")") 
                else:
                    agent_schedule[time_zone][agent_name][this_date].append(time_indexes[time_zone][slot_index] + " (TM)")
    # Deleted if statement for time zone because the loop in each was the same 
                
# print("Debug Marker")  
# for zone in agent_schedule:
#     for agent in agent_schedule[zone]:
#         print(agent, agent_schedule[zone][agent])


for time_zone in agent_schedule:
    for agent in agent_schedule[time_zone]:
        for date in agent_schedule[time_zone][agent]:
            times = agent_schedule[time_zone][agent][date]
            searching = False # When True, it is currently in a series of sequential time periods
            new_time = "00:00AM-00:00AM" # Starter values for before the loop
            last_time = "00:00AM" # new_time is the shift hours, last_time checks if we are still in a series
            for period in times:
                match = re.search("\(:..\)", period) # Looks for unusual shift times, match is further used to change minute times
                if "(TM)" in period: # Team meetings are considered a separate shift for everyone
                    if match:
                        new_period = period[:3] + match.group()[2:4] + period[5:11] + match.group()[2:4] + period[13:15]
                        shifts[agent][date].append(new_period+" (TM)") # Added with a (TM) marker to differentiate
                    else:
                        shifts[agent][date].append(period[:15]+" (TM)") # added without changing minute times
                    continue
                if not searching: # starting a new series of sequential time periods (beginning of shift)
                    new_time = period
                    if match:
                        new_time = period[:3] + match.group()[2:4] + period[5:15]
                    last_time = period[8:15]
                    searching = True
                    continue
                if searching and period[:7] != last_time: # When we come to the end of a sequential time period (end of shift)
                    shifts[agent][date].append(new_time) # This method also accounts for multiple shifts on the same day
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
                shifts[agent][date].append(new_time)
            if not shifts[agent][date]: # Deletes any days with no shifts from the dictionary
                del shifts[agent][date]

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