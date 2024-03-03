import networkx as nx
import pandas as pd


def manualLabel_network_links(game_name):
    # read the networks with game name
    Code_dir = '/Users/saiyingge/Coding Projects/PyCharmProjects/NetworkProject/'

    network = nx.read_graphml(Code_dir + 'Data/Networks/' + game_name + '.graphml')
    # get the edges info
    links = pd.DataFrame(network.edges(data=True), columns=['from', 'to', 'link_info'])

    # Expand the 'link_info' dictionary into separate columns
    links = pd.concat([links.drop(['link_info'], axis=1), links['link_info'].apply(pd.Series)], axis=1)
    # change round to int
    links['round'] = links['round'].str.extract('(\d+)').astype(int)
    links['sign'] = links['sign'].astype(int)
    links['from'] = links['from'].astype(int)
    links['to'] = links['to'].astype(int)

    # check duplicates in the link
    links.duplicated().sum()

    return links


def gptLabel_network_links(df_scores_output):
    #drop na
    df_scores_output = df_scores_output.dropna()
    # from the speaker
    df_scores_output['from'] = df_scores_output['speaker'].str.extract('(\d+)').dropna().astype(int)
    # to the mentionedPlayer
    df_scores_output['to'] = df_scores_output['mentionedPlayer'].str.extract('(\d+)').dropna().astype(int)
    # sign of the sentiment if the secore is positive, negative, or neutral
    df_scores_output['sign'] = df_scores_output['score'].apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)
    #drop the sign =0
    df_scores_output = df_scores_output[df_scores_output['score'] != 0]

    # only keep the columns that are needed
    df_scores_output = df_scores_output[['from', 'to', 'sign', 'round']]
    # remove the duplicates
    df_scores_output = df_scores_output.drop_duplicates()
    # remove the self-loops
    df_scores_output = df_scores_output[df_scores_output['from'] != df_scores_output['to']]

    return df_scores_output


def compare_links_percentage(game_name, df_scores_all):
    manual_links = manualLabel_network_links(game_name)
    gpt_links = gptLabel_network_links(df_scores_all)

    # Convert to sets of tuples for easy comparison
    manual_set = set(zip(manual_links['from'], manual_links['to'], manual_links.get('sign', ''), manual_links.get('round', '')))
    gpt_set = set(zip(gpt_links['from'], gpt_links['to'], gpt_links.get('sign', ''), gpt_links.get('round', '')))

    # Calculate the intersection (overlap) of the two sets
    overlap = manual_set & gpt_set

    # Convert the overlap back to a DataFrame for further analysis or reporting
    overlap_df = pd.DataFrame(list(overlap), columns=['from', 'to', 'sign', 'round'])

    # Calculate the percentage of overlap relative to the total number of unique links
    total_unique_links = len(manual_set | gpt_set)  # Union of both sets for total unique links
    overlap_percentage = (len(overlap) / total_unique_links) * 100 if total_unique_links > 0 else 0
    common_in_gpt =len(overlap) / len(gpt_set) * 100
    common_in_manual = len(overlap) / len(manual_set) * 100

    print(f"Overlap: {len(overlap)} links")
    print(f"Overlap Percentage: {overlap_percentage:.2f}%")
    print(f"percentage of common links in GPT: {common_in_gpt:.2f}%")
    print(f"percentage of common links in manual: {common_in_manual:.2f}%")


    # Return the percentages
    return overlap_percentage, common_in_gpt, common_in_manual




