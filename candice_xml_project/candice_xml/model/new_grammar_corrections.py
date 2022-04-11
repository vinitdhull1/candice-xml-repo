#-*- coding: utf-8 -*-

from .base import Model
from ..__commons__ import LOGGER_NAME, nlp
import logging

logger = logging.getLogger(LOGGER_NAME)
from ..__paths__ import PATH_TO_RESOURCES
import re

import pandas as pd
import inflect
from ..__parameters__ import sentence_tokenizer
import hunspell
hobj = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')


inflect_engine = inflect.engine()



# en_dash_regex = r'\s*{}\s*'.format(str('\u2013'))



def read_introductory_commas_list():
    """
    --> Read words like however, in case of, etc. csv
    :return
    """
    data = pd.read_csv(PATH_TO_RESOURCES.joinpath('comma_correction.csv').as_posix())
    comma_list = data['0'].tolist()
    comma_list_corr = []
    for _ in comma_list:
        comma_list_corr.append(_.strip())
    return comma_list_corr


def read_en_dashes_list():
    """
    --> Read words where hyphen(-) needs to be replaced by en dash(–––––)
       words like north-south, left-right 
    :return
    """
    data = pd.read_csv(PATH_TO_RESOURCES.joinpath('en_dash.csv').as_posix())
    return data


def remove(text):
    new_text = ''
    for char in text:
        if char.isalpha():
            new_text += char.lower()
    return new_text


