import gspread
import pandas as pd 
import dtale 
import re

#NOTE DONT FORGET TO COMMENT OUT
spreadsheetID = "********"
#NOTE DONT FORGET TO COMMENT OUT


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
            
        for slot_index in range(len(time_slots)):
            current_slot = time_slots[slot_index] # the current value of the time slot as we iterate
            if agent_name in current_slot:
                match = re.search(":..", current_slot) # checking for unusual start times
                if match:
                    agent_schedule[time_zone][agent_name][this_date].append(str(slot_index) + " special" + match.group()) # Adds to the list with an extra marker
                else:
                    agent_schedule[time_zone][agent_name][this_date].append(slot_index) # adds index of current slot if it matches agent name
    # Deleted if statement for time zone because the loop in each was the same 
                
print("Debug Marker")  
for zone in agent_schedule:
    for agent in agent_schedule[zone]:
        print(agent, agent_schedule[zone][agent])
                   
# dtale.show(
#     currentWeek_df,
#     host= 'localhost', 
#     port = 4000, 
#     subprocess = False, 
#     force = True 
#     )