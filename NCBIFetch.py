from Bio import Entrez
import pandas as pd
from pandas import DataFrame
import itertools
from itertools import chain
from itertools import groupby
import codecs
import io
import sys
import encodings
import time
import os
import math
from IPython.display import HTML
from datetime import date
import datetime
import lxml
import lxml.html
import pickle
import types
from operator import itemgetter
import json
import helper
import random
import string
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class ncbi_fetch:
    def __init__(self,input_db,email_id):
        self.input_db = input_db.lower()
        self.email_id = email_id

    #function for fetching xmls for given ids
    def pub_fetch(self,id_list_fetch):
        Entrez.email = self.email_id
        id_list_filt = id_list_fetch[0:3] #comment
        ids = ','.join(id_list_filt) #comment
        # ids = ','.join(id_list_fetch) #uncomment
        id_list_fetch = id_list_filt #comment
        submitinterv = math.ceil(len(id_list_fetch)/10000)
        sleeptime = 5
        restartc = 0
        doc_list = []

        for i in range(submitinterv):
            fetchHandle = Entrez.efetch(db=self.input_db,
                                      retmode='xml',
                                      id=id_list_fetch,
                                      retstart = restartc,
                                      retmax=10000)
            fetchRead = io.TextIOWrapper(fetchHandle.detach(), encoding='utf-8')
            doc = fetchRead.read()
            doc_list.append(doc)
            time.sleep(sleeptime)
            restartc += 10000
        doc_full = doc_list
        # article_list = helper.xml_to_html(doc_full,self.input_db)
        return doc_full

    def search_properties(self):
        unique_id = helper.create_unique_id()
        now = datetime.datetime.now()
        time_stamp = now.strftime("%Y-%m-%d %H:%M")
        id_list = helper.id_run('search',self.input_db)
        run_fetch = self.pub_fetch(id_list)
        article_list = helper.xml_to_html(run_fetch,self.input_db)
        n_records_fetched = len(article_list)
        prop_dict = {'id':unique_id,'id_type':'fetch'
        ,'input_db':self.input_db,'record_count':n_records_fetched
        ,'run_date':time_stamp}
        return prop_dict
