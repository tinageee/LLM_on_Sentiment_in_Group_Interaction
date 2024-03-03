"""
OpenAI Sentiment Analysis

This script uses the OpenAI GPT-3.5 Turbo model to assign sentiment scores to players' comments in a game context.

Author: Tina Ge
Date: Oct,2023
updated: Mar,2024

Usage:
1. Set OpenAI API key in the 'api_key' variable.
2. Define the input data with comments from players and the target player's comment.
3. Call the 'generate_sentiment_scores' function with the input data to obtain sentiment scores.
4. The function will return sentiment scores for mentioned players in JSON format.
5. test with different prompts, models, and model parameters and comparison result will be saved to a json file.

"""
from datetime import time, datetime

# Import necessary libraries
import openai
import json
import pandas as pd
import numpy as np
import re
from transformers import GPT2Tokenizer
from datetime import datetime, timedelta
import time

# read the prompt from prompts.py
from prompts import prompt_for_round_include_refIndx, prompt_for_round_include_context, \
    prompt_for_round_include_context_and_refIndx

'''
number of tokens
prompt_for_round_include_refIndx = 675
prompt_for_round_include_context = 566
prompt_for_round_include_context_and_refIndx = 822


'''
from compare_gpt_manual_output_links import compare_links_percentage

# Read the API key from the configuration file
with open("config.json") as config_file:
    config = json.load(config_file)
    api_key = config["api_key"]

# Set  OpenAI API Key
openai.api_key = api_key

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")


def segment_dataframe_with_indx(df, token_limit):
    # List to hold the segmented data
    segments = []

    current_segment = ''
    current_tokens = 0

    for _, row in df.iterrows():
        # Skip if the 'trans' field is NaN
        if pd.isna(row['trans']):
            continue

        speaker = "Facilitator" if row['speaker'] == 0 else (
            f"p{int(row['speaker'])}" if 1 <= row['speaker'] <= 8 else "unknown")

        conversation = row['trans']
        idx = int(row['indx'])
        row_text = f"{idx}. {speaker}: {conversation}\n"  # Added '\n' for readability
        row_tokens = len(tokenizer.tokenize(row_text))

        # Check if adding this row exceeds the token limit
        if current_tokens + row_tokens <= token_limit:
            # Add the row to the current segment
            current_segment += row_text
            current_tokens += row_tokens
        else:
            # Current segment is full, add it to the segments list
            segments.append(current_segment.strip())  # Strip to remove any trailing newline
            # Start a new segment with the current row
            current_segment = row_text
            current_tokens = row_tokens

    # Add the last segment if it contains any rows
    if current_segment:
        segments.append(current_segment.strip())  # Ensure it's added as a string

    return segments


def gpt3_generate_sentiment_scores_by_round(input_data, gpt_model, prompt_for_round, token_limit):
    '''
    Generate sentiment scores based on the input data using the OpenAI GPT-3 model.
    :param input_data: the input data with group conversation
    :param gpt_model:   the GPT model to use
    :param prompt_for_round:    the prompt for the round
    :return:    the GPT model's output, defined in the prompt
    '''
    # Convert input to string format for the prompt
    input_str = "Input:" + str(input_data)

    # Generate a response using the OpenAI GPT-3 model
    response = openai.Completion.create(
        model=gpt_model,
        prompt=prompt_for_round + input_str + "\nOutput:",
        temperature=0,
        max_tokens=token_limit,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["Input", "Output"]
    )

    # Return the model's output as a string
    return response  # .choices[0].text.strip()


def gpt4_chatcompletion_generate_sentiment_scores_by_round(input_data, prompt_for_round, gpt_model):
    """
    Generate sentiment scores based on the input data using the OpenAI GPT-4 model.

    :param input_data: The input data with group conversation.
    :param prompt_for_round: The prompt for the round.
    :param gpt_model: The GPT model to use; defaults to 'gpt-4'. Note that the input for GPT-4 may differ from GPT-3.
    :return: The response from the GPT model.
    """
    # Ensure the API key is set in your environment or set it directly here
    # openai.api_key = "your-api-key-here"

    input_str = "Input:" + str(input_data)
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": prompt_for_round},  # System message setting the context
            {"role": "user", "content": input_str + "\nOutput:"}  # User message with the actual prompt/data
        ],
        stop=["Input", "Output"]  # Define stopping points to control the output
    )

    return response


def split_text_into_segments(text, token_limit):
    tokens = tokenizer.tokenize(text)
    segments = []
    current_segment = []

    for token in tokens:
        if len(current_segment) + 1 <= token_limit:
            current_segment.append(token)
        else:
            segments.append(tokenizer.convert_tokens_to_string(current_segment))
            current_segment = [token]

    # Add the last segment if not empty
    if current_segment:
        segments.append(tokenizer.convert_tokens_to_string(current_segment))

    return segments


