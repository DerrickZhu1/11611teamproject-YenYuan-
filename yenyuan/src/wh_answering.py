'''
Created on Apr 17, 2016
@author: XinLu
'''

import traceback
#from answer import yes_or_no
from article import Article
from gen_question import question
from simplify import simplify_sen
#from extract_answer import extract_answer
import re
import string
import nltk
from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.tree import Tree
import script_wrapper as stanford_parser
import script_wrapper as tsurgeon
from config import debug
from subprocess import check_output
import script_wrapper
import script_wrapper as stanford_parser
import script_wrapper as tsurgeon
import csv


wh_map= {"Where":["GPE"], "Who":["PERSON"], "When":["DATE","TIME"], "What":["PRODUCT","ORGANIZATION"]}
parser = StanfordParser(path_to_jar=stanford_parser.stanford_parser_jar, path_to_models_jar=stanford_parser.stanford_model_jar)

'''
def get_ranked_sentences(): #also question and sentences storage
    with open("../data/set2/a9.txt") as f:
        article = Article(f.read())
        question = "When is the most favorable time to observe Taurus in the night sky?"
        ranked_answers = extract_answer(question, article)
        # extractions = []
        print("\nQuestion: " + question + "\n")
        print("Top answer:")
        (sim, sent) = ranked_answers[0]
        print(sent)
        print("Cosine similarity: " + str(1 - sim))
        print("\nNext 5 closest:")
        for (sim, sent) in ranked_answers[1:6]:
            print(sent)
            print("Cosine similarity: " + str(1 - sim))
        print
    # store sentences
    whole = question
    for i in range(6):
        (sim, sent)=ranked_answers[i]
        whole = whole + '\n' + sent
    with open("../temp/news2.txt", "w+") as f:
        f.write(str(whole))
    return question,ranked_answers[0:6]
'''

def collect_name_entities(question,top_sentences):
    #combine question and sentences into one file
    sentence=question
    for k in range(len(top_sentences)):
        (sim, answer_sentence) = top_sentences[k]
        sentence=sentence+"\n"+answer_sentence

    with open("../temp/news2.txt", "w+") as f:
        f.write(str(sentence))
        f.close()

    if True:
        result = check_output(['./run_sst.sh', '../../temp/news2.txt'], cwd="../lib/sst-light/", stderr=script_wrapper.DEVNULL)
    else:
        result = check_output(['./run_sst.sh', '../../temp/news2.txt'], cwd="../lib/sst-light/", stderr=script_wrapper.DEVNULL)
    with open("../temp/news2.tags", "w+") as f:
        f.write(result)

    entities_l=[]
    tags_l=[]
    ii=0
    # with open("../temp/news1.tags") as tsv:
    with open("../temp/news2.tags") as tsv:
        for line in csv.reader(tsv,delimiter="\t"):
            entities_l.append([])
            tags_l.append([])
            if line==[]:
                ii=ii+1
                continue
            else:
                if line:
                    if line[3]!='0':
                        entities_l[ii].append(line[0])
                        tags_l[ii].append(line[3])
    print entities_l[1]
    print tags_l[1]
    # clean up the result from the tagger
    entities = []
    for k in range(ii):
        prev_tag_name = tags_l[k][0].split(':')[:2]
        cur_entity = entities_l[k][0]
        entities.append({})
        for i in range(1, len(tags_l[k])):
            cur_token = entities_l[k][i]
            cur_tag_name = tags_l[k][i].split(':')[:2]
            if 'I' in cur_tag_name[0] :
                cur_entity = cur_entity + " " + cur_token
            else:
                if not prev_tag_name[1] in entities[k]:
                    entities[k][prev_tag_name[1]] = []
                # change encoding, another way is to .encode('ascii','ignore')
                entities[k][prev_tag_name[1]].append(str(cur_entity))
                cur_entity = cur_token
            if i==len(tags_l[k])-1:
                if not cur_tag_name[1] in entities[k]:
                    entities[k][cur_tag_name[1]] = []
                entities[k][cur_tag_name[1]].append(str(cur_entity))
            prev_tag_name = cur_tag_name
    return entities


def get_prep(tree, answer_sentence, entity,prep):
    for i in range(0, len(tree)):
        node = tree[i]
        if isinstance(node, nltk.Tree):
            if node.label() == "PP":  # store prep
                if re.match(entity,' '.join(node.leaves()[1:])):
                    prep.append(node.leaves()[0])
            if node.height() > 2:
                get_prep(node, answer_sentence, entity,prep)


def delete_entity_in_question(entities,k):
    for (tag_a,entity_a) in entities[k+1].iteritems():
        for (tag_q,entity_q) in entities[0].iteritems():
            inters=set(entity_a).intersection(entity_q)
            if inters:
                for inter in inters:
                    entities[k + 1][tag_a].remove(inter)
    entity=entities[k + 1].copy()
    for (tag_a, entity_a) in entities[k + 1].iteritems():
        if entity[tag_a] == []:
            entity.pop(tag_a)
    return entity


def get_answer_phrase(question,top_sentences,entities):
    k=0
    wh=question.split()[0]
    while(k<6):
        # print k
        match_tags=[]
        entities[k+1]=delete_entity_in_question(entities,k) # delete entities of answer sentence from question
        for (tag,entity) in entities[k+1].iteritems(): #only get one answer phrase that is not in question
            if tag in wh_map[wh]:
                match_tags.append(tag)
        if match_tags!=[]:
            if len(match_tags)>1:
                # print 111
                (sim, answer_sentence) = top_sentences[k]
                return answer_sentence #if multiple tags use original sentence
            print(entities[k+1][match_tags[0]])
            if len(entities[k+1][match_tags[0]])>1:
                # print 222
                (sim, answer_sentence) = top_sentences[k]
                #print entities[k+1][match_tags[0]]
                return answer_sentence #if multiple entities use original sentence
            #get answer phrase
            if wh=="When" or wh=="Where":
                # print 333
                (sim,answer_sentence)=top_sentences[k]
                main_tree = parser.raw_parse(answer_sentence).next()
                # print main_tree
                prep=[]
                get_prep(main_tree,answer_sentence,entities[k+1][match_tags[0]][0],prep)
                if prep!=[]:
                    return prep[0].title()+" "+entities[k+1][match_tags[0]][0]+'.'
                else:
                    a = entities[k + 1][match_tags[0]][0].split()
                    if len(a) > 1:
                        return a[0].title()+' ' + ' '.join(a[1:]) + '.'
                    else:
                        return a[0].title() + '.'
            elif wh=="Who":
                a = entities[k + 1][match_tags[0]][0].split()
                if len(a) > 1:
                    return a[0].title()+' ' + ' '.join(a[1:]) + '.'
                else:
                    return a[0].title() + '.'
            elif wh=="What":
                return top_sentences[0][1]
            else:
                # print 444
                a = entities[k + 1][match_tags[0]][0].split()
                if len(a)>1:
                    return a[0].title() +' '+ ' '.join(a[1:]) + '.'
                else:
                    return a[0].title()+ '.'
        else:
            k=k+1
        if k==6:
            return top_sentences[0][1]

'''
def main():
    question,top_sentences=get_ranked_sentences()
    entities=collect_name_entities(question,top_sentences)
    # # entities[1]['DATE']=['the months of December and January']
    answer_phrase=get_answer_phrase(question,top_sentences,entities)
    print answer_phrase
'''

if __name__ == "__main__":
    main()