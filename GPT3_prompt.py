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

# Read the API key from the configuration file
with open("config.json") as config_file:
    config = json.load(config_file)
    api_key = config["api_key"]

# Set your OpenAI API Key
openai.api_key = api_key

# Define a function to generate sentiment scores based on input data
def generate_sentiment_scores(input_data):
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
    return response.choices[0].text.strip()

# Example usage:
input_data = {
    "context": {
        "facilitator": "Okay, is there any discussion for player six? Do you have any justification or do the rest of you have questions?",
        "player3": "Any reason for that or just?",
        "player6": "Yeah, I think you want to approve the mission.",
        "player1": "Why do you choose p3 after you?"
    },
    "targetTurnOfTalk": {
        "player7": "P3 is a conspirator."
    }
}

# Call the function to generate sentiment scores and print the output
output = generate_sentiment_scores(input_data)
print(output)  # This will print the model's output
