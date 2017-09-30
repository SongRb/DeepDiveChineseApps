#!/usr/bin/env python
#coding:utf-8
from deepdive import *
import random
from collections import namedtuple

import logging
LOG_FILENAME = 'example.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,filemode='w')

SpouseLabel = namedtuple('SpouseLabel', 'p1_id, p2_id, label, type')

# lemma is splited sentences
# token is word set
# Target Chinese word may contain one or more character in word set due to word segment rules
def contains(lemma,word_set):
    for word in word_set:
        for token in lemma:
            if word in token:
                logging.debug("True")
                return True
    return False

def set_contain(c_set,lemma):
    return len(c_set.intersection(lemma))>0



@tsv_extractor
@returns(lambda
        p1_id   = "text",
        p2_id   = "text",
        label   = "int",
        rule_id = "text",
    :[])
# heuristic rules for finding positive/negative examples of spouse relationship mentions
def supervise(
        p1_id="text", p1_begin="int", p1_end="int",
        p2_id="text", p2_begin="int", p2_end="int",
        doc_id="text", sentence_index="int", sentence_text="text",
        tokens="text[]", lemmas="text[]", pos_tags="text[]", ner_tags="text[]",
        dep_types="text[]", dep_token_indexes="int[]",
    ):

    # Constants
    LOCATED = frozenset([i.encode('utf8') for i in [u"位在",u"位于",u"出生于"]])
    COMBINATION = frozenset([i.encode('utf8') for i in [u'的']])

    # Common data objects
    
    p1_end_idx = p1_end
    p1_start_idx = p1_begin
    p2_start_idx = p2_begin
    p2_end_idx = p2_end
    
    head_lemmas = lemmas[:p1_start_idx]
    head_ner_tags = ner_tags[:p1_start_idx]
    intermediate_lemmas = lemmas[p1_end_idx+1:p2_start_idx]
    intermediate_ner_tags = ner_tags[p1_end_idx+1:p2_start_idx]
    tail_lemmas = lemmas[p2_end_idx+1:]
    tail_ner_tags = ner_tags[p2_end_idx+1:]

    spouse = SpouseLabel(p1_id=p1_id, p2_id=p2_id, label=None, type=None)

    logging.debug(str(type(lemmas[1])))
    logging.debug(str(lemmas))
    
    # 北京市...17号
    # if len(intermediate_lemmas)<=2:
    #     yield spouse._replace(p1_id = p2_id,p2_id = p1_id, label=1, type="pos:so close")

    if len(intermediate_lemmas)>25:
        yield spouse._replace(label=-1, type="neg:so far")
    
    # 位于北京的人民大会堂
    if set_contain(LOCATED,head_lemmas) and set_contain(COMBINATION,intermediate_lemmas):
        yield spouse._replace(p1_id = p2_id,p2_id = p1_id, label=1, type="pos:located in place")
        yield spouse._replace(p1_id = p1_id,p2_id = p2_id, label=-1, type="neg:reversed") 
    
    # 人民大会堂位于北京
    if set_contain(LOCATED,intermediate_lemmas):
        yield spouse._replace(label=1, type="pos:located from place")
        yield spouse._replace(p1_id = p2_id,p2_id = p1_id, label=-1, type="neg:reversed")  





