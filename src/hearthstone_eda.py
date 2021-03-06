import numpy as np
import pandas as pd
import json

def read_data():
    '''Initializes the two, uncleaned dataframes'''
    unclean_df = pd.read_csv("../data/hearthstone_decks.csv")
    json_df = pd.read_json("../data/refs.json")
    return unclean_df, json_df

def deck_list_create(unclean_df):
    '''takes the deck dataframe and combines all the single card columns into a single columns with a list of dbfIds'''
    card_col_ls = ['card_{}'.format(i) for i in range(30)] #creates list of column names for cards
    big_card_df = pd.DataFrame(unclean_df[card_col_ls], columns=card_col_ls) #creates a new dataframe with JUST the card columns so .values works correctly
    big_card_list = big_card_df.values.tolist() #makes list of lists of deck lists
    for ls in big_card_list:
        for idx, card in enumerate(ls):
            if card in broken_ids.keys():
                ls[idx] = broken_ids[card]
    unclean_df['card_list'] = tuple(map(tuple, big_card_list)) #makes new column where each value in big_card_list is mapped from a list to a tuple
    unclean_df.drop(card_col_ls, axis=1, inplace=True) #drops single card lists in favor of the new listed one
    return unclean_df

def deck_dataframe_creation(unclean_df):
    '''creates dataframes for different important deck types, none needs to be cleaned'''
    ranked_deck_df = unique_column_split(unclean_df, 'deck_type', 'Ranked Deck')
    none_df = unique_column_split(unclean_df, 'deck_type', 'None')
    tournament_df = unique_column_split(unclean_df, 'deck_type', 'Tournament')
    return ranked_deck_df, none_df, tournament_df

def unique_column_split(df, col_str, value):
    '''Returns a new dataframe from a given column in the dataframe where each row contains the inputted value at inputted column'''
    return pd.DataFrame(df[df[col_str] == value])

def fill_with_na(data_frame, fill_dict):
    '''Fills NaN values in given dataframe according to dictionary input'''
    data_frame.fillna(value=fill_dict, inplace=True)
    return data_frame


def drop_rows(data_frame, removal_dict):
    '''Drops all rows from a given data frame where the col = key in removal dict and the value@col = value in removal_dict'''
    drop_set = set()
    for key, value in removal_dict.items():
        drop_set.update(set(data_frame[data_frame[key] == value].index))
    data_frame.drop(drop_set, inplace=True)
    return data_frame
    

def drop_cols(data_frame, cols_to_drop):
    '''Drops columns from given dataframe. cols are inputted as a list in cols_to_drop'''
    data_frame.drop(cols_to_drop, axis=1, inplace=True)
    return data_frame


def weapon_durability_fixing(json_data):
    '''Fixes weapons having "SPELL" as health rather than their durability value'''
    weapon_index = json_data[json_data['type'] == 'WEAPON'].index
    for i in weapon_index:
        json_data['health'][i] = json_data['durability'][i]
    return json_data['health']


