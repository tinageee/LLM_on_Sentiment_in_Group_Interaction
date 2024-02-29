'''
This script preprocesses the transcripts by:
- Forward filling the missing values in the 'round' column
- Removing \t, \n characters, and other specified sequences
- Checking for missing data in specified columns
- Checking for odd symbols
- Saving the cleaned data to a new CSV file

'''

import re
import pandas as pd
import warnings
import json

# Ignore the SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# use the transcripts with high quality, read the game names from the csv file
# Read the raw labels from CSV
# read file based on the game names
with open("config.json") as config_file:
    config = json.load(config_file)
    csv_file_path = config["csv_file_path"]

transcripts = pd.read_csv(csv_file_path)
game_names = transcripts['game'].unique()


def contains_odd_symbols(s):
    """Check if string contains odd symbols."""
    pattern = r'[^a-zA-Z0-9,.!\' ?[]]'
    return bool(re.search(pattern, s))


def clean_transcript(df: pd.DataFrame) -> pd.DataFrame:
    # other note- 003USP too broken
    """
    Cleans the given dataframe by:
    - Forward filling the missing values in the 'round' column
    - Removing \t, \n characters, and other specified sequences from the 'trans' column

    Parameters:
    - df (pd.DataFrame): The input dataframe

    Returns:
    - pd.DataFrame: The cleaned dataframe
    """

    def clean_transcript(text):
        # Remove patterns like "@number number@" # eg 007SB
        cleaned_text = re.sub(r'@\d+ \d+@', '', text)
        return cleaned_text

    # Assuming df is your DataFrame and 'trans' is the column containing transcripts
    df['trans'] = df['trans'].apply(lambda x: clean_transcript(x) if isinstance(x, str) else x)

    # Forward fill the missing values in 'round' column
    df['round'] = df['round'].fillna(method='ffill')

    # Remove \t and \n characters
    df['trans'] = df['trans'].str.replace('\t', '').str.replace('\n', '')

    # remove ?�?
    df['trans'] = df['trans'].str.replace('?�?', '')

    # Remove the sequence _x000b__x000b_ from 'trans' column
    df['trans'] = df['trans'].str.replace('_x000b__x000b_', '')
    df['trans'] = df['trans'].str.replace('_x000D_ _x000D_', '')
    df['trans'] = df['trans'].str.replace('_x000D_', '')

    # Remove timestamps from 'trans' column
    df['trans'] = df['trans'].str.replace(r'\[\d{1,2}:\d{2}:\d{2}\]', '', regex=True)

    # Remove ?€? with ' # 003ISR
    df['trans'] = df['trans'].str.replace('?€?', '')  # for removing the sequence

    # replace p1, p2, p3, p4, p5, p6, p7, p8 with player1, player2, player3, player4, player5, player6, player7, player8, ignore the case
    # df['trans'] = df['trans'].str.replace('p1', 'player1', case=False)
    # df['trans'] = df['trans'].str.replace('p2', 'player2', case=False)
    # df['trans'] = df['trans'].str.replace('p3', 'player3', case=False)
    # df['trans'] = df['trans'].str.replace('p4', 'player4', case=False)
    # df['trans'] = df['trans'].str.replace('p5', 'player5', case=False)
    # df['trans'] = df['trans'].str.replace('p6', 'player6', case=False)
    # df['trans'] = df['trans'].str.replace('p7', 'player7', case=False)

    return df


def screening_transcript(transcripts: pd.DataFrame, game_names) -> pd.DataFrame:
    """
    Screening the given dataframe by:
    - Checking for missing data in specified columns
    - Checking for odd symbols

    Parameters:
    - df (pd.DataFrame): The input dataframe

    Returns:
    - pd.DataFrame: The screened dataframe
    """
    all_issues = []
    # original screening
    for game in game_names:
        # find the corresponding transcript
        game_trans = transcripts[transcripts['game'] == game]

        if game_trans is None:
            print(f"Transcript {game} not found")
            continue
        # Check for missing data in specified columns
        cols_to_check = ['round', 'speaker', 'trans']
        missing_data_rows = game_trans[game_trans[cols_to_check].isnull().any(axis=1)].copy()

        if not missing_data_rows.empty:
            missing_data_rows['issue'] = "Missing Data"
            all_issues.append(missing_data_rows)

        # Check for odd symbols in 'trans'
        odd_symbol_rows = game_trans[
            game_trans['trans'].apply(lambda x: isinstance(x, str) and contains_odd_symbols(x))]

        if not odd_symbol_rows.empty:
            odd_symbol_rows['issue'] = "Odd symbols in 'trans'"
            all_issues.append(odd_symbol_rows)

    # with data filtered
    all_issues_df = pd.concat(all_issues)
    print(all_issues_df['issue'].value_counts())

    return all_issues_df


issue_b4_cleaning = screening_transcript(transcripts, game_names)

# clean transcript and remove the missing data
transcripts = clean_transcript(transcripts)
transcripts = transcripts.dropna(subset=['trans'])

issue_after_cleaning = screening_transcript(transcripts, game_names)

# drop off the labels
transcripts = transcripts.drop(columns=['raw_labels'])
# save the cleaned data

# Save the cleaned data to a new CSV file
transcripts.to_csv('Data/transcripts_cleaned.csv', index=False)
