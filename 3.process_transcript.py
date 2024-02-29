import pandas as pd
import os
import json

# // ToDo:  when make it public, change the api_key to public key
def df_to_context(df):
    '''
    Convert the dataframe to the context that can be used for the GPT model
    :param df: the transcript dataframe
    :return: speaker, context
    '''
    # df=game_round_transcript
    text=  ''
    for index, row in df.iterrows():
        speaker = row['speaker']
        # change the speaker to player1, player2, player3, player4, player5, player6, player7, player8
        if speaker == 0:
            speaker = 'Facilitator'
        # if speaker between 1-8
        elif speaker in range(1, 9):
            speaker = 'p' + str(int(  speaker))
        else:
            speaker = 'unknown speaker'

        context = row['trans']
        text = text + speaker+': \''+context+'\''+'\n'

    return text



# read transcript file


# Load your CSV file using pandas
# read the file
transcript = pd.read_csv('Data/transcripts_cleaned.csv')

# read the game names from the csv
game_info = pd.read_csv('game_info.csv')
game_names = game_info['game_name'].unique()

# process by round
for ind, game in game_info.iterrows():
    game_name = game['game_name']
    for round in range(1, game['max_round'] + 1):
        # print(game_name, round)
        # game_name = '003NTU'
        # round = 1
        # get the transcript for the game and round
        game_round_transcript = transcript[
            (transcript['game'] == game_name) & (transcript['round'] == 'round' + str(round))]

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
