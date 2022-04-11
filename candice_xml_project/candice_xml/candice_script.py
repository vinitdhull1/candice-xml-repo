from string import punctuation
from bs4 import BeautifulSoup,element
import uuid
from collections import OrderedDict
from copy import deepcopy
import re
from candice_xml.helpers import *

# file_path = "/home/aptara/Music/test_files/xml_files/TRSL1599/TRSL1599-ms.xml"

def read_data_from_xml(file_path):
    """
    Reads data from manuscript.xml in a xml file, parses through BeautifulSoup and returns the soup object.
    """
    try:
        o = open(file_path, 'r')
        xml_content = o.read()
        soup = BeautifulSoup(xml_content, 'xml')
        return soup
    except KeyError:
        pass


def write_data_into_xml(soup,new_file_path):
        """
        Writes the updated soup object into filename.xml replacing the original content.
        """
        with open("{}".format(new_file_path), "w", encoding='utf-8') as file:
            file.write(str(soup))    


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



def make_words_from_para(para):
    para = re.sub(r'>(.)',r'> \1',str(para))
    para = re.sub(r'(.)<',r'\1 <',str(para))
    para = re.sub(r' +',r' ',para)
    words_list = parenthesis_split(para)
    return words_list

def create_tags_list(words_list):
    tags = []

    for word in words_list:
        if re.match('^</.',word):
            tags.append('closing')
        elif re.match('<.',word):
            tags.append('opening')
        else:
            if word.strip() in punctuation:
                tags.append('punctuation')
            else:
                tags.append('word')
    return tags



def create_word_tag_list(words_list):
    tags = create_tags_list(words_list)

    word_tag_list = []
    idx = 0
    range_idx = 0
    prev_tag = tags[idx]
    for tag,word in zip(tags,words_list):
        if idx-1 > 0:
            prev_tag = tags[idx-1]
        if prev_tag != 'opening' and tag not in ['closing','punctuation']:
            range_idx = range_idx + 1 

        word_tag_list.append({"index":idx,"word":word,"tag":tag,
                        "range":(range_idx, range_idx + len(word))})
        idx += 1
        range_idx += len(word)  

    return word_tag_list

def create_paragraph_and_range_map(word_tag_list):
    paragraph = ""

    range_idx = 0
    range_mapping = {}

    for idx,word_tag in enumerate(word_tag_list):
        if word_tag["tag"] == "word":
            paragraph += word_tag["word"] + " "
            range_mapping[(range_idx,range_idx + len(word_tag["word"]))] =  word_tag['range']
            range_idx = range_idx + len(word_tag["word"]) + 1
        elif word_tag["tag"] == "punctuation":
            paragraph = paragraph[:-1] + word_tag["word"] + " "
            range_mapping[(range_idx-1,range_idx + len(word_tag["word"]) - 1)] =  word_tag['range']
            range_idx += len(word_tag["word"])

    paragraph = paragraph.rstrip()
    
    return paragraph,range_mapping


from candice_xml.model.spelling_us_uk import find_majority


from candice_xml.model.gecko import gecko
from candice_xml.model.hyphen_del import del_hyphen
from candice_xml.model.spelling_us_uk import change_sentence_to_majority

