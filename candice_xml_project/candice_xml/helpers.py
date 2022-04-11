

from candice_xml.constants import ERROR_WEIGHTAGE,  WORDS_AVG, \
                        LEVEL_0, LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_1_MAX, LEVEL_2_MAX

from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.tokenize import RegexpTokenizer
punkt_param = PunktParameters()
punkt_param.abbrev_types = ['following', 'follows', 'refs', 'ref', 'al', 'et', 'e.g', 'vs', 'a.m', 'y.o', 'min', 'i.e', 'fig', 'no', 'eq',
     'eqs', 'usa', 'etc', 'ds', 'inc', '_num_', 'u.s', 'ltd']
sentence_tokenizer = PunktSentenceTokenizer(punkt_param)
#word_tokenizer = WordPunctTokenizer()
#word_tokenizer = RegexpTokenizer(r"""\S+[^.,:;\w\s]+\S+|\w+|[,:;.]|\S+""")
#word_tokenizer = RegexpTokenizer(r"""[^.,:;'"\s]+|[,.:;'"]""")
word_tokenizer = RegexpTokenizer(r'\w+|[^\w\s]')



def get_editing_level(error_dict, total_word_count):
    sva_score = ERROR_WEIGHTAGE.get("SVA") * error_dict.get("sva_error") / 100
    spell_score = ERROR_WEIGHTAGE.get("Spelling") * error_dict.get("spelling_error") / 100
    punctuation_score = ERROR_WEIGHTAGE.get("Punctuation") * error_dict.get("punctuation_error") / 100
    article_score = ERROR_WEIGHTAGE.get("Article") * error_dict.get("article") / 100
    preposition_score = ERROR_WEIGHTAGE.get("Prepositions") * error_dict.get("preposition") / 100
    clauses_score = ERROR_WEIGHTAGE.get("Clauses") * error_dict.get("clauses") / 100
    total_score = sva_score + spell_score + punctuation_score + article_score + preposition_score + clauses_score
    if total_word_count > 0:
        final_score = (total_score / total_word_count) * WORDS_AVG
    else:
        final_score = 0

    if total_word_count > 250:
        if final_score <= LEVEL_1_MAX:
            return LEVEL_1
        elif LEVEL_1_MAX < final_score <= LEVEL_2_MAX:
            return LEVEL_2
        else:
            return LEVEL_3
    else:
        return LEVEL_1

def create_del_tag(del_token):
    return "<?candice_delete " + del_token + " ?>"

def create_add_tag(add_token):
    return "<?candice_insert " + add_token + " ?>"

def convert_map_to_list(map_):
    
    return [i for item in map_ for i in range(item['start'], item['stop'])]


def combine_non_add_maps_single_sent(maps):
    add_list = set(convert_map_to_list(maps[0]))
    final_map = deepcopy(maps[0])
    for map_ in maps[1:]:
        for item_idx, item in enumerate(map_):
            if len(set(range(item['start'], item['stop'])).intersection(add_list)) == 0:
                final_map.append(item)
                add_list = add_list.union(set(range(item['start'], item['stop'])))
            
    return sorted(final_map, key=lambda x: x['start'])


def combine_add_maps_single_sent(maps):
    """
    --> combine add maps from multiple modules for a single sentence
    --> final output will be a list
    --> if any spans overlap, then, the map with higher priority will be considered in the final map
    :param add_maps (list of list of list): list of all add maps (sorted by priority)
    :param map_names (list): list of all map names
    :return (list): single list with add maps combined
    """
    add_list = [item['position'] for item in maps[0]]
    final_map = deepcopy(maps[0])
    for map_ in maps[1:]:
        for item_idx, item in enumerate(map_):
            if item['position'] not in add_list:
                final_map.append(item)
                add_list.append(item['position'])
            
    return sorted(final_map, key=lambda x: x['position'])



def make_add_del_map(objs):
    add_map = []
    del_map = []

    for obj in objs:
        add_map.append({'position':obj['stop'],
                        'token':obj['change']})
        del_map.append({'start':obj['start'],
                        'stop':obj['stop'],
                        'token':obj['token']})

    return add_map, del_map