if __name__ == '__main__':

    unclean_df, json_df = read_data()
    #turns out there are some broken ids, fixing them early should help
    broken_ids = {836.0: 836.0, 137.0: 836.0, 253.0: 836.0,
    1681.0: 692.0, 38319.0: 692.0, 1682.0: 692.0, 692.0: 692.0,
    19292.0: 1929.0, 38710.0: 1929.0, 1929.0: 1929.0,
    2466.0: 2261.0, 2380.0: 2261.0, 41609.0: 2261.0, 2430.0: 2261.0,
    45369.0: 2261.0, 2652.0: 2261.0, 2558.0: 2261.0, 40259.0: 2261.0, 2261.0: 2261.0,
    13335.0: 13335.0, 38112.0: 13335.0, 38113.0: 13335.0,
    86.0: 86.0, 1161.0: 86.0, 928.0: 86.0,
    41408.0: 40372.0, 40372.0: 40372.0, 41409.0: 40372.0,
    2292.0: 2292.0, 2311.0: 2292.0, 38320.0: 2292.0, 2310.0: 2292.0,
    40402.0: 38266.0, 38266.0: 38266.0,
    42146.0: 40953.0, 40953.0: 40953.0, 42213.0: 40953.0,
    40341.0: 940.0, 40352.0: 940.0, 940.0: 940.0,
    690.0: 151.0, 276.0: 151.0, 322.0: 151.0, 468.0: 151.0, 151.0: 151.0,
    2048.0: 2048.0, 2230.0: 2048.0,
    179.0: 179.0, 38653.0: 179.0,
    2178.0: 2009.0, 2009.0: 2009.0, 2177.0: 2009.0, 2176.0: 2009.0}
    unclean_df = deck_list_create(unclean_df)
    ranked_decks, none_type, tournament = deck_dataframe_creation(unclean_df)
    df_list = [ranked_decks, none_type, tournament] #creates list of dfs to easily iterate future cleaning methods through them

    #defines dictionary for proper card.json NaN filling
    card_fill_dict = {
        'collectible' : 0, 
        'hideStats' : 0, 
        'race' : 'None', 
        'attack' : 'Spell',
        'health' : 'Spell',
        'durability' : 'None',
        'spellDamage' : 0,
        'overload' : 0,
        'text' : 'None',
        'referencedTags' : 'None',
        'mechanics' : 'None'
        } 

    #tells what rows to drop. Where col(key) == value
    card_row_drop_dict = {
        'collectible' : 0,
        'set' : 'HERO_SKINS',
        'type' : 'HERO'
    }

    #defines card.json cols to drop
    card_cols_to_drop = [
        'howToEarn',
        'howToEarnGolden',
        'playRequirements',
        'artist',
        'collectionText',
        'classes',
        'multiClassGroup',
        'hideStats',
        'targetingArrowText',
        'entourage',
        'elite',
        'faction',
        'flavor',
        'playerClass',
        'collectible', #shouldn't need this column assuming all cards in the df are correct
        'id' #this seems like an internal blizzard id, not the id we'll be using to create deck lists
        ]

    '''
    ORDER IS IMPORTANT HERE, MUST DO 
        1)FILL
        2)ROW DROP
        3)COL DROP
    '''

    json_df = drop_cols(drop_rows(fill_with_na(json_df, card_fill_dict), card_row_drop_dict), card_cols_to_drop)
    json_df['health'] = weapon_durability_fixing(json_df)
    #with the above code, the card DF should be as clean as it needs to be!

    #starting below is code to clean the deck df

    #drops the deck_type column in important dfs as it's redundant info in the df
    #this sorts the data frame by deck rating in order to keep the highest rated copy of each deck
    for df in df_list: 
        df.drop('deck_type', axis=1, inplace=True)
        df.sort_values('rating', ascending=False, inplace=True) 
    
   
    
    #this drops all rows with duplicate decks, NOT using this for tournaments
    ranked_decks.drop_duplicates('card_list', inplace=True)
    none_type.drop_duplicates('card_list', inplace=True)
    
    for df in df_list:
        df['date'] = pd.to_datetime(df['date'])

    #makes dfs for each year, from here it's easier to work on a month by month standpoint
    ranked_decks_2014 = ranked_decks[ranked_decks['date'].map(lambda x: x.year == 2014)]
    ranked_decks_2014['month'] = ranked_decks_2014['date'].map(lambda x: x.month)
    ranked_decks_2015 = ranked_decks[ranked_decks['date'].map(lambda x: x.year == 2015)]
    ranked_decks_2015['month'] = ranked_decks_2015['date'].map(lambda x: x.month)
    ranked_decks_2016 = ranked_decks[ranked_decks['date'].map(lambda x: x.year == 2016)]
    ranked_decks_2016['month'] = ranked_decks_2016['date'].map(lambda x: x.month)
    ranked_decks_2017 = ranked_decks[ranked_decks['date'].map(lambda x: x.year == 2017)]
    ranked_decks_2017['month'] = ranked_decks_2017['date'].map(lambda x: x.month)
    
    #The following data is for personal reference and bookkeeping

    # SET IDs
    '''
    {
        TGT : The Grand Tournament, 
        GANGS : Mean Streets of Gadgetzan, 
        CORE : Basic, 
        UNGORO : Journey to Un'Goro, 
        EXPERT1 : Classic, 
        HOF : Hall of Fame, 
        OG : Whispers of the Old Gods, 
        BRM : Blackrock Mountain, 
        GVG : Goblins versus Gnomes, 
        KARA : One Night in Karazhan, 
        LOE : League of Explorers, 
        NAXX : Naxxramus
    }
    '''

    #DECK DF MASTER COL LIST
    '''
    ['craft_cost', 'date', 'deck_archetype', 'deck_class', 'deck_format',
    'deck_id', 'deck_set', 'deck_type', 'rating', 'title', 'user', 'card_0',
    'card_1', 'card_2', 'card_3', 'card_4', 'card_5', 'card_6', 'card_7',
    'card_8', 'card_9', 'card_10', 'card_11', 'card_12', 'card_13', 'card_14', 
    'card_15', 'card_16', 'card_17', 'card_18', 'card_19', 'card_20', 'card_21', 
    'card_22', 'card_23', 'card_24', 'card_25', 'card_26', 'card_27', 'card_28', 
    'card_29']
    '''

    #DECK DF CURRENT COL LIST
    '''
    ['craft_cost', 'date', 'deck_archetype', 'deck_class', 'deck_format',
    'deck_id', 'deck_set', 'deck_type', 'rating', 'title', 'user', 'card_list']
    '''

    #JSON_DF MASTER COL LIST
    '''
    ['artist', 'attack', 'cardClass', 'classes', 'collectible',
    'collectionText', 'cost', 'dbfId', 'durability', 'elite', 'entourage',
    'faction', 'flavor', 'health', 'hideStats', 'howToEarn', 'howToEarnGolden', 'id', 'mechanics',
    'multiClassGroup', 'name', 'overload', 'playRequirements',
    'playerClass', 'race', 'rarity', 'referencedTags', 'set', 'spellDamage',
    'text', 'type'] 
    '''
    
    #JSON_DF CURRENT COL LIST
    '''
    ['attack', 'cardClass', 'cost', 'dbfId', 'durability',
    'health', 'mechanics', 'name', 'overload', 'race', 
    'rarity', 'referencedTags', 'set', 'spellDamage', 'text', 'type'] 
    '''