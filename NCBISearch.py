from Bio import Entrez
import pandas as pd
from pandas import DataFrame
import itertools
from itertools import chain, groupby
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
import pickle
import types
import lxml.html
from operator import itemgetter
import json
import random
import string
import helper
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class ncbi_search:
    def __init__(self,input_term,input_db,email_id):
        self.input_term = input_term
#         self.input_db = input_db
        self.input_db = input_db.lower()
        self.email_id = email_id



    #Find # of records within search parameters
    def pub_count(self):
        Entrez.email = self.email_id
        counthandle = Entrez.egquery(term = self.input_term)
        record = Entrez.read(counthandle)
        for row in record["eGQueryResult"]:
            if row['DbName'] == self.input_db:
                record_count = row['Count']
        counthandle.close()
        record_count = int(record_count)
        return record_count

    #function for retrieving and storing ids
    def pub_search(self, record_count, sort = 'relevance', chunksize = 500, sleeptime = 5):
        Entrez.email = self.email_id
        # record_count = 10
        # record_count = int(self.pub_count())
        submitinterv = math.ceil(int(record_count)/chunksize)
        id_list = []
        retstartc = 0
        if record_count < chunksize:
            ret_max = record_count
        elif record_count >= chunksize:
            ret_max = chunksize
        for i in range(submitinterv):
            handle = Entrez.esearch(db=self.input_db,
                                sort='relevance',
                                retstart= retstartc,
                                retmax=ret_max,
                                retmode='xml',
                                term=self.input_term)
            idresults = Entrez.read(handle)
            id_list += idresults['IdList']
            time.sleep(sleeptime)
            retstartc += chunksize
            handle.close()
        return id_list

    def search_properties(self,record_count):
        unique_id = helper.create_unique_id()
        now = datetime.datetime.now()
        time_stamp = now.strftime("%Y-%m-%d %H:%M")
        n_records_searched = record_count
        prop_dict = {'id':unique_id,'id_type':'search'
        ,'input_term':self.input_term,'input_db':self.input_db,'record_count':n_records_searched
        ,'run_date':time_stamp}
        return prop_dict