def parenthesis_split(sentence,separator=" ",lparen="<",rparen=">"):
    nb_brackets=0
    sentence = sentence.strip(separator) # get rid of leading/trailing seps

    l=[0]
    for i,c in enumerate(sentence):
        if c==lparen:
            nb_brackets+=1
        elif c==rparen:
            nb_brackets-=1
        elif c==separator and nb_brackets==0:
            l.append(i)
        # handle malformed string
        # if nb_brackets<0:
        #     raise Exception("Syntax error")

    l.append(len(sentence))
    # handle missing closing parentheses
    # if nb_brackets>0:
    #     raise Exception("Syntax error")


    return([sentence[i:j].strip(separator) for i,j in zip(l,l[1:])])




def create_delete_token(del_map, range_mapping):
    del_map_range = []
    del_map_token = []
    for one_del in del_map:
        del_map_range.append((one_del['start'],one_del['stop']))
        del_map_token.append(one_del['token'])

    actual_del_token = []
    actual_del_range = []
    for idx,one_del_range in enumerate(del_map_range):
        # print(range_mapping)
        if one_del_range in range_mapping:
            actual_del_range.append(range_mapping[one_del_range])
            actual_del_token.append(del_map_token[idx])
        else:
            for key,value in range_mapping.items():
                if one_del_range[0] >= key[0] and one_del_range[0] <= key[1]:
                    difference = one_del_range[0] - key[0]
                    start = value[0] + difference
                    end = start + (one_del_range[1] - one_del_range[0])
                    actual_del_range.append((start,end))
                    actual_del_token.append(del_map_token[idx])
    return actual_del_range, actual_del_token



def create_add_token(add_map, range_mapping):
    actual_add_position = []
    actual_add_token = []
    for one_map in add_map:
        add_position = one_map["position"]
        for mapping in range_mapping:
            list_map = list(range(mapping[0],mapping[1] + 1))
            if add_position in list_map:
                add_idx = list_map.index(add_position)
                actual_add_position.append(list(range(range_mapping[mapping][0], range_mapping[mapping][1] + 1))[add_idx])
                actual_add_token.append(one_map['token'])
    return actual_add_position, actual_add_token



def update_xml(one_dict):
    add_idx = 0
    del_idx = 0
    paragraph_xml = ""
    del_flag_two_words = False
    word_tag_list = one_dict["word_tag_list"]
    for word_tag in word_tag_list:
        del_flag = False
        if word_tag["index"] not in [0,len(word_tag_list)-1]:
            
            if add_idx <= len(one_dict["add_map"]):
                for idx in range(add_idx, len(one_dict["add_map"])):
                    if one_dict["add_positions"][idx] >= word_tag["range"][0] and \
                        (one_dict["add_positions"][idx] <= word_tag["range"][1]):
                            paragraph_xml += create_add_tag(one_dict["add_tokens"][idx]) + " "
                            add_idx += 1

#             print(one_dict)
            if del_idx <= len(one_dict["del_map"]):
                for idx in range(del_idx, len(one_dict["del_map"])):
                    if one_dict["del_positions"][idx] == word_tag["range"]:
                        paragraph_xml += create_del_tag(one_dict["del_tokens"][idx]) + " "
                        del_idx += 1
                        del_flag = True
                    else:
                        if one_dict["del_positions"][idx][0] == word_tag["range"][0] \
                            and one_dict["del_positions"][idx][1] < word_tag["range"][1]:
                            paragraph_xml += create_del_tag(one_dict["del_tokens"][idx]) + " "
                            
                            remaining_start_index = len(word_tag["word"]) - \
                                                    (word_tag["range"][1] - one_dict["del_positions"][idx][1])
                            paragraph_xml += word_tag["word"][remaining_start_index:] + " "
                            del_idx += 1
                            del_flag = True
                        else:
                            if one_dict["del_positions"][idx][0] == word_tag["range"][0] \
                                and one_dict["del_positions"][idx][1] > word_tag["range"][1]:
                                del_flag_two_words = True

                            if del_flag_two_words and one_dict["del_positions"][idx][1] == word_tag["range"][1]:
                                paragraph_xml += create_del_tag(one_dict["del_tokens"][idx]) + " "
                                del_flag_two_words = False
                                del_idx += 1
                                del_flag = True
                
            if not(del_flag) and not(del_flag_two_words):
                if word_tag["tag"] == "word":
                    paragraph_xml += word_tag["word"] + " "
                elif word_tag["tag"] == "punctuation":
                    paragraph_xml = paragraph_xml[:-1] + word_tag["word"] + " "
                elif word_tag["tag"] == "opening":
                    paragraph_xml += word_tag["word"]
                elif word_tag["tag"] == "closing":
                    paragraph_xml = paragraph_xml[:-1] + word_tag["word"] + " "
    return paragraph_xml.rstrip()
