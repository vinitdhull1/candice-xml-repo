
import pandas as pd
from candice_xml.helpers import word_tokenizer, make_add_del_map


def read_spell_csv():
    """
    --> Read US-UK csv
    --> Creates two dicts : us_to_uk and uk_to_us
    :return (dict , dict): ( us_to_uk, uk_to_us)
    """
    df = pd.read_csv('candice_xml/resources/final_spell.csv')
    df['US'] = df['US'].apply(lambda x: x.lower().strip())
    df['UK'] = df['UK'].apply(lambda x: x.lower().strip())

    us_to_uk = dict(zip(df['US'].tolist(), df['UK'].tolist()))
    uk_to_us = dict(zip(df['UK'].tolist(), df['US'].tolist()))

    return us_to_uk, uk_to_us


def read_spell_csv_mollus():
    """
    --> Read US-UK csv
    --> Creates two dicts : us_to_uk and uk_to_us
    :return (dict , dict): ( us_to_uk, uk_to_us)
    """
    df = pd.read_csv('candice_xml/resources/final_spell_mollus.csv')
    df['US'] = df['US'].apply(lambda x: x.lower().strip())
    df['UK'] = df['UK'].apply(lambda x: x.lower().strip())

    us_to_uk = dict(zip(df['US'].tolist(), df['UK'].tolist()))
    uk_to_us = dict(zip(df['UK'].tolist(), df['US'].tolist()))

    return us_to_uk, uk_to_us

def get_us_list():
    df = pd.read_csv('candice_xml/resources/us_spell_journals.csv')
    us_list = df['Type'].values.tolist()

    return us_list


us_to_uk, uk_to_us = read_spell_csv()
us_to_uk_mollus, uk_to_us_mollus = read_spell_csv_mollus()
us_journal_names = get_us_list()


   
error_type = 'spelling_error'

def find_count(paragraph_dict):

    us_count = 0
    uk_count = 0
    us_words, uk_words = [], []

    for uuid in paragraph_dict:
        sentence = paragraph_dict[uuid]['paragraph']

        tokens = word_tokenizer.tokenize(sentence)
        for token in tokens:
            if token.lower().strip() in us_to_uk.keys():
                us_words.append(token)
                us_count += 1
            if token.lower().strip() in uk_to_us.keys():
                uk_words.append(token)
                uk_count += 1
    return us_count, uk_count, us_words, uk_words

def find_majority(paragraph_dict):
    """
    --> Decides the majority on the basis of count
    --> In case majority cannot be decided, chose US type (verify from ashok) (acc. to SME, check punctuation, serial comma)
    :return (str): "us" if majority is US, "uk" if majority is UK, "both" if cannot decide majority
    """
    ## journal name exception
    
    # if self.get_journal_code() in us_journal_names:
    #     # logger.info('the journal uses US spell type')
    #     return 'us'

    us_count, uk_count, us_words, uk_words = find_count(paragraph_dict)

    # logger.info('US COUNT = {}'.format(us_count))

    # logger.info('UK COUNT = {}'.format(uk_count))

    if us_count >= uk_count:
        return 'us'
    else:
        return 'uk'


def change_sentence_to_majority(paragraph_dict, error_dict):
    """
    --> Takes sentence as an input
    --> Changes non majority tokens to majority tokens
    --> Returns spans of the changed tokens
    :param sentence (str): input sentence
    :param majority (str): "US" or "UK"
    :return (list): each item will be a dict specifying the position of the token to be changed
                --> e.g. [{'start':int, 'stop':int, 'new_token':str, 'token' : str}, ...]
    """
    

    error_count = 0

    majority = find_majority(paragraph_dict)

    for uuid in paragraph_dict:
        sentence = paragraph_dict[uuid]['paragraph']

        spans = list(word_tokenizer.span_tokenize(sentence))
        tokens = word_tokenizer.tokenize(sentence)
        obj = []
        # if general_code == "MOLLUS":
        #     final_dict = uk_to_us_mollus if majority == 'us' else us_to_uk_mollus if majority == 'uk' else None
        # else:
        final_dict = uk_to_us if majority == 'us' else us_to_uk if majority == 'uk' else None
        
        if not final_dict:
            return []
        for (start, stop), token in zip(spans, tokens):
            if token in final_dict.keys() and (token not in ['practice','practise']):
                obj.append({'start': start, 'stop': stop, 'change': final_dict[token], 'token': token})
        
        add_map, del_map = make_add_del_map(obj)
    
        if add_map:
            error_count += len(add_map)

        paragraph_dict[uuid]['add_map'].append(add_map)
        paragraph_dict[uuid]['del_map'].append(del_map)
    

    # print(error_type,error_count)
    error_dict[error_type] += error_count

    return paragraph_dict, error_dict

