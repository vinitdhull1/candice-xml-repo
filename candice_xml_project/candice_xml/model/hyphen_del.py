
import spacy
import pandas as pd
from candice_xml.helpers import make_add_del_map


nlp = spacy.load('en_core_web_sm')

def read_excluded_hyphen_list():
    """
    --> Read prefix_list csv
    :return
    """
    df = pd.read_csv('candice_xml/resources/words_with_hyphen.csv')
    words = df['words'].apply(lambda x: x.lower()).values.tolist()
    return words

def read_prefix_list():
    """
    --> Read prefix_list csv
    :return
    """
    df = pd.read_csv('candice_xml/resources/prefix_list.csv')
    prefix_list = df['prefix'].apply(lambda x: x.lower()).values.tolist()
    return prefix_list

def read_hyphen_restore_list():
    """
    --> Read prefix_list csv
    :return
    """
    df = pd.read_csv('candice_xml/resources/hyphen_restore.csv')
    words = df['words'].apply(lambda x: x.lower()).values.tolist()
    return words

prefix_list = read_prefix_list()
hyphen_restore =  read_hyphen_restore_list()

list_non_noun = ["in","on","of","for","to","up","to","onto","up","down","below", 
        ",",".",";",":","a","an","the","and","or","but","yet","which","that","while","whereas",
        "who","whom","where","how","why","what","am","has","have","had","is"]
del_hyphen_words = {"a-priori-solution":"a priori solution","a-posteriori-solution":"a posteriori solution",
        "per-mille-basis":"per mille basis","in-situ-technique":"in situ technique","bona-fide-offer":"bona fide offer"}

error_type = 'punctuation_error'

