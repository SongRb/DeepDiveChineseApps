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
    # The word used between two names to indicate married
    MARRIED = [i.encode('utf8') for i in [u"嫁",u"娶"]]
    FAMILY = [i.encode('utf8') for i in [u"母",u"妈妈", u"父",u"爸爸", u"兄",u"弟",u"姐",u"妹", u"爷爷",u"奶奶",u"外公",u"外婆"]]

    # The word used to indicate 'with' relationship
    AND = [i.encode('utf8') for i in [u"和",u"与",u"同",u"一起"]]

    # The word used after two names to indicate married
    MAR = [i.encode('utf8') for i in [u"结婚",u"离婚",u"夫妻",u"妻", u"夫",u"老婆",u"老公",u"爱人",u"夫妇"]]
    
    MAX_DIST = 10

    # Common data objects
    p1_end_idx = min(p1_end, p2_end)
    p2_start_idx = max(p1_begin, p2_begin)
    p2_end_idx = max(p1_end,p2_end)
    intermediate_lemmas = lemmas[p1_end_idx+1:p2_start_idx]
    intermediate_ner_tags = ner_tags[p1_end_idx+1:p2_start_idx]
    tail_lemmas = lemmas[p2_end_idx+1:]
    spouse = SpouseLabel(p1_id=p1_id, p2_id=p2_id, label=None, type=None)

    logging.debug(str(type(lemmas[1])))
    logging.debug(str(lemmas))
    logging.debug(str(intermediate_lemmas))
    logging.debug(str(tail_lemmas))

    # Rule: Candidates that are too far apart
    if len(intermediate_lemmas) > MAX_DIST:
        yield spouse._replace(label=-1, type='neg:far_apart')

    # Rule: Candidates that have a third person in between
    if 'PERSON' in intermediate_ner_tags:
        yield spouse._replace(label=-1, type='neg:third_person_between')

    # Rule: Sentences that contain wife/husband in between
    #         (<P1>)([ A-Za-z]+)(wife|husband)([ A-Za-z]+)(<P2>)

    if contains(intermediate_lemmas,MARRIED):
        yield spouse._replace(label=1, type='pos:wife_husband_between')

    # Rule: Sentences that contain and ... married
    #         (<P1>)(and)?(<P2>)([ A-Za-z]+)(married)
    if contains(intermediate_lemmas,AND) and contains(tail_lemmas,MAR):
        yield spouse._replace(label=1, type='pos:married_after')

    # Rule: Sentences that contain familial relations:
    #         (<P1>)([ A-Za-z]+)(brother|stster|father|mother)([ A-Za-z]+)(<P2>)
    if contains(intermediate_lemmas,FAMILY):
        yield spouse._replace(label=-1, type='neg:familial_between')
