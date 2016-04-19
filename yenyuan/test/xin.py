'''
Edit to Zhong's first attempt.
Created on Mar 16, 2016
authors - zhongzhu, bsennish

Changes made:
Fixed issues with aux verb handling.
- Treat have|has|had as aux only when sistered to a VP
Improved get_top_questions verb recognition.
- Can handle sentences with embedded clauses.
- Can handle conjoined VP's
Handled sentences with basic negation.
Implemented improved, but still imperfect post-processing.
Cleaned up the structure of the code.

TO DO (in the very near future):
Preprocessing on complex sentences.
Fix outstanding issues with simple constructions.
- Deal with contractions (I'm, you're, etc.)
Better get_top_questions verb recognition - maybe with dependency parsing.
Figure out how to stop tsurgeon from printing loads of stuff.
Maybe optimize - this is quite slow.
'''

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


tag_aux_map = {"VBD": "did", "VB": "do", "VBZ": "does", "VBP": "do"}
qhead_map = {"LOCATION": "Where", "PERSON": "Who", "ORGANIZATION": "What"}
qhead_map = {"GPE": "Where", "PERSON": "Who", "ORGANIZATION": "What", "DATE": "When", "MONEY": "How much"}
where_prep=['in', 'at', 'on', 'between', 'under', 'behind', 'upon', 'outside', 'above', 'across', 'inside', 'toward',
            'into', 'up', 'near', 'through', 'over','to']


parser = StanfordParser(path_to_jar=stanford_parser.stanford_parser_jar, path_to_models_jar=stanford_parser.stanford_model_jar)
st = StanfordNERTagger(model_filename='../lib/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz', path_to_jar="../lib/stanford-ner-2015-12-09/stanford-ner-3.6.0.jar")
lemmatizer = WordNetLemmatizer()
# embedded = []

'''
For future use.

def save_embedded_clause(tree):
    pattern = '/SBAR|S/=embed > VP'
    has_embedded =  check_output([tregex_path,
                        '-s',
                        pattern,
                        init_tree_file])
    if not has_embedded:
        return tree
    embedded.append(has_embedded)
    unembedded_treestr = check_output([tsurgeon_path,
                                '-treeFile',
                                init_tree_file,
                                '-s',
                                '-po',
                                pattern,
                                'prune embed'])
    with open(init_tree_file, "w+") as f:
        f.write(str(unembedded_treestr))
        f.close()
    tree = Tree.fromstring(unembedded_treestr)
    return tree
'''


# label some special parts
def clean_sentence(tree):
    words = tree.leaves()
    if 'not' in words or 'n\'t' in words:
        tree = tsurgeon.remove_negation(tree)
    tree = tsurgeon.relabel_subject(tree)
    tree = tsurgeon.relabel_NPinPP(tree)
    return tree

# Gets the get_top_questions verb when there are no auxilliaries.
# Finds VB's that directly descend from the root by ROOT < S < VP < get_top_questions
def get_main_verbs(tree):
    main_verbs = tsurgeon.get_main_verbs(tree).split('\n')[:-1]
    main_verbs = [Tree.fromstring(main_verb) for main_verb in main_verbs]
    return main_verbs


# Changes get_top_questions verb to bare form.
def fix_inflection(tree, main_verb):
    for node in tree:
        if isinstance(node, nltk.Tree):
            if node == main_verb:
                verb = node[0]
                node.remove(verb)
                node.insert(0, lemmatizer.lemmatize(verb, 'v'))
                break
            if node.height() > 2:
                fix_inflection(node, main_verb)

# If the sentence has no aux verb, inserts the proper do-form before the
# clause and changes the get_top_questions verb to its bare form.
def move_no_aux(tree):
    # Still need to account for cases where there is no obvious unique MV
    '''
    try:
        main_verbs = get_main_verb(tree)
    except:
        return tree
    '''
    main_verbs = get_main_verbs(tree)
    pos = main_verbs[0].label()
    do_form = tag_aux_map[pos]
    transformed_treestr = tsurgeon.insert_do(tree, pos, do_form)
    tree = Tree.fromstring(transformed_treestr)
    for main_verb in main_verbs:
        fix_inflection(tree, main_verb)
    return tree


