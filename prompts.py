prompt_for_round_include_refIndx = '''
Goal:
You are an advanced AI tasked with analyzing player interactions during a round of the "Resistance" game. Your primary function is to evaluate comments made during discussions to ascertain the sentiments players harbor towards each other, assigning corresponding sentiment scores. These scores should range from -1 to 1, where -1 indicates the player is perceived as a deceptive spy, and 1 suggests the player is viewed as a trustworthy villager or leader candidate.

Rules:
- Players are identified by labels p1 through p8.
- The speaker and the mentioned player must not be the same individual. speaker != mentionedPlayer. no self-mention.
- Focus solely on tagging conversations that exhibit clear positive or negative sentiment. Accompany each identified sentiment with a brief reasoning and the index of the conversation from the input where the sentiment was observed.
- A facilitator is present within the game context but does not participate in the sentiment analysis. no facilitator in speaker or mentionedPlayer
- The output should be in JSON format, detailing the sentiment scores as specified, along with the index of the conversation from which each sentiment was derived.

Example Input:
{ "1. P2: 'I trust p4 completely, but I'm unsure about p5. p6 seems to be hiding something.' 
  2. P5: 'What player would you pick for the mission?'
  ...
  10. P3: 'I will pick p2, p4 for the mission.' 
  11. P7: 'I agree with your choices.'
  ...
  66. P8: 'I have a feeling p4 is a villager and I would like nominate her for this round's leader.'
"
}

Expected Output:
{
  "sentimentScores": [
    {
      "speaker": "p2",
      "mentionedPlayer": "p4",
      "score": 1,
      "reason": "Expressed complete trust.",
      "conversationIndex": 1
    },
    {
      "speaker": "p2",
      "mentionedPlayer": "p6",
      "score": -1,
      "reason": "Suggested deception.",
      "conversationIndex": 1
    },
    {
      "speaker": "p3",
      "mentionedPlayer": "p2",
      "score": 1,
      "reason": "Selected for team.",
      "conversationIndex": 10
    },
    {
      "speaker": "p3",
      "mentionedPlayer": "p4",
      "score": 1,
      "reason": "Selected for team.",
      "conversationIndex": 10
    },
    {
      "speaker": "p7",
      "mentionedPlayer": "p3",
      "score": 1,
      "reason": "Supported p3's choice.",
      "conversationIndex": 11
    }
    {
      "speaker": "p8",
      "mentionedPlayer": "p4",
      "score": 1,
      "reason": "seems to be a villager and nominated for leader.",
      "conversationIndex": 66
    }
  ]
}
'''

prompt_for_round_include_context = '''
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
      "score": 1,
      "reason": "select for team"
    }
    {
      "speaker": "p3",
      "mentionedPlayer": "p5",
      "score": 1,
      "reason": "select for team"
    }
    {
      "speaker": "p7",
      "mentionedPlayer": "p3",
      "score": 0.5,
      "reason": "support p3's choice"
    }
  ]
}

'''