def del_hyphen(paragraph_dict,us_uk_type,error_dict):


    error_count = 0
    for uuid in paragraph_dict:
        sentence = paragraph_dict[uuid]['paragraph']

        doc = nlp(sentence)

        # us_uk_type = "us"

        excluded_hyphen = read_excluded_hyphen_list()
        objs = []

        for idx, word in enumerate(doc):
            try:
                if "{}-{}".format(word.text.lower(), doc[idx+1].text.lower()) in hyphen_restore:
                    if doc[idx + 2].pos_ in ["PROPN", "NOUN"] or  doc[idx + 2].text not in list_non_noun:
                        objs.append({
                                'token': "{} {}".format(word.text, doc[idx+1].text),
                                'start': word.idx,
                                'stop' :  doc[idx+1].idx + len( doc[idx+1].text),
                                'change': "{}-{}".format(word.text, doc[idx+1].text)
                            })
            except:
                pass
            
            try:
                if "{}-{}-{}".format(word.text.lower(), doc[idx+1].text.lower(),doc[idx+2].text.lower()) in hyphen_restore:
                    if doc[idx + 3].pos_ in ["PROPN", "NOUN"] or  doc[idx + 3].text not in list_non_noun:
                        objs.append({
                                'token': "{} {} {}".format(word.text, doc[idx+1].text,doc[idx+2].text),
                                'start': word.idx,
                                'stop' :  doc[idx+2].idx + len( doc[idx+2].text),
                                'change': "{}-{}-{}".format(word.text, doc[idx+1].text, doc[idx+2].text)
                            })
            except:
                pass


                            
            if word.text == "-":
                if doc[idx-1].pos_ == 'NUM':
                    try:
                        if doc[idx+1].text.lower() in ['half', 'third', 'thirds'] or  doc[idx+1].text[-2:].lower() == "th" or  doc[idx+1].text[-3:].lower() == "ths":
                            objs.append({
                                'token' : "{}{}{}".format(doc[idx-1].text, word.text, doc[idx+1].text),
                                'start' : doc[idx-1].idx,
                                'stop': doc[idx + 1].idx + len(doc[idx + 1].text),
                                'change': '{} {}'.format(doc[idx-1].text,  doc[idx+1].text)
                                })
                    except:
                        pass
                    
                try:
                    if "{}{}{}".format(doc[idx-1].text.lower(), word.text, doc[idx+1].text.lower()) in hyphen_restore:
                        if doc[idx + 2].pos_ in ["PROPN", "NOUN"]:
                            continue
                        elif doc[idx + 2].text in list_non_noun:
                            objs.append({
                                'token': '{}{}{}'.format(doc[idx-1].text, word.text, doc[idx+1].text),
                                'start': doc[idx-1].idx,
                                'stop': doc[idx + 1].idx + len(doc[idx + 1].text),
                                'change': '{} {}'.format(doc[idx-1].text,  doc[idx+1].text)
                            })
                except:
                    pass
                try:
                    if "{}{}{}{}{}".format(doc[idx-1].text.lower(), word.text, doc[idx+1].text.lower(),doc[idx+2].text.lower(),doc[idx+3].text.lower()) in hyphen_restore:
                        if doc[idx + 4].pos_ in ["PROPN", "NOUN"]:
                            continue
                        elif doc[idx + 4].text in list_non_noun:
                            objs.append({
                                'token':  "{}{}{}{}{}".format(doc[idx-1].text, word.text, doc[idx+1].text,doc[idx+2].text,doc[idx+3].text),
                                'start': doc[idx-1].idx,
                                'stop': doc[idx + 3].idx + len(doc[idx + 3].text),
                                'change': '{} {} {}'.format(doc[idx-1].text,  doc[idx+1].text, doc[idx + 3].text)
                            })
                except:
                    pass
                
                try:
                    del_word = "{}{}{}{}{}".format(doc[idx-1].text.lower(), word.text, doc[idx+1].text.lower(),doc[idx+2].text,doc[idx+3].text.lower())
                    if del_word in del_hyphen_words:
                         objs.append({
                                'token': del_word,
                                'start': doc[idx-1].idx,
                                'stop': doc[idx + 3].idx + len(doc[idx + 3].text),
                                'change': del_hyphen_words[del_word]                        
                        })



                except:
                    pass

            
            if word.text[-2:].lower() == "ly" and word.text.lower() not in ['early', 'poly']:
                try:
                    if doc[idx+1].text == "-":
                        objs.append({
                            'token': "{}-{}".format(word.text,  doc[idx+2].text),
                            'start': word.idx,
                            'stop': doc[idx+2].idx+ len(doc[idx+2].text),
                            'change': "{} {}".format(word.text,  doc[idx+2].text)
                            })
                except:
                    pass


            if word.text.lower() in prefix_list and (not word.text.isupper()) and (word.text not in ['Co']):
                first_word = word.text

                if idx + 2 < len(doc):
                    if us_uk_type == 'us':
                        if doc[idx + 1].text == '-':
                            if "{}{}{}".format(doc[idx],doc[idx+1], doc[idx+2]).lower() in excluded_hyphen:
                                continue
                            if doc[idx+2].text in ['and', 'or', '/', ',']:
                                continue



                            if doc[idx + 2].text[0] == first_word[-1]:
                                continue
                            #
                            # if doc[idx + 2].pos_ == "PROPN":
                            #     continue

                            if doc[idx + 2].text[0].isupper():
                                continue

                            if doc[idx + 2].text[0].isnumeric():
                                continue

                            try:
                                if doc[idx+3].text == '-':
                                    continue
                            except IndexError:
                                logger.warning("Index Error")


                            if doc[idx].text == doc[idx+2].text[0:len(doc[idx])]:
                                continue


                            objs.append({
                                'token': '{}-{}'.format(first_word, doc[idx + 2].text),
                                'start': word.idx,
                                'stop': doc[idx + 2].idx + len(doc[idx + 2].text),
                                'change': '{}{}'.format(first_word, doc[idx + 2].text)
                            })
                        if doc[idx + 1].text in ['and', 'or', '/', ',']:
                            objs.append({
                                'token': '{}'.format(first_word),
                                'start': word.idx,
                                'stop': doc[idx].idx + len(doc[idx].text),
                                'change': '{}-'.format(first_word)
                            })

        add_map, del_map = make_add_del_map(objs)

        if add_map:
            error_count += len(add_map)

        paragraph_dict[uuid]['add_map'].append(add_map)
        paragraph_dict[uuid]['del_map'].append(del_map)

    error_dict[error_type] += error_count


    return paragraph_dict, error_dict