def trim_and_repair_json(text):
    '''
    some of the output from the model may not be valid JSON, so we need to trim the input text to the last complete sentiment score object and attempt to repair it as valid JSON.
    Trim the input text to the last complete sentiment score object and attempt to repair it as valid JSON.
    :param text:
    :return:
    '''
    #trim the front of the text, keep after first'{
    text = text[text.find('{'):]

    # Find all complete sentiment score objects
    complete_objects = re.findall(r'\{\s*"speaker":.*?\n\s*\}', text, re.DOTALL)

    # If no complete objects are found, return an error or empty JSON
    if not complete_objects:
        return '{}'

    # Get the last complete object and find its last occurrence in the text
    last_complete_object = complete_objects[-1]
    last_object_index = text.rfind(last_complete_object)

    # Trim the text up to and including the last complete object
    trimmed_text = text[:last_object_index + len(last_complete_object)]

    # Close the sentimentScores array and the root object
    trimmed_text += '\n  ]\n}'  # Assuming the structure is as shown in your example

    # Attempt to parse the trimmed text to ensure it's valid JSON
    try:
        parsed_json = json.loads(trimmed_text)
        return parsed_json
    except json.JSONDecodeError as e:
        # Handle JSON errors (e.g., log them)
        print(f"JSON error after trimming: {e}")
        return None


def test_gpt3_model(game_name, gpt_model, prompt_text, input_token_limit, output_token_limit):
    '''
    Test the GPT-3 model with the given parameters on the specified game.

    :param game_name:   the name of the game to test the model on
    :param gpt_model:   the GPT model to use
    :param prompt_text:     the prompt for the round
    :param input_token_limit:   the maximum number of tokens for the input data
    :param output_token_limit:  the maximum number of tokens for the output data
    :return:    json file with the model parameters and comparison result, df_model_all, df_scores_all
    '''
    start_time_overall = time.time()
    # Filter the transcript for the current game
    game_round_transcript = transcript[transcript['game'] == game_name]
    game_round = game_info[game_info['game_name'] == game_name]['max_round'].values[0]

    df_scores_all = pd.DataFrame()
    df_model_all = pd.DataFrame()

    for current_round in range(1, game_round + 1):
        print(f"Processing round {current_round} for game {game_name}")
        # Filter the transcript for the current round
        game_round_transcript_by_round = game_round_transcript[game_round_transcript['round'] == f'round{current_round}']

        # Divide the conversation into smaller pieces and Convert the conversation to context with index
        segments = segment_dataframe_with_indx(game_round_transcript_by_round, input_token_limit)

        for segment in segments:
            # Process each segment with the model
            output = gpt3_generate_sentiment_scores_by_round(segment, gpt_model, prompt_text,
                                                             output_token_limit)

            # Parse the JSON
            data = trim_and_repair_json(output.choices[0].text.strip())

            if not data or 'sentimentScores' not in data or not data['sentimentScores']:
                print(f"data is na when processing segment for {game_name} round {current_round}")
                print(f"gpt out put{output.choices[0].text.strip()}")
                print(f" the input is: {segment}")
                continue

            # Process and collect data as before
            df_scores = pd.DataFrame(data['sentimentScores'])
            df_scores['round'] = current_round
            df_scores['game'] = game_name
            df_scores_all = pd.concat([df_scores_all, df_scores], ignore_index=True)

            # Assuming model info collection is similar
            df_model = pd.DataFrame({'model_name': [gpt_model]})
            df_model['prompt_tokens'] = output.usage.prompt_tokens
            df_model['completion_tokens'] = output.usage.completion_tokens
            df_model['total_tokens'] = output.usage.total_tokens
            df_model['round'] = current_round
            df_model['game'] = game_name
            df_model_all = pd.concat([df_model_all, df_model], ignore_index=True)

    # compare the output from gpt with human labeled network
    end_time_overall = time.time()  # End timing the entire function execution
    overall_processing_time = end_time_overall - start_time_overall  # Calculate overall processing time

    # Comparison and JSON output
    Overlap, common_in_gpt, common_in_manual = compare_links_percentage(game_name, df_scores_all)
    time_stamp = datetime.now().strftime("%Y-%m-%d-%H:%M")
    model_parameters_and_result = {
        "model_name": gpt_model, "test_game": game_name,
        "game_rounds_num": game_round, "input_token_limit": input_token_limit,
        "output_token_limit": output_token_limit, "Overlap_Percentage": Overlap,
        "common_in_gpt_Percentage": common_in_gpt,"common_in_manual_Percentage": common_in_manual,
        "total_tokens": int(df_model_all['total_tokens'].sum()),  # Ensure conversion to Python int type
        "overall_processing_time": overall_processing_time, 'time_stamp': time_stamp, "prompt": prompt_text
    }

    print(model_parameters_and_result)
    for key, value in model_parameters_and_result.items():
        if isinstance(value, np.integer):
            model_parameters_and_result[key] = int(value)

    with open(f'Data/model_comparison_{time_stamp}.json', 'w') as f:
        json.dump(model_parameters_and_result, f, indent=4)

    return df_model_all, df_scores_all


