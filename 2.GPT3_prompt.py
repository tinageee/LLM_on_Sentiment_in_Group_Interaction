"""
OpenAI Sentiment Analysis

This script uses the OpenAI GPT-3.5 Turbo model to assign sentiment scores to players' comments in a game context.

Author: Tina Ge
Date: Oct,2023

Usage:
1. Set OpenAI API key in the 'api_key' variable.
2. Define the input data with comments from players and the target player's comment.
3. Call the 'generate_sentiment_scores' function with the input data to obtain sentiment scores.
4. The function will return sentiment scores for mentioned players in JSON format.

"""
# Import necessary libraries
import os
import openai
import json
import pandas as pd

# Read the API key from the configuration file
with open("config.json") as config_file:
    config = json.load(config_file)
    api_key = config["api_key"]

# Set  OpenAI API Key
openai.api_key = api_key


# Define a function to generate sentiment scores based on input data
def generate_sentiment_scores_by_terms(input_data):
    # Convert input to string format for the prompt
    input_str = "Input:" + str(input_data)

    # Generate a response using the OpenAI GPT-3 model
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt="Goal:\nIn the 'Resistance' game, assign sentiment scores to players based on a specific player's comment during their turn of talk.\n\nRules:\nThe player speaking provides comments.\nPlayers discussed receive scores.\nScores range from -1 to 1:\n-1: Seen as a deceptive spy.\n0: Neutral sentiment.\n1: Seen as a trustworthy villager, and if nominated as a leader.\nPlayers can be labeled as p1, p2, up to p8.\nA \"facilitator\" guides the game.\nScores are derived from the current comment but consider previous comments for context.\nFeedback is given in JSON format.\n\nHow to Use:\nSubmit the current comment and some prior context. Receive sentiment scores based on that.\n\nInput format: {\n  \"context\": { \"previous comments\" },\n  \"targetTurnOfTalk\": { \"current comment\" }\n}\n\nOutput format: {\n  \"speakingPlayer\": {\n    \"mentionedPlayer\": {\n      \"score\": \"assigned score\",\n      \"reason\": \"brief explanation\"\n    }\n  }\n}\n\n" + input_str + "\nOutput:",
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["Input", "Output"]
    )

    # Return the model's output as a string
    return response  # .choices[0].text.strip()


# Example usage:
input_data = {
    "context": {
        "Facilitator": "Okay, is there any discussion for player six? Do you have any justification or do the rest of you have questions?",
        "player3": "Any reason for that or just?",
        "player6": "Yeah, I think you want to approve the mission.",
        "player1": "Why do you choose p3 after you?"
    },
    "targetTurnOfTalk": {
        "player7": "P3 is a conspirator."
    }
}

# Call the function to generate sentiment scores and print the output
output = generate_sentiment_scores_by_terms(input_data)
print(output.choices[0].text.strip())  # This will print the model's output

