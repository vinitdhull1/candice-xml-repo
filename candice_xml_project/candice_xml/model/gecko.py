# from ..__parameters__ import word_tokenizer
# from ..__parameters__ import sentence_tokenizer
import re
import requests
import json
from candice_xml.helpers import make_add_del_map

url = "http://127.0.0.1:801/predict"

error_type = 'sva_error'

def gecko(paragraph_dict, error_dict):

    error_count = 0

    for uuid in paragraph_dict:
        sentence = paragraph_dict[uuid]['paragraph']

        data = {    "input_text":sentence,
                    "reorder":"false"}

        resp = requests.post(url,data)

        objs = json.loads(resp.text)
    
        # if objs:
        #     print(sentence)
        #     print(objs)

        add_map, del_map = make_add_del_map(objs)

        if add_map:
            error_count += len(add_map)
        
        paragraph_dict[uuid]['add_map'].append(add_map)
        paragraph_dict[uuid]['del_map'].append(del_map)

    error_dict[error_type] += error_count

    # print(sentence)
    # print(objs)
    return paragraph_dict, error_dict