def generate_candice_xml(xml_file):
    # soup = read_data_from_xml(file_path)
    soup = BeautifulSoup(xml_file, 'xml')



    style_tags = ["ce:para","ce:simple-para","p"]

    paras_dict = {}
    error_dict = {"sva_error":0,"punctuation_error":0,"article":0,"spelling_error":0,\
                    "preposition":0,"clauses":0}

    total_word_count = 0

    for style_tag in style_tags:
        all_paras = soup.find_all(style_tag)
        for para in all_paras:
            paragraph_uuid = str(uuid.uuid4())
            para['uuid'] = paragraph_uuid
            paras_dict[paragraph_uuid] = {"original_xml":str(para),"tag":para.name, "attributes":para.attrs}

    for para_uuid in paras_dict:
        original_xml = paras_dict[para_uuid]["original_xml"]
        original_xml = re.sub(r'>(.)',r'> \1',str(original_xml))
        original_xml = re.sub(r'(.)<',r'\1 <',str(original_xml))
        original_xml = re.sub(' +',' ',original_xml)

        words_list = parenthesis_split(original_xml)
        word_tag_list = create_word_tag_list(words_list)

        paras_dict[para_uuid]["word_tag_list"] = word_tag_list
        
        paragraph, range_mapping = create_paragraph_and_range_map(word_tag_list)
        
        paras_dict[para_uuid]["paragraph"] = paragraph
        paras_dict[para_uuid]["range_map"] = range_mapping
        paras_dict[para_uuid]["add_map"] = []
        paras_dict[para_uuid]["del_map"] = []

        total_word_count = total_word_count + len(paragraph.split())


    us_uk_type = find_majority(paras_dict)


    paras_dict,error_dict = change_sentence_to_majority(paras_dict,error_dict)
    paras_dict,error_dict = gecko(paras_dict,error_dict)
    paras_dict,error_dict = del_hyphen(paras_dict,us_uk_type,error_dict)

    # models = ["gecko","hyphen_del"]

    for para_uuid in paras_dict:
        

        paras_dict[para_uuid]["add_map"] = combine_add_maps_single_sent(paras_dict[para_uuid]["add_map"])
        paras_dict[para_uuid]["del_map"] = combine_non_add_maps_single_sent(paras_dict[para_uuid]["del_map"])

        if paras_dict[para_uuid]["add_map"] or paras_dict[para_uuid]["del_map"]:
            paras_dict[para_uuid]["change"] = True
        else:
            paras_dict[para_uuid]["change"] = False

        paras_dict[para_uuid]["add_positions"],paras_dict[para_uuid]["add_tokens"] = create_add_token(paras_dict[para_uuid]["add_map"],paras_dict[para_uuid]['range_map'])

        paras_dict[para_uuid]["del_positions"],paras_dict[para_uuid]["del_tokens"] = create_delete_token(paras_dict[para_uuid]["del_map"],paras_dict[para_uuid]['range_map'])

        paras_dict[para_uuid]["updated_xml"] = update_xml(paras_dict[para_uuid])


    for para_uuid in paras_dict:
        if paras_dict[para_uuid]["change"]:
            if paras_dict[para_uuid]["tag"] == "p":
                para_tag =  paras_dict[para_uuid]["tag"]

                soup_update = BeautifulSoup("<" + paras_dict[para_uuid]["tag"] + ">" + \
                                          paras_dict[para_uuid]["updated_xml"] + \
                                          "</" + paras_dict[para_uuid]["tag"] + ">",'lxml')
            else:
                para_tag = "ce:" + paras_dict[para_uuid]["tag"]
                
                soup_update = BeautifulSoup("<ce:" + paras_dict[para_uuid]["tag"] + ">" + \
                                              paras_dict[para_uuid]["updated_xml"] + \
                                              "</ce:" + paras_dict[para_uuid]["tag"] + ">",'lxml')
            # print(soup.find(para_tag,{"uuid":uuid}))
            
            soup_update = soup_update.find(para_tag)

            for attr in paras_dict[para_uuid]["attributes"]:
                if attr != 'uuid':
                    soup_update[attr] = paras_dict[para_uuid]["attributes"][attr]

            # print(soup_update)
            if(soup.find(para_tag,{"uuid":para_uuid})):
                soup.find(para_tag,{"uuid":para_uuid}).replaceWith(soup_update)
            # print(paras_dict[para_uuid]["updated_xml"])
            
        else:
            if paras_dict[para_uuid]["tag"] == "p":
                para_tag =  paras_dict[para_uuid]["tag"]
            else:
                para_tag = "ce:" + paras_dict[para_uuid]["tag"]
            
            soup.find(para_tag,{"uuid":para_uuid}).attrs.pop('uuid',None)

    candice_xml_file = str(soup)
    candice_xml_file = candice_xml_file.replace("xmlns:=","xmlns=")





    #### HTML FILE ####

    # error_dict = {"sva":10,"punctuation":23,"grammar":3}

    editing_level = get_editing_level(error_dict,total_word_count)

    table_html_string = ""

    for key,value in error_dict.items():
        table_html_string = table_html_string + "<tr>\n <td>{}</td>\n <td>{}</td>\n</tr>\n".format(key,value)

    candice_html_report =   """ <html>
                                    <head>
                                        <title>Candice XML Report </title>
                                    </head>
                                    <body>
                                        <table>
                                          <tr>
                                            <th>Editing Level</th>
                                            <th>Level {}</th>
                                          </tr>
                            """.format(editing_level)
                            
    candice_html_report += table_html_string
                            
    candice_html_report += """
                                <tr>
                                    <td>Total Words</td>
                                    <td>{}</td>
                                </tr>
                            """.format(total_word_count)
                            
    candice_html_report += """
                                        </table>
                                    </body>
                                </html>
                            """


    # print(candice_html_report)
    return candice_xml_file,candice_html_report


# soup = read_data_from_xml(file_path)
# generate_candice_xml(str(soup))


# write_data_into_xml(soup)