# Detokenizes a list of tokens.
# Still needs work.
def detokenize(words):
    punct = set(list(string.punctuation))
    pos = 0
    new = []
    for word in words:
        chars = set(list(word))
        if chars.intersection(punct):
            new = new[:-1] + [words[pos - 1] + words[pos]]
        else:
            new.append(word)
        pos += 1
    return new


# Fix capitalization and punctuation on the question.
def fix_output(tree):
    words = tree.leaves()
    pos = dict()
    for (word, cur_tag) in tree.pos():
        pos[word] = cur_tag
    words[0] = words[0][0].upper() + words[0][1:]
    punct = "?"
    if words[-1] in string.punctuation:
        words = words[:-1] + [punct]
    else:
        words += [punct]
    if pos[words[1]] != "NNP" and words[1] != 'I':
        words[1] = words[1][0].lower() + words[1][1:]
    return " ".join(detokenize(words))


def inverse_verb(main_tree_str):
    if tsurgeon.test_aux(main_tree_str):
        main_tree_str = tsurgeon.mark_aux(main_tree_str)
        main_tree_str = tsurgeon.move_aux(main_tree_str)
        main_tree = Tree.fromstring(main_tree_str)
    else:
        main_tree = move_no_aux(main_tree_str)
    return main_tree


'''
use stanford tagger to get all the named entities in the sentence
return: {u'PERSON': [u'Dempsey'], u'ORGANIZATION': [u'Major League Soccer', u'New England Revolution']}
'''
def named_entities(sentence):
    st = StanfordNERTagger(model_filename='../lib/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz', path_to_jar="../lib/stanford-ner-2015-12-09/stanford-ner-3.6.0.jar")
    tags = st.tag(word_tokenize(sentence))
    print tags
    # clean up the result from the tagger
    prev_tag_name = str(tags[0][1])
    cur_entity = str(tags[0][0])
    entities = {}
    for i in range(1, len(tags)):
        cur_tag = tags[i]
        cur_token = str(cur_tag[0])
        cur_tag_name = str(cur_tag[1])
        if cur_tag_name == prev_tag_name:
            cur_entity = cur_entity + " " + cur_token
        else:
            if not prev_tag_name in entities:
                entities[prev_tag_name] = []
            # change encoding, another way is to .encode('ascii','ignore')
            entities[prev_tag_name].append(str(cur_entity))
            cur_entity = cur_token
        prev_tag_name = cur_tag_name
    del entities['O']  # not needed, 'O' means not a named entity
    return entities

def supersense_tag(sentence):
    import csv
    # from subprocess import check_output
    # with open("../temp/news1.txt", "w+") as f:
    #     f.write(str(sentence))
    #     f.close()
    # check_output(['../sst-light-0.4/sst',
    #               'multitag','../temp/news1.txt','0','0',
    #               '../sst-light-0.4/DATA/GAZ/gazlistall_minussemcor',
    #               '../sst-light-0.4/MODELS/WSJPOSc_base_20',
    #               '../sst-light-0.4/DATA/WSJPOSc.TAGSET',
    #               '../sst-light-0.4/MODELS/WSJc_base_20',
    #               '../sst-light-0.4/DATA/WSJ.TAGSET',
    #               '>','../temp/news1.tags'])
    entities_l=[]
    tags_l=[]

    # with open("../temp/news1.tags") as tsv:
    with open("../sst-light-0.4/DATA/news1.tags") as tsv:
        for line in csv.reader(tsv,delimiter="\t"):
            if line:
                if line[3]!='0':
                    entities_l.append(line[0])
                    tags_l.append(line[3])

    # clean up the result from the tagger
    prev_tag_name = str(tags_l[0].split(':')[1])
    # if len(tags_l[0].split(':'))==3:
    #     prev_tag_name = prev_tag_name +':'+tags_l[0].split(':')[2]
    cur_entity = str(entities_l[0])
    entities = {}
    for i in range(1, len(tags_l)):
        cur_token = str(entities_l[i])
        cur_tag_name = str(tags_l[i].split(':')[1])
        # if len(tags_l[i].split(':'))==3:
        #     cur_tag_name = cur_tag_name + ':' + tags_l[i].split(':')[2]
        if cur_tag_name == prev_tag_name:
            cur_entity = cur_entity + " " + cur_token
        else:
            if not prev_tag_name in entities:
                entities[prev_tag_name] = []
            # change encoding, another way is to .encode('ascii','ignore')
            entities[prev_tag_name].append(str(cur_entity))
            cur_entity = cur_token
        if i==len(tags_l)-1:
            if not cur_tag_name in entities:
                entities[cur_tag_name] = []
            entities[cur_tag_name].append(str(cur_entity))
        prev_tag_name = cur_tag_name
    # del entities['O']  # not needed, 'O' means not a named entity
    return entities

