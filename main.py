import gspread
import pandas as pd 
import dtale 

#NOTE DONT FORGET TO COMMENT OUT
spreadsheetID = "****************"
#NOTE DONT FORGET TO COMMENT OUT

gc = gspread.service_account(filename="credentials.json")
sh = gc.open_by_key(spreadsheetID)

worksheet = sh.worksheet("Dec 2023")

data = worksheet.get_all_values()

df = pd.DataFrame(data)

structured_df = df.drop(columns=[0, 9, 10, 11, 12, 13, 14])

weeks = list()

for week_index in range(0, len(structured_df), 19):
    currentweek_df = structured_df.iloc[week_index:week_index+16, :]
    weeks.append(currentweek_df)

print(len(weeks))

dtale.show(
    weeks[-1],
    host= 'localhost', 
    port = 4000, 
    subprocess = False, 
    force = True 
    )