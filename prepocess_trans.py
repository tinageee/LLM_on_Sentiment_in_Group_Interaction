import csv
import re
import pandas as pd
import os
import warnings
import zipfile


# Ignore the SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# Set the file path
path = "/Users/saiyingge/**Research Projects/Nomination-network/data/Tags_in_2022/Tagged"
output_path = "/Users/saiyingge/**Research Projects/Nomination-network/data/Cleaned_2023"

# List all files with the specific pattern
files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('T.xlsx')]


def contains_odd_symbols(s):
    """Check if string contains odd symbols."""
    pattern = r'[^a-zA-Z0-9,.!\' ?[]]'
    return bool(re.search(pattern, s))

def read_excel_file(filepath):
    """Attempt to read an Excel file using different engines."""
    try:
        return pd.read_excel(filepath)
    except ValueError:
        try:
            return pd.read_excel(filepath, engine='openpyxl')
        except zipfile.BadZipFile:
            print(f"File {filepath} appears to be corrupted or not a valid Excel file.")
        except Exception as e:
            print(f"Failed to read {filepath} with error: {e}")
    return None


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

    # Remove timestamps from 'trans' column
    df['trans'] = df['trans'].str.replace(r'\[\d{1,2}:\d{2}:\d{2}\]', '', regex=True)

    # Remove ?€? with ' # 003ISR
    df['trans'] = df['trans'].str.replace('?€?', '')  # for removing the sequence

    return df


all_issues = []
# orginal screening
for x in files:
    # x= "/Users/saiyingge/**Research Projects/Nomination-network/data/Tags_in_2022/Tagged/007SB_T.xlsx"
    df = read_excel_file(x)

    if df is None:
        continue
    # fix the transcript

    # Check for missing data in specified columns
    cols_to_check = ['round', 'speaker', 'trans']
    missing_data_rows = df[df[cols_to_check].isnull().any(axis=1)].copy()

    if not missing_data_rows.empty:
        missing_data_rows['issue'] = "Missing Data"
        all_issues.append(missing_data_rows)

    # Check for odd symbols in 'trans'
    odd_symbol_rows = df[df['trans'].apply(lambda x: isinstance(x, str) and contains_odd_symbols(x))]

    if not odd_symbol_rows.empty:
        odd_symbol_rows['issue'] = "Odd symbols in 'trans'"
        all_issues.append(odd_symbol_rows)

# with data filtered

filtered_issues = []
for x in files:
    # x= "/Users/saiyingge/**Research Projects/Nomination-network/data/Tags_in_2022/Tagged/007SB_T.xlsx"
    df = read_excel_file(x)

    if df is None:
        continue
    # fix the transcript
    df = clean_transcript(df)

    # Check for missing data in specified columns
    cols_to_check = ['round', 'speaker', 'trans']
    missing_data_rows = df[df[cols_to_check].isnull().any(axis=1)].copy()

    if not missing_data_rows.empty:
        missing_data_rows['issue'] = "Missing Data"
        filtered_issues.append(missing_data_rows)

    # Check for odd symbols in 'trans'
    odd_symbol_rows = df[df['trans'].apply(lambda x: isinstance(x, str) and contains_odd_symbols(x))]

    if not odd_symbol_rows.empty:
        odd_symbol_rows['issue'] = "Odd symbols in 'trans'"
        filtered_issues.append(odd_symbol_rows)

# Combine all issues into a single DataFrame
filtered_df = pd.concat(filtered_issues)