prompt_for_round_include_context_and_refIndx = '''
Goal:
You are an advanced AI designed to analyze player interactions during a game of "Resistance." Your objective extends to evaluating comments made during discussions to ascertain the sentiments players hold towards each other, assigning sentiment scores accordingly. Additionally, you are tasked with incorporating context from previous rounds into your analysis to produce a summary that captures the overall dynamics and strategies at play. The sentiment scores range from -1 to 1, with -1 indicating a player is perceived as a deceptive spy, and 1 indicating the player is seen as a trustworthy villager or leader candidate.

Rules:
- Players are identified with labels p1 through p8.
- The speaker and the mentioned player must not be the same individual. speaker != mentionedPlayer
- Focus on tagging conversations that clearly exhibit positive or negative sentiment. For each sentiment identified, provide a concise reasoning along with the index of the conversation from the input where the sentiment was observed.
- Incorporate the provided context into your analysis to enhance the accuracy of your sentiment scores and the depth of your summary.
- A facilitator is present in the game context but does not participate in the sentiment analysis.
- Output should be in JSON format, detailing the sentiment scores as specified, and include a summary that reflects the context and the essence of the discussions observed.

Example Input:
{
  "context": "Earlier rounds have seen fluctuating alliances and growing suspicions. P1 and P3 have shown skepticism towards P5's recent actions, hinting at potential deceit.",
  "discussions": [
    "1. P2: 'I trust p4 completely, but I'm unsure about p5. p6 seems to be hiding something.'",
    "2. P5: 'What player would you pick for the mission?'",
    "...",
    "10. P3: 'I will pick p2, p4 for the mission.'",
    "11. P7: 'I agree with your choices.'",
    "...",
    "66. P8: 'I have a feeling p4 is a villager and I would like to nominate her for this round's leader.'"
  ]
}

Expected Output:
{
  "summaryDiscussions": "p2 trusts p4,doubts p6. P3's decision to pick P2 and P4 for the mission, supported by P7. P8's nomination of P4 as a leader.",
  "sentimentScores": [
    {
      "speaker": "p2",
      "mentionedPlayer": "p4",
      "score": 1,
      "reason": "Expressed complete trust.",
      "conversationIndex": 1
    },
    {
      "speaker": "p2",
      "mentionedPlayer": "p5",
      "score": -0.5,
      "reason": "Expressed uncertainty.",
      "conversationIndex": 1
    },
    {
      "speaker": "p2",
      "mentionedPlayer": "p6",
      "score": -1,
      "reason": "Suggested deception.",
      "conversationIndex": 1
    },
    {
      "speaker": "p3",
      "mentionedPlayer": "p2",
      "score": 1,
      "reason": "Selected for team.",
      "conversationIndex": 10
    },
    {
      "speaker": "p3",
      "mentionedPlayer": "p4",
      "score": 1,
      "reason": "Selected for team.",
      "conversationIndex": 10
    },
    {
      "speaker": "p7",
      "mentionedPlayer": "p3",
      "score": 0.5,
      "reason": "Supported p3's choice.",
      "conversationIndex": 11
    },
    {
      "speaker": "p8",
      "mentionedPlayer": "p4",
      "score": 1,
      "reason": "Viewed as a villager and nominated for leader.",
      "conversationIndex": 66
    }
  ]
}
'''

prompt_terms='''
Goal:\nIn the 'Resistance' game, assign sentiment scores to players based on a specific player's comment during their turn of talk.\n\nRules:\nThe player speaking provides comments.\nPlayers discussed receive scores.\nScores range from -1 to 1:\n-1: Seen as a deceptive spy.\n0: Neutral sentiment.\n1: Seen as a trustworthy villager, and if nominated as a leader.
\nPlayers can be labeled as p1, p2, up to p8.\nA \"facilitator\" guides the game.
\nScores are derived from the current comment but consider previous comments for context.
\nFeedback is given in JSON format.\n
\nHow to Use:\nSubmit the current comment and some prior context. Receive sentiment scores based on that.\n\nInput format: {\n  \"context\": { \"previous comments\" },\n  \"targetTurnOfTalk\": { \"current comment\" }\n}\n\nOutput format: {\n  \"speakingPlayer\": {\n    \"mentionedPlayer\": {\n      \"score\": \"assigned score\",\n      \"reason\": \"brief explanation\"\n    }\n  }\n}\n\n" + input_str + "\nOutput:",
'''

# # Example usage:
# input_data = {
#     "context": {
#         "Facilitator": "Okay, is there any discussion for player six? Do you have any justification or do the rest of you have questions?",
#         "player3": "Any reason for that or just?",
#         "player6": "Yeah, I think you want to approve the mission.",
#         "player1": "Why do you choose p3 after you?"
#     },
#     "targetTurnOfTalk": {
#         "player7": "P3 is a conspirator."
#     }
# }
#
# # Call the function to generate sentiment scores and print the output
# output = generate_sentiment_scores_by_terms(input_data)
# print(output.choices[0].text.strip())  # This will print the model's output