def test_gpt4_model(game_name, gpt_model, prompt_text, input_token_limit, output_token_limit):
    start_time_overall = time.time()
    # Initial setup
    game_round_transcript = transcript[transcript['game'] == game_name]
    game_round = game_info[game_info['game_name'] == game_name]['max_round'].values[0]

    df_scores_all = pd.DataFrame()
    df_model_all = pd.DataFrame()

    # Iterate through each round
    for current_round in range(1, game_round + 1):
        print(f"Processing round {current_round} for game {game_name}")
        game_round_transcript_by_round = game_round_transcript[
            game_round_transcript['round'] == f'round{current_round}']

        # Segment the conversation
        segments = segment_dataframe_with_indx(game_round_transcript_by_round, input_token_limit)

        for segment in segments:
            output = gpt4_chatcompletion_generate_sentiment_scores_by_round(segment, prompt_text, gpt_model)
            data = trim_and_repair_json(output.choices[0].message['content'])

            if not data or 'sentimentScores' not in data or not data['sentimentScores']:
                print(f"data is na when processing segment for {game_name} round {current_round}")
                continue

            # Processing data
            df_scores = pd.DataFrame(data['sentimentScores'])
            df_scores['round'] = current_round
            df_scores['game'] = game_name
            df_scores_all = pd.concat([df_scores_all, df_scores], ignore_index=True)

            # Model info collection
            df_model = pd.DataFrame({'model_name': [gpt_model], 'round': current_round, 'game': game_name,
                                     'prompt_tokens': output.usage.prompt_tokens,
                                     'completion_tokens': output.usage.completion_tokens,
                                     'total_tokens': output.usage.total_tokens})
            df_model_all = pd.concat([df_model_all, df_model], ignore_index=True)

    end_time_overall = time.time()  # End timing the entire function execution
    overall_processing_time = end_time_overall - start_time_overall  # Calculate overall processing time

    # Comparison and JSON output
    Overlap, common_in_gpt, common_in_manual = compare_links_percentage(game_name, df_scores_all)
    time_stamp = datetime.now().strftime("%Y-%m-%d-%H:%M")
    model_parameters_and_result = {
        "model_name": gpt_model, "test_game": game_name,
        "game_rounds_num": game_round, "input_token_limit": input_token_limit,
        "output_token_limit": output_token_limit, "Overlap_Percentage": Overlap,
        "common_in_gpt_Percentage": common_in_gpt,"common_in_manual_Percentage": common_in_manual,
        "total_tokens": int(df_model_all['total_tokens'].sum()),  # Ensure conversion to Python int type
        "overall_processing_time": overall_processing_time, 'time_stamp': time_stamp, "prompt": prompt_text
    }

    print(model_parameters_and_result)
    for key, value in model_parameters_and_result.items():
        if isinstance(value, np.integer):
            model_parameters_and_result[key] = int(value)


    with open(f'Data/model_comparison_{time_stamp}.json', 'w') as f:
        json.dump(model_parameters_and_result, f, indent=4)

    return df_model_all, df_scores_all


# using test data
transcript = pd.read_csv('Data/transcripts_cleaned.csv')

# Initialize the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# read the game info from the csv
game_info = pd.read_csv('game_info.csv')
game_names = game_info['game_name'].unique()

# Define the input data with comments from players and the target player's comment
# gpt_model = "davinci-002"
# gpt_model = "gpt-3.5-turbo-0125"
# test on game 001ISR
game_name = '001ISR'

prompt_text = prompt_for_round_include_refIndx

# the gpt3 model's maximum context length is 4097 tokens  token of prompt_for_round_include_refIndx = 675
input_token_limit = 1500  # Adjust based on model and desired completion length
output_token_limit = 1500  # Adjust based on model and desired completion length

# gpt_model = "gpt-3.5-turbo-instruct"
gpt_model = "gpt-3.5-turbo-0125" # need use test_gpt4_model for chatcompletion model
# test the model on game 001ISR
df_model_all, df_scores_all=test_gpt3_model(game_name, gpt_model, prompt_text, input_token_limit, output_token_limit)

# test with gpt that use chatcompletion
# gpt_model = "gpt-3.5-turbo-0125"
# gpt_model = "gpt-4" #common configurations allowing around 4,096 to 8,192 tokens in total.
gpt_model = "gpt-4-1106-preview"
# gpt_model='gpt-4-0125-preview'
input_token_limit = 1500  # Adjust
# based on model and desired completion length
output_token_limit = 1000
df_model_all, df_scores_all=test_gpt4_model(game_name, gpt_model, prompt_text, input_token_limit, output_token_limit)
'''
performance gpt-4 > gpt-4-1106-preview > gpt-4-0125-preview > gpt-3.5-turbo-instruct > gpt-3.5-turbo-0125 > davinci-002
# the best model performance is "gpt-4" with input_token_limit = 2000 and output_token_limit = 1000
price gpt-4 > gpt-4-1106-preview > gpt-4-0125-preview > gpt-3.5-turbo-instruct > gpt-3.5-turbo-0125 > davinci-002

# considering the performance and price, the best model is "gpt-4-1106-preview" with input_token_limit = 2000 and output_token_limit = 1000

'''