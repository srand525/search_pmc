# import psycopg2
import string
import random
import pickle
import os
import json
import lxml
import lxml.html
import itertools
from itertools import chain
from itertools import groupby
import datetime

def run_query(cursor, query):
    query_run = cursor.execute(query)
    query_return = cursor.fetchall()
    return query_return

def create_unique_id():
    character_set = string.ascii_letters
    character_set += string.digits
    unique_identifier = ''
    for _ in range(25):
        unique_identifier += random.choice(character_set)
    return unique_identifier

#serialize id
def serialize_output(unique_id,output):
    # pickle_name = ''
    pickle_name = unique_id + '.pkl'
    with open(pickle_name, 'wb') as f:
      pickle.dump(output, f)
#
# #function to save the unique identifier for the xml as a json
def update_id_json(prop_dict):
    if not os.path.isfile(os.path.join(os.getcwd(),'unique_identifiers.json')):
        with open("unique_identifiers.json", mode='w', encoding='utf-8') as f:
            json.dump([], f)
    if os.path.isfile(os.path.join(os.getcwd(),'unique_identifiers.json')):
        with open("unique_identifiers.json") as f:
            data = json.load(f)
        data.append(prop_dict)
        with open('unique_identifiers.json', 'w') as f:
            json.dump(data, f)


def id_run(run_type,input_db):
    input_db  = input_db.lower()
    json_path = "unique_identifiers.json"
    json_file = json.load(open(json_path,"r"))
    type_dict_list = [d for d in json_file if d['id_type'] == run_type and d['input_db'] == input_db]
    most_recent = max(type_dict_list,key = lambda x:x['run_date'])
    unique_id = most_recent['id']
    serialized_data_path = unique_id + '.pkl'
    with open(serialized_data_path, 'rb') as f:
        serialized_data = pickle.load(f)
    return serialized_data
#
# #count number of articles returned from a fetch
def xml_to_html(doc_list,input_db):
  pre_article_list = []
  for doc in doc_list:
    xml = lxml.html.fromstring(doc)
    if input_db == 'pmc':
        article = xml.xpath("//article")
    if input_db == 'pubmed':
        article = xml.xpath("//pubmedarticle")
    pre_article_list.append(article)
    article_list = list(itertools.chain.from_iterable(pre_article_list))
    return article_list

#clean folder
def clean_folder():
  pkl_to_delete = [f for f in os.listdir() if f.endswith('.pkl')]
  uid_to_delete = [i for i in os.listdir() if 'unique_identifier_' in i and i.endswith('.json')]
  to_delete = uid_to_delete+pkl_to_delete
  for f in to_delete:
      os.remove(f)
  # return to_delete

#
# def filter_ids(input_db,id_list_all,cur):
#     searched_tuples = [(i, input_db) for i in id_list_all]
#     cur.execute('select distinct associatedid,pullsource from public.datapull_uniqueid')
#     existing_tuples = cur.fetchall()
#     to_pull = [i[0] for i in searched_tuples if i not in existing_tuples]
#     return to_pull
