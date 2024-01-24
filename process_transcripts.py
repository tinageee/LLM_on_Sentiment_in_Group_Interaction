import pandas as pd
import os


# use the transcripts with high quality, read the game names from the csv file
game_name_file_path = "/Users/saiyingge/Coding Projects/PyCharmProjects/LLM_tag/Game_names_LLM.xlsx"
# read the game names from the xlsx
game_names = pd.read_excel(game_name_file_path)
# convert the game names to a list
game_names = game_names['game_names'].tolist()

# read file based on the game names

# Load your CSV file using pandas
csv_file_path = "/Users/saiyingge/Coding Projects/PyCharmProjects/NetworkProject/Data/Private_Data/Reviewed/combined_labels_w_transcripts.csv"'
#read the file
df = pd.read_csv(csv_file_path)


# for all  the row in the folder, print out the transrpt that has odd information, odd marks
for file in file_list:
    if file.endswith(".csv"):
        df = pd.read_csv(csv_file_path + "/" + file)
        #print out the transrpt that has odd marks
        for index, row in df.iterrows():
            if row['trans'] == 'nan' or row['trans'].
                print(row['trans'] + " " + str(index) + " " + file)








# for file in file_list:
#     if file.endswith(".csv"):
        file="015AZ.csv"
        df = pd.read_csv(csv_file_path+"/"+file)
        #change the first column name to index,using column number
        df.columns.values[0] = "idx"
        #take the pervious 4 rows as context,
        #or if the row number is less than 4, take all the rows before the current row
        # or if the context words is less than

# Assuming your CSV has columns like 'player', 'context', and 'targetTurnOfTalk'
# You can modify the column names as needed to match your CSV structure

# Create empty dictionaries for 'context' and 'targetTurnOfTalk'
context_dict = {}
target_turn_dict = {}

# Iterate through rows of the DataFrame and populate the dictionaries
for index, row in df.iterrows():
    player = row['player']
    context = row['context']
    target_turn = row['targetTurnOfTalk']

    # Populate the 'context' dictionary
    context_dict[player] = context

    # Populate the 'targetTurnOfTalk' dictionary
    target_turn_dict[player] = target_turn

# Create the final 'input_data' dictionary
input_data = {
    "context": context_dict,
    "targetTurnOfTalk": target_turn_dict
}

# Now 'input_data' contains the desired structure based on your CSV file
print(input_data)