def find_qhead(sub_entities, substr):
    for tag, entities in sub_entities.iteritems():
        for entity in entities:
            if re.match(entity, substr):
                return qhead_map[tag]

def gen_question_recur(tree, ori_sent_inversed, ori_sent, questions, all_entities, prep):
    #classify entities
    who_entities={}
    for tag, entities in all_entities.iteritems():
        if tag=='PERSON':
            who_entities[tag]=entities
    where_entities={}
    for tag, entities in all_entities.iteritems():
        if tag == 'GPE':
            where_entities[tag] = entities
    when_entities = {}
    for tag, entities in all_entities.iteritems():
        if tag == 'DATE':
            when_entities[tag] = entities

    for i in range(0, len(tree)):
        node = tree[i]
        if isinstance(node, nltk.Tree):
            if node.label() == "PP":  # store prep
                prep.append(node.leaves()[0])

            if node.label() == "pNP":  # NP in PP
                #where
                substr = ' '.join(node.leaves())
                qhead = find_qhead(where_entities, substr)
                # print '1'+str(qhead)
                if qhead and prep[-1] in where_prep:
                    # remove the substring and insert question head word in front
                    substr = prep[-1] +' '+ substr #add prep before pNP
                    questions.append(' '.join([qhead, ori_sent_inversed.replace(substr, '')]))
                #when
                substr = ' '.join(node.leaves())
                qhead = find_qhead(when_entities, substr)
                # print '1'+str(qhead)
                if qhead:
                    # remove the substring and insert question head word in front
                    substr = prep[-1] +' '+ substr  # add prep before pNP
                    questions.append(' '.join([qhead, ori_sent_inversed.replace(substr, '')]))

            if node.label() == tsurgeon.label_subject:  # for subject
                #who
                substr = ' '.join(node.leaves())
                qhead = find_qhead(who_entities, substr)
                # print '2'+str(qhead)
                if qhead:
                    # remove the substring and insert question head word in front
                    questions.append(' '.join([qhead, ori_sent.replace(substr, '')]))
                #what
                qhead_who = qhead
                qhead_when = find_qhead(when_entities, substr)
                # print '2'+str(qhead)
                if not qhead_who and not qhead_when:
                    # remove the substring and insert question head word in front
                    questions.append(' '.join(['What', ori_sent.replace(substr, '')]))

            if node.height() > 2:
                gen_question_recur(node, ori_sent_inversed, ori_sent, questions, all_entities, prep)

def cleanup_question(q):
    q = q.replace("  ", " ").replace(" \.", ".")
    q = q[:-1] + "?"
    return q

def question(inputstr):
    # entities = named_entities(inputstr)
    entities = supersense_tag(inputstr)
    # print entities

    main_tree = parser.raw_parse(inputstr).next()
    main_tree_str = clean_sentence(main_tree) #label subject, remove negation
    # TODO: mark_unmovable_tags

    main_tree = inverse_verb(main_tree_str)
    sentence = str(' '.join(Tree.fromstring(main_tree_str).leaves()))
    sentence_inversed = str(' '.join(main_tree.leaves()))
    questions = []
    print main_tree
    prep=[] #use to store prep when trave the tree
    gen_question_recur(main_tree, sentence_inversed, sentence, questions, entities, prep)
#     questions = [fix_output(q) for q in questions]
    questions = [cleanup_question(q) for q in questions]
    return questions

def get_top_questions():
    s="Tom went to New York yesterday."
    s = "New York, at Feb 9, 2001, The Associated " \
        "Press reported another overnight jump in the price of gas -up nearly " \
        "20 percent, or 65 cents a gallon, over the past year to average nearly $3.88 " \
        "a gallon nationally."
    s = "The cat went to New York at 4 P.M."
    print(question(s))
#     while True:  # Just do a keyboard interrupt to exit the loop.
#         print("\nEnter a simple declarative sentence:")
#         inputstr = sys.stdin.readline()
#         q = question(inputstr)
#         print("\nQUESTION:")
#         print(q)


if __name__ == "__main__":
    get_top_questions()
    # s=""
    # supersense_tag(s)