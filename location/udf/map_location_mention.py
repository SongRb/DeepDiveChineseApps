#!/usr/bin/env python
# encoding:utf8

import re

from deepdive import *

number_pattern = r'[^一二三四五六七八九十0-9年月日时分秒]'
number_search = re.compile(number_pattern).search


def number_match(strg):
    return not bool(number_search(strg))


LOCATION_SET = ['亚', '斯克', '斯坦', '堡', '拉巴德', '波利斯', '波里斯', '维尔', '国', '州', '省',
                '市', '区', '县', '旗', '镇', '乡', '村', '屯', '道', '街', '路', '号', '洲', '山脉',
                '山', '河', '江', '湖', '海', '洋', '道', '郡', '邑', '洞', '里', '町', '坊', '社','站','厂',]


def match_postfix(str):
    for postfix in LOCATION_SET:
        postfix_length = len(postfix)
        if len(str) >= postfix_length and str[-postfix_length:] == postfix:
            if len(str) == postfix_length:
                return 0
            else:
                return 1
    return -1


@tsv_extractor
@returns(lambda
         mention_id="text",
         mention_text="text",
         doc_id="text",
         sentence_index="int",
         begin_index="int",
         end_index="int",
         : [])
def extract(
    doc_id="text",
    sentence_index="int",
    tokens="text[]",
    ner_tags="text[]",
):
    """
    Finds phrases that are continuous words tagged with PERSON.
    """
    num_tokens = len(ner_tags)
    # find all first indexes of series of tokens tagged as PERSON
    first_index = 0
    end_index = 0
    while first_index < num_tokens:
        if ner_tags[first_index] != 'O':
            end_index = first_index
            previous_tag = ner_tags[first_index]
            while end_index < num_tokens and previous_tag == ner_tags[end_index]:
                end_index += 1
            fi = first_index
            ei = end_index - 1
            first_index = end_index
            mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, fi, ei)
            mention_text = "".join(
                map(lambda i: tokens[i], xrange(fi, ei + 1)))
            if not number_match(mention_text):
                # Output a tuple for each PERSON phrase
                yield [mention_id,mention_text,doc_id,sentence_index,fi,ei,]

        else:
            res = match_postfix(tokens[first_index])
            if res == 1 or (res == 0 and first_index == 0):
                mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, first_index, first_index)
                mention_text = tokens[first_index]
                yield [mention_id,mention_text,doc_id,sentence_index,first_index,first_index,]
            elif res == 0 and first_index != 0:
                mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, first_index - 1, first_index)
                mention_text = tokens[first_index - 1] + tokens[first_index]
                yield [mention_id,mention_text,doc_id,sentence_index,first_index-1,first_index,]

            first_index += 1


# if __name__ == '__main__':
#     doc1 = [
# '1',1,

# u'2007年,末,，,社民,连遭,揭发,其,位于,九龙,尖沙市,的,总部,，,是,黑社会,大佬,的,物业,，,2007年,12月,24日,，,社民,连,知道,此,事,曝光,后,，,外务,副主席,劳永乐,认为,投诉,指控,严重,，,即使,租约,合法,，,仍,可能,影响,社民,连,的,公信力,，,希望,尽快,开会,及,向,公众,澄清,，,但,其他,核心,成员,如,主席,黄毓民,、,秘书长,陶君行,、,常委,陈伟业,等,均,认为,做法,毫无,问题'
# ,
# u'MISC,MISC,O,O,O,O,O,O,MISC,MISC,O,O,O,O,O,O,O,O,O,MISC,MISC,MISC,O,O,O,O,O,O,O,O,O,O,O,PERSON,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,PERSON,O,O,PERSON,O,O,PERSON,O,O,O,O,O,O'
#     ]

#     doc1[2] = doc1[2].split(',')
#     doc1[3] = doc1[3].split(',')

#     for i in extract(doc1[0],doc1[1],doc1[2],doc1[3]):
#         print i,i[1]
