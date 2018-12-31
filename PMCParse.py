import pickle
import pandas as pd
import lxml.html
from lxml.etree import tostring
import re
import itertools
import io
import json
import helper
from lxml import etree
import string
import random
import datetime


#Parse pmc ids
def pmc_ids(article):
    id_types_list = [elem for elem in article.xpath(".//front/article-meta/article-id[@pub-id-type = 'pmid' or @pub-id-type = 'pmc' or @pub-id-type = 'doi']")]
    id_dict = {}
    for id_type in id_types_list:
        id_type_name = id_type.values()[0]
        id_type_val = id_type.text_content()
        id_dict[id_type_name] = id_type_val
    return id_dict

#Parse pmc titles
def pmc_titles(article):
    article_title = article.xpath(".//front/article-meta/title-group/article-title")[0].text_content()
    return article_title

#Parse pmc dates
def pmc_dates(article):
    date_types_all = [elem for elem in article.xpath(".//front/article-meta/pub-date[@pub-type = 'epub' or @pub-type = 'ppub']")]
    big_list = []
    for date_type in date_types_all:
        child_list = [child for child in date_type.iterchildren('year','month','day')]
        child_tup = (child_list,len(child_list))
        big_list.append(child_tup)

    check_list = [b[1] for b in big_list]
    date_val_list = big_list[check_list.index(max(check_list))][0]
    date_dict = {d.tag:d.text_content() for d in date_val_list}

    if len(date_dict.values()) == 3:
        date_full = '{0}/{1}/{2}'.format(date_dict['month'],date_dict['day'],date_dict['year'])
    elif len(date_dict.values()) < 3:
        date_full = None

    return [date_dict, date_full]


#Parse pmc keywords
def pmc_kwd(article):
    kwd_dict_list = [{'descriptorname':elem.text_content()} for elem in article.xpath('.//front/article-meta/kwd-group/kwd')]
    return kwd_dict_list


#Parse pmc pubtypes
def pmc_pub_type(article):
    pub_type_list_all = [elem.text_content() for elem in article.xpath('./front/article-meta/article-categories/subj-group/subject')]
    pub_type_set = set(pub_type_list_all)
    pub_type_list = [el for el in pub_type_set if not el.isdigit()]
    return pub_type_list


#Parse pmc abstract text
#Parse pmc abstract text
def pmc_abstract(article):
    abs_list = [elem for elem in article.xpath('.//front/article-meta/abstract/sec')]
    if abs_list == []:
        abs_list = [elem for elem in article.xpath('.//front/article-meta/abstract')]
    abstract_list = []
    for a in abs_list:
        abs_dict = {}
        try:
            abs_dict['label'] = a.xpath('.//title')[0].text_content()
        except:
            abs_dict['label'] = None
        abs_dict['text'] = a.xpath('.//p')[0].text_content()
        abstract_list.append(abs_dict)
    return abstract_list


#Parse pmc journal info
def pmc_journal(article):
    journal_list = [elem for elem in article.xpath(".//front/journal-meta/journal-id[@journal-id-type = 'nlm-ta' or @journal-id-type = 'iso-abbrev']|.//front/journal-meta/journal-title-group/journal-title|.//front/journal-meta/journal-title")]
    journal_dict = {j.tag:j.text_content() for j in journal_list}
    return journal_dict


#Parse author info
def pmc_author(article):
    auth_list = [elem for elem in article.xpath(".//front/article-meta/contrib-group/contrib")]
    aff_dict = {elem.attrib.values()[0]:elem.text_content() for elem in article.xpath(".//front/article-meta/aff|.//front/article-meta/contrib-group/aff")}
    author_list = []
    for a in auth_list:
        auth_dict = {}
        try:
            aff_ind = a.xpath('.//xref')[0].attrib.values()[1]
            aff_val_pull = aff_dict[aff_ind]
            aff_val_format = re.sub("\d+","",aff_val_pull)
            aff_val_replace = aff_val_format.replace("\n"," ")
            aff_val = ' '.join(aff_val_replace.split())
        except:
            aff_val = None
        try:
            contact_val = a.xpath('.//email')[0].text_content()
        except:
            contact_val = [elem.text_content() for elem in article.xpath(".//front/article-meta/author-notes/corresp/email")][0]
        auth_dict['fname'] = a.xpath('.//given-names')[0].text_content()
        auth_dict['lname'] = a.xpath('.//surname')[0].text_content()
        auth_dict['contact'] = contact_val
        auth_dict['affl'] = aff_val
        author_list.append(auth_dict)
    return author_list

#Define parser function
def parse_pmc(article):

    try:
        abs_dict_list = pmc_abstract(article)
    except:
        abs_dict_list = None
    try:
        auth_dict_list = pmc_author(article)
    except:
        auth_dict_list = None
    try:
        dates_dict_list = pmc_dates(article)
    except:
        dates_dict_list = None
    try:
        id_dict = pmc_ids(article)
    except:
        id_dict = None
    try:
        journal_dict = pmc_journal(article)
    except:
        journal_dict = None
    try:
        kwd_dict_list = pmc_kwd(article)
    except:
        kwd_dict_list = None
    try:
        pub_type_list = pmc_pub_type(article)
    except:
        pub_type_list = None
    try:
        title = pmc_titles(article)
    except:
        title = None
    try:
        optionalId01 = id_dict['doi']
    except:
        optionalId01 = None
    try:
        optionalId02 = id_dict['pmid']
    except:
        optionalId02 = None


    d = {
        'title':title,
        'associatedId': id_dict['pmc'],
        'author': auth_dict_list,
        'journalName' : journal_dict['journal-title'],
        'journalISO':journal_dict['journal-id'],
        'pubtype': pub_type_list,
        'publishdate':dates_dict_list[0],
        'publishdatefull':dates_dict_list[1],
        'meshterms': kwd_dict_list,
        'abstract':abs_dict_list,
        'optionalId01' :optionalId01,
        'optionalId02': optionalId02,
        'pullsource': 'pmc'
    }

    return d

def parse_all(article_list):
  article_dict_list = []
  for art in article_list:
    try:
        d = parse_pmc(art)
        article_dict_list.append(d)
    except:
        pass
  parsed_df = pd.DataFrame(article_dict_list)
  return parsed_df

def parse_properties(parsed_df):
    unique_id = helper.create_unique_id()
    now = datetime.datetime.now()
    time_stamp = now.strftime("%Y-%m-%d %H:%M")
    # id_list = helper.id_run('search')
    # run_fetch = self.pub_fetch(id_list)
    # article_list = helper.xml_to_html(run_fetch,self.input_db)
    n_records_parsed = len(parsed_df.index)
    prop_dict = {'id':unique_id,'id_type':'parse'
    ,'input_db':'pmc','record_count':n_records_parsed
    ,'run_date':time_stamp}
    return prop_dict

def main():
    full_doc = helper.id_run('fetch','pmc')
    article_list = helper.xml_to_html(full_doc,'pmc')
    parsed_df = parse_all(article_list)
    prop_dict = parse_properties(parsed_df)
    unique_id = prop_dict['id']
    helper.serialize_output(unique_id,parsed_df)
    helper.update_id_json(prop_dict)