class new_grammar_corrections(Model):
    """
        1. Introductory commas
            Introductory words like However, Moreover, Furthermore, etc., create continuity from one sentence to the next.

        2. Usage of en-dash: Linking distinct items/person names 
            Use en-dashes to link distinct items or names for comparison or contrast.

        3. Usage of pluralization in compound words

    """

    def __init__(self,
                *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = 'new_grammar'
        self._type = 'punctuation'


    def introductory_commas(self,doc):

        objs = []

        comma_list = read_introductory_commas_list()
        start = False

        sentences = sentence_tokenizer.tokenize(doc.text)

            
        last_idx = 0
        for sentence in sentences:
        # last_idx = 0
        # sentence = doc.text
        # small_doc = doc
            start = False
            start_word = ""
            for comma_word in comma_list:

                if sentence.startswith(comma_word):
                    start = True
                    start_word = comma_word
            
            small_doc = nlp(sentence)
            if start:

                for word in small_doc:
                    if word.text in start_word.split(" "):
                        pass

                    else:

                        first_word_after_comma_word = word
                        #print(word.text,word.dep_)
                        if(first_word_after_comma_word.text == ','):
                            pass
                        elif(first_word_after_comma_word.dep_ in ['prep','aux']):
                            pass
                        elif(word.i + 3 < len(small_doc)):
                            comma_flag = False
                            for indx in range(1,4):
                                if small_doc[word.i + indx].text == ',':
                                    comma_flag = True
                            if comma_flag:
                                pass
                            else:
                                word_to_correct = small_doc[word.i - 1].text
                                word_to_correct_idx = small_doc[word.i - 1].idx + last_idx
                                objs.append({
                                            'token': '{}'.format(word_to_correct),
                                            'start': word_to_correct_idx,
                                            'stop': word_to_correct_idx + len(word_to_correct),
                                            'change': '{},'.format(word_to_correct)
                                        })

                        else:
                            
                            word_to_correct = small_doc[word.i - 1].text
                            word_to_correct_idx = small_doc[word.i - 1].idx + last_idx
                            objs.append({
                                        'token': '{}'.format(word_to_correct),
                                        'start': word_to_correct_idx,
                                        'stop': word_to_correct_idx + len(word_to_correct),
                                        'change': '{},'.format(word_to_correct)
                                    })

                        break



    
            last_idx += small_doc[-1].idx + len(small_doc[-1].text) + 1

        return objs

    def en_dash_changes(self,doc):

        objs = []

        data = read_en_dashes_list()

        exception_left_list = ['x','sigma']
        exception_right_list = ['ray','aldrich']

        hyphenated_list = re.findall(r'\w+[ ]*(?:-[ ]*\w+)+',doc.text)
        first_word = []
        second_word = []
        for item in hyphenated_list:
            if len(item.split('-')) == 2:
                first_word.append(item.split('-')[0].strip())
                second_word.append(item.split('-')[-1].strip())
                # print(first_word,second_word)
        # print(doc)
        
        left = False
        right = False
        propn = False
        database = False

        print(hyphenated_list)
        hyphen_idx = 0
        for indx,word in enumerate(doc):
            if hyphen_idx < len(hyphenated_list):
                if remove(word.text) == first_word[hyphen_idx].lower():
                    print(hyphen_idx)
                    print(remove(word.text), doc[indx +1].text)
                if remove(word.text) == first_word[hyphen_idx].lower() and doc[indx+1].text == '-':
            
                    if (word.pos_ == 'PROPN'):
                        #print("Left",word, word.pos_)
                        propn = True
                        left_flag = True
                        probable_word_idx = word.i
                        probable_start_idx = word.idx
                        if not(word.text[0].isupper()):
                            left_flag = False
                        # if not(hobj.spell(word.text)):
                        #     left_flag = False
                        if not(word.text.isalpha()):
                            left_flag = False
                        upper_count = 0
                        for char in word.text:
                            if char.isupper():
                                upper_count += 1
                        if len(word.text) == upper_count or (upper_count in range(2,len(word.text))):
                            left_flag = False
                        if len(word.text) <= 3:
                            left_flag = False
                        if left_flag:
                            left = True

                    if (remove(word.text) in data["left"].tolist()):
                        database = True
                        database_idx = data["left"].tolist().index(remove(word.text))
                        probable_word_idx = word.i
                        probable_start_idx = word.idx
                        left = True

                if remove(word.text) == second_word[hyphen_idx].lower():
                    if propn:
                        if (word.pos_ == 'PROPN'):
                            right_flag = True
                            #print("Right",word,word.pos_)
                            probable_end_idx = word.idx + len(word)
                            probable_right_word_idx = word.i
                            if not(word.text[0].isupper()):
                                right_flag = False
                            # if not(hobj.spell(word.text)):
                            #     right_flag = False
                            if not(word.text.isalpha()):
                                right_flag = False
                            upper_count = 0
                            for char in word.text:
                                if char.isupper():
                                    upper_count += 1
                            if len(word.text) == upper_count or (upper_count in range(2,len(word.text))):
                                right_flag = False
                            #print(doc[word.i + 1].text)
                            if doc[word.i + 1].text.lower() in ["co","company"]:
                                right_flag = False
                            if len(word.text) <= 3:
                                right_flag = False
                            if right_flag:
                                right = True
                            

                    if database:
                        if (remove(word.text) == data["right"].iloc[database_idx]):
                            probable_end_idx = word.idx + len(word)
                            probable_right_word_idx = word.i
                            right = True

                    if left and right:
                        replace = True
                        if (remove(doc[probable_word_idx].text) not in exception_left_list) \
                            and (remove(doc[probable_right_word_idx].text) not in exception_right_list):
                            objs.append({
                                        'token': '{}-{}'.format(doc[probable_word_idx].text,doc[probable_right_word_idx].text),
                                        'start': probable_start_idx,
                                        'stop': probable_end_idx,
                                        'change': '{}{}{}'.format(doc[probable_word_idx].text,str(u"\u2013"),doc[probable_right_word_idx].text)
                                    })
                        left = False
                        right = False
                        propn = False
                        database = False
                        
                    else:
                        left = False
                        right = False
                        propn = False
                        database = False
                    hyphen_idx += 1
                        
            else:
                break

        

        
        return objs


    


    def em_dash_changes(self,doc):
        objs = []
        pos_list = [ 'VERB', 'DET', 'ADV', 'PART', 'CCONJ' , 'ADP', 'ADJ', 'AUX']
        exception_words = ["who", "such", "that", "which"]

        sentences = sentence_tokenizer.tokenize(doc.text)
        last_idx = 0
        # last_idx = 0
        # sentence = doc.text
        # small_doc = doc
        en_dash = str(u"\u2013")
        for sentence in sentences:
            small_doc = nlp(sentence)
            en_dash_list = small_doc.text.split(en_dash)

            if len(en_dash_list) == 3:
                
                first = en_dash_list[0]
                second = en_dash_list[1]
                third = en_dash_list[2]

                first_doc = nlp(first)
                second_doc = nlp(second)
                third_doc = nlp(third)
                
                first_idx = -1
                second_idx = -1

                
                en_dash_1_first_word = first_doc[-1]

                first_second_space = ""
                for word in second_doc:
                    if word.pos_ == "SPACE":
                        first_second_space = word
                    else:
                        first_second_word = word
                        break

                
                en_dash_2_first_word = second_doc[-1]

                second_second_space = ""
                for word in third_doc:
                    # print(word.pos_)
                    if word.pos_ == "SPACE":
                        second_second_space = word
                    else:
                        first_third_word = word
                        break

                # print(first_third_word.text, first_third_word.pos_)
                # print(first_second_word.text, first_second_word.pos_)
                if first_second_word.pos_ in pos_list or first_second_word.text.lower().strip() in exception_words:
                    
                    if first_third_word.pos_ in pos_list or first_third_word.text.lower().strip() in exception_words:
                        

                        for word in small_doc:
                            if word.text == en_dash:
                                if first_idx == -1:
                                    first_idx = word.idx
                                else:
                                    second_idx = word.idx
                
                if first_idx != -1 and second_idx != -1:
                    
                    if first_second_space:
                        objs.append({
                                    'token': '{}{}{}'.format(en_dash_1_first_word.text,en_dash,first_second_space.text),
                                    'start': en_dash_1_first_word.idx + last_idx,
                                    'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 2 +
                                            len(first_second_space) + last_idx ,
                                    'change': '{}{}'.format(en_dash_1_first_word.text,str(u"\u2014"))
                                })
                    else:    
                        objs.append({
                                        'token': '{}{}{}'.format(en_dash_1_first_word.text,en_dash,first_second_word.text),
                                        'start': en_dash_1_first_word.idx  + last_idx,
                                        'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 1 +
                                                len(first_second_word.text) + last_idx,
                                        'change': '{}{}{}'.format(en_dash_1_first_word.text,str(u"\u2014"),first_second_word.text)
                                    })
                    if second_second_space:
                        objs.append({
                                    'token': '{}{}{}'.format(en_dash_2_first_word.text,en_dash,second_second_space.text),
                                    'start': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 
                                            en_dash_2_first_word.idx  + last_idx + 2,
                                    'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 1 + 
                                            en_dash_2_first_word.idx + len(en_dash_2_first_word.text) + 3 + 
                                            len(second_second_space) + last_idx ,
                                    'change': '{}{}'.format(en_dash_2_first_word.text,str(u"\u2014"))
                                })
                    else:
                        objs.append({
                                        'token': '{}{}{}'.format(en_dash_2_first_word.text,en_dash,first_third_word.text),
                                        'start': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 
                                                en_dash_2_first_word.idx + last_idx + 2,
                                        'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 1 + 
                                                en_dash_2_first_word.idx + len(en_dash_2_first_word.text) + 2 +
                                                + len(first_third_word.text) + last_idx ,
                                        'change': '{}{}{}'.format(en_dash_2_first_word.text,str(u"\u2014"),first_third_word.text)
                                    })

            last_idx += small_doc[-1].idx + len(small_doc[-1].text) + 1

        # sentences = sentence_tokenizer.tokenize(doc.text)
        last_idx = 0
        for sentence in sentences:
            small_doc = nlp(sentence)
        # last_idx = 0
        # sentence = doc.text
        # small_doc = doc
            hyphen_dash_list = re.compile("\s\s-\s\s").split(small_doc.text)
            # print(hyphen_dash_list)
            if len(hyphen_dash_list) == 3:

                first = hyphen_dash_list[0]
                second = hyphen_dash_list[1]
                third = hyphen_dash_list[2]

                first_doc = nlp(first)
                second_doc = nlp(second)
                third_doc = nlp(third)

                first_idx = -1
                second_idx = -1


                en_dash_1_first_word = first_doc[-1]

                first_second_space = ""
                for word in second_doc:
                    if word.pos_ == "SPACE":
                        first_second_space = word
                    else:
                        first_second_word = word
                        break


                en_dash_2_first_word = second_doc[-1]

                second_second_space = ""
                for word in third_doc:
                    # print(word.pos_)
                    if word.pos_ == "SPACE":
                        second_second_space = word
                    else:
                        first_third_word = word
                        break

                # print(first_third_word.text, first_third_word.pos_)
                # print(first_second_word.text, first_second_word.pos_)
                if first_second_word.pos_ in pos_list or first_second_word.text.lower().strip() in exception_words:

                    if first_third_word.pos_ in pos_list or first_third_word.text.lower().strip() in exception_words:


                        for word in small_doc:
                            if word.text == en_dash or word.text == '-':
                                if first_idx == -1:
                                    first_idx = word.idx
                                else:
                                    second_idx = word.idx

                if first_idx != -1 and second_idx != -1:

                    if first_second_space:
                        objs.append({
                                    'token': '{} - {}'.format(en_dash_1_first_word.text,first_second_space.text),
                                    'start': en_dash_1_first_word.idx + last_idx,
                                    'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 4 +
                                            len(first_second_space) + last_idx ,
                                    'change': '{}{}'.format(en_dash_1_first_word.text,str(u"\u2014"))
                                })
                    else:
                        objs.append({
                                        'token': '{} - {}'.format(en_dash_1_first_word.text,first_second_word.text),
                                        'start': en_dash_1_first_word.idx  + last_idx,
                                        'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 3 +
                                                len(first_second_word.text) + last_idx,
                                        'change': '{}{}{}'.format(en_dash_1_first_word.text,str(u"\u2014"),first_second_word.text)
                                    })
                    if second_second_space:
                        objs.append({
                                    'token': '{} - {}'.format(en_dash_2_first_word.text,second_second_space.text),
                                    'start': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 
                                            en_dash_2_first_word.idx  + last_idx + 3,
                                    'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 4 + 
                                            en_dash_2_first_word.idx + len(en_dash_2_first_word.text) + 3 + 
                                            len(second_second_space) + last_idx ,
                                    'change': '{}{}'.format(en_dash_2_first_word.text,str(u"\u2014"))
                                })
                    else:
                        objs.append({
                                        'token': '{} - {}'.format(en_dash_2_first_word.text,first_third_word.text),
                                        'start': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 
                                                en_dash_2_first_word.idx + last_idx + 3,
                                        'stop': en_dash_1_first_word.idx + len(en_dash_1_first_word.text) + 4 + 
                                                en_dash_2_first_word.idx + len(en_dash_2_first_word.text) + 2 +
                                                + len(first_third_word.text) + last_idx ,
                                        'change': '{}{}{}'.format(en_dash_2_first_word.text,str(u"\u2014"),first_third_word.text)
                                    })

            last_idx += small_doc[-1].idx + len(small_doc[-1].text) + 1

        return objs


    def transform(self, add_all, del_all, com_all):
        # self._sent_list = self.bracket_content_modifier(self._name, self._sent_list)
        add_, del_, com_ = [], [], []
        docs = self._get_spacy_docs()

        for idx, doc in enumerate(docs):
            obj = self.introductory_commas(doc)
            # obj = self.en_dash_changes(doc)
            obj.extend(self.en_dash_changes(doc))
            # obj.extend(self.compound_words_pluralization(doc))
            obj.extend(self.em_dash_changes(doc))
            _temp_add, _temp_del, _temp_com = [], [], []
            for item in obj:
                if item['change'] != item['token']:
                    start, stop = self._map_span((item['start'], item['stop']), self._span_maps[idx])
                    add_map = self._return_add_map(pos=stop, token=item['change'])
                    del_map = self._return_del_map(start=start, stop=stop, token=self._sent_list[idx][start:stop])
                    if self.check_existent_map(add_map, add_all[idx]) and self.check_existent_map(del_map, del_all[idx]):
                        continue
                    self._num_errors += 1
                    _temp_del.append(del_map)
                    _temp_add.append(add_map)

            add_.append(_temp_add)
            del_.append(_temp_del)
            com_.append([])

        return add_, del_, com_