# Define a function to generate sentiment scores based on input data
prompt_for_round = '''

Goal:
You are an AI designed to analyze player interactions during the "Resistance" game. 
Your role involves evaluating comments made during a discussion round to determine players' sentiments towards each other and assign sentiment scores accordingly. 
Sentiment scores ranging from -1 to 1, where -1 indicates a player is perceived as a deceptive spy, 0 indicates neutrality, and 1 indicates the player is seen as a trustworthy villager or leader candidate.

Rules
Players are identified as p1 through p8.
A facilitator oversees the game but does not contribute to the sentiment analysis.
Sentiment scores are based on the current comments, with context from previous discussions considered when available.
The output will be in JSON format,  including both sentiment scores for the current round and a summary of current discussions.
speakingPlayer != mentionedPlayer

Example Input:
{
  "context": "In previous rounds, p1 expressed doubt about p3's loyalty. p4 has been consistently supportive of p5.",
  "currentRound": "P2: 'I trust p4 completely, but I'm unsure about p5. p6 seems to be hiding something.' P3: 'I will pick p2,p4,p5 for the mission.' p7: 'I agree with p3's choices.'"
}

Expected Output:
{
  "summaryDiscussions": "p2 trusts p4,doubts p6.",
  "sentimentScores": [
    {
      "speaker": "p2",
      "mentionedPlayer": "p4",
      "score": 1,
      "reason": "Expressed complete trust."
    },
    {
      "speaker": "p2",
      "mentionedPlayer": "p5",
      "score": -0.5,
      "reason": "Expressed uncertainty."
    },
    {
      "speaker": "p2",
      "mentionedPlayer": "p6",
      "score": -1,
      "reason": "Suggested deception."
    }
    {
      "speaker": "p3",
      "mentionedPlayer": "p2",
      "score": 1,
      "reason": "select for team"
    }
    {
      "speaker": "p3",
      "mentionedPlayer": "p4",
      "score": 1   ,
      "reason": "select for team"
    }
    {
      "speaker": "p3",
      "mentionedPlayer": "p5",
      "score": 1   ,
      "reason": "select for team"
    }
    {
      "speaker": "p7",
      "mentionedPlayer": "p3",
      "score": 0.5   ,
      "reason": "support p3's choice"
    }
  ]
}

'''


def generate_sentiment_scores_by_round(input_data, gpt_model):
    # Convert input to string format for the prompt
    input_str = "Input:" + str(input_data)

    # Generate a response using the OpenAI GPT-3 model
    response = openai.Completion.create(
        model=gpt_model,
        prompt=prompt_for_round + input_str + "\nOutput:",
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["Input", "Output"]
    )

    # Return the model's output as a string
    return response  # .choices[0].text.strip()


def gpt4_generate_sentiment_scores_by_round(input_data, gpt_model='gpt-4'):
    input_str = "Input:" + str(input_data)
    # Assuming 'input_data' is structured appropriately for your task
    # and 'gpt_model' specifies the model to use, e.g., 'gpt-4'
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": prompt_for_round},  # System message setting the context
            {"role": "user", "content": input_str + "\nOutput:"}  # User message with the actual prompt/data
        ]
        , stop=["Input", "Output"]
    )

    return response


# Call the function to generate sentiment scores and print the output
input_data = {
    "context": "na",
    "currentRound": text}
gpt_model= "gpt-3.5-turbo-instruct"
# gpt_model = 'gpt-4'
# gpt_model='davinci'
output = generate_sentiment_scores_by_round(input_data, gpt_model)
print(output)  # This will print the model's output
result = output.choices[0].text.strip()
#
# gpt4_output = gpt4_generate_sentiment_scores_by_round(input_data, gpt_model='gpt-4')
# print(gpt4_output)  # This will print the model's output
# gpt4_result = gpt4_output.choices[0].message.content

all_df_scores = pd.DataFrame()
all_df_summary = pd.DataFrame()

# Parse the JSON
data = json.loads(output.choices[0].text.strip())
# data = json.loads(gpt4_result)
# Create a DataFrame for sentiment scores
df_scores = pd.DataFrame(data['sentimentScores'])

# Handling the summary
# Since the summary is a single string, it's not typical to use a DataFrame for this purpose.
# However, if needed, you could create a simple DataFrame with a single row and column to hold it.
df_summary = pd.DataFrame({'summaryDiscussions': [data['summaryDiscussions']]})
# add column to store the model name and used token
df_summary['model_name'] = gpt_model
df_summary['token'] = output.usage.total_tokens

# Now you have 'df_scores' for sentiment scores and 'df_summary' for the summary of previous discussions
print("Sentiment Scores DataFrame:")
print(df_scores)
print("\nSummary DataFrame:")
print(df_summary)

all_df_scores = pd.concat([df_scores, all_df_scores], axis=0)
all_df_summary = pd.concat([df_summary, all_df_summary], axis=0)
