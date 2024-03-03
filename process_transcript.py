'''
convert the transcript to the context that can be used for the GPT model
calculate the number of tokens, rows and length of the conversation
'''

import pandas as pd
import os
import json
from transformers import GPT2Tokenizer


def df_to_context_w_index(df):
    """
    Convert the dataframe to the context that can be used for the GPT model
    :param df: the transcript dataframe
    :return: speaker, context
    """
    # df=game_round_transcript
    text_out = ''
    for index, row in df.iterrows():
        # if conversation is na skip
        if row['trans'] is None:
            continue

        context = row['trans']
        speaker = row['speaker']
        # change the speaker to player1, player2, player3, player4, player5, player6, player7, player8
        if speaker == 0:
            speaker = 'Facilitator'
        # if speaker between 1-8
        elif speaker in range(1, 9):
            speaker = 'p' + str(int(speaker))
        else:
            speaker = 'unknown speaker'

        text_out = text_out + str(index) + ". " + speaker + ': \'' + str(context) + '\' \n'
    return text_out


def df_to_context(df):
    """
    Convert the dataframe to the context that can be used for the GPT model
    :param df: the transcript dataframe
    :return: speaker, context
    """
    # df=game_round_transcript
    text_out = ''
    for index, row in df.iterrows():
        if row['trans'] is None:
            continue
        speaker = row['speaker']
        # change the speaker to player1, player2, player3, player4, player5, player6, player7, player8
        if speaker == 0:
            speaker = 'Facilitator'
        # if speaker between 1-8
        elif speaker in range(1, 9):
            speaker = 'p' + str(int(speaker))
        else:
            speaker = 'unknown speaker'

        context = row['trans']
        text_out = text_out + speaker + ': \'' + str(context) + '\'' + '\n'

    return text_out


from transformers import GPT2Tokenizer

# Initialize the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# read transcript file

# Load  CSV file using pandas
# read the file
transcript = pd.read_csv('Data/transcripts_cleaned.csv')

# read the game names from the csv
game_info = pd.read_csv('game_info.csv')
game_names = game_info['game_name'].unique()

# count the number of tokens, rows and length of the conversation and store
by_round_info = []
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# process by round
for ind, game in game_info.iterrows():
    game_name = game['game_name']
    for round in range(1, game['max_round'] + 1):
        # print(game_name, round)
        # game_name = '006AZ'
        # round = 5
        # get the transcript for the game and round
        game_round_transcript = transcript[
            (transcript['game'] == game_name) & (transcript['round'] == 'round' + str(round))]
        # count the number of rows and length of the conversation and store
        conversation = df_to_context_w_index(game_round_transcript)
        tokens = tokenizer.tokenize(conversation)
        by_round_info.append({'game': game_name, 'round': round, 'num_rows': game_round_transcript.shape[0],
                              'conversation_length': len(conversation), 'num_tokens': len(tokens)})

by_round_info_df = pd.DataFrame(by_round_info)

# show the average conversation length and row
print("average conversation_length for "+by_round_info_df['conversation_length'].mean())
print("average num_rows for "+by_round_info_df['num_rows'].mean())
print("average num_tokens for "+by_round_info_df['num_tokens'].mean())

