'''
Created on Apr 7, 2016

@author: zhongzhu
'''
from os.path import devnull
from subprocess import check_output


DEVNULL = open(devnull, 'wb')

tregex_path = '../lib/stanford-tregex-2015-12-09/'
tregex_class_path = tregex_path + 'stanford-tregex.jar:' + tregex_path + 'lib/*'

label_subject = "SUBJECT"
label_NP_in_PP = "pNP"

# use this method to write the string to a temp file before use the script
def write_to_temp(tree, temp_file="../temp/__temp"):
    with open(temp_file, "w+") as f:
        f.write(str(tree))
        f.close()
    return temp_file

# call tsurgeon in java
def tsurgeon(tree_file=None, pattern=None, op=None, script=None):
    params = ['java', '-mx100m', '-classpath', tregex_class_path,
              'edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon', '-treeFile', tree_file, '-s'] 
    if pattern and op:
        params.extend(['-po', pattern, op])
    else:
        params.extend(script)
    return check_output(params, stderr=DEVNULL)

# call tregex in java
def tregex(tree_file=None, pattern=None):
    return check_output(['java', '-mx100m', '-classpath', tregex_class_path,
                  'edu.stanford.nlp.trees.tregex.TregexPattern',
                  '-s', pattern, tree_file], stderr=DEVNULL)

# remove negation
def remove_negation(tree):
    f = write_to_temp(tree)
    pattern = 'VP < RB=neg'
    unnegated_treestr = tsurgeon(f, pattern, 'prune neg')
    return unnegated_treestr

# relabel subject
def relabel_subject(tree):
    f = write_to_temp(tree)
    pattern = 'ROOT < (S < (NP=subj $++ VP))'
    relabeled_treestr = tsurgeon(f, pattern, 'relabel subj ' + label_subject)
    return relabeled_treestr

# relabel NP in PP
def relabel_NP_in_PP(tree):
    f = write_to_temp(tree)
    pattern = 'PP < NP=pNP'
    relabeled_treestr = tsurgeon(f, pattern, 'relabel pNP ' + label_NP_in_PP)
    return relabeled_treestr

# Checks whether there are auxiliaries in the sentence.
def test_aux(tree):
    f = write_to_temp(tree)
    # Pattern partly from the Heilman dissertation - page 74.
    pattern = ('ROOT=root < (S=clause <+(/VP.*/) (VP [ < /(MD|VB.?)/=aux < ' + 
              '(VP < /VB.?/=verb) | < (/(VB.?)/=aux < is|was|were|am|are|has' + 
              '|have|had|do|does|did $ VP) | < (/(VB.?)/=aux < ' + 
              'is|was|were|am|are)]))')  
    check_aux = tregex(f, pattern)
    if check_aux:
        return True
    return False

def get_main_verbs(tree):
    f = write_to_temp(tree)
    pattern = '/(VB.?)/=main >+ (VP) (S > ROOT)'
    main_verbs = tregex(f, pattern)
    return main_verbs

# Changes the label of every auxiliary to AUX.
def mark_aux(tree):
    f = write_to_temp(tree)
    pattern = ('ROOT=root < (S=clause <+(/VP.*/) (VP [ < /(MD|VB.?)/=aux < ' + 
              '(VP < /VB.?/=verb) | < (/(VB.?)/=aux < is|was|were|am|are|has' + 
              '|have|had|do|does|did $ VP) | < (/(VB.?)/=aux < ' + 
              'is|was|were|am|are)]))') 
    aux_marked_treestr = tsurgeon(tree_file=f, pattern=pattern, op="relabel aux AUX")
    return aux_marked_treestr


# Moves the most dominant auxiliary ahead of the clause.
def move_aux(tree):
    f = write_to_temp(tree)
    pattern = 'ROOT < (S=clause < (VP < AUX=aux))'
    transformed_treestr = tsurgeon(f, pattern, 'move aux $+ clause')
    return transformed_treestr


# insert proper 'do' verb to the tree
def insert_do(tree, pos, do_form):
    f = write_to_temp(tree)
    pattern = 'ROOT <: S=clause'
    transformed_treestr = tsurgeon(f, pattern, 'insert (%s %s) $+ clause' % (pos, do_form)) 
    return transformed_treestr

# remove the auxiliary verb in front
def remove_aux(tree):
    f = write_to_temp(tree)
    inversed_tree = tsurgeon(tree_file=f, script=['../scripts/sq_remove_aux'])
    return inversed_tree

# from question to statement
def revert_aux(tree):
    f = write_to_temp(tree)
    inversed_tree = tsurgeon(tree_file=f, script=['../scripts/sq_insert_target',
                                  '../scripts/sq_move_aux',
                                  '../scripts/sq_excise_target'])
    return inversed_tree


# returns the subject NP of a sentence
def findSubject(tree):
    f = write_to_temp(tree)
    pattern = 'NP > (S > ROOT) $ VP'
    subj = tregex(f, pattern)
    return subj


# if a tree has a subordinate clause, returns it.
def hasSubordinateClause(tree):
    f = write_to_temp(tree)
    pattern = 'SBAR > (S > ROOT)'
    return tregex(f, pattern)


# move leading prepositional phrase to be the last child of main VP
def moveLeadingPP(tree):
    f = write_to_temp(tree)
    pattern = '/PP/=lead > (S > ROOT) $ (/VP/=main)'
    return tsurgeon(f, pattern, 'move lead >-1 main')


# returns participle modifier if it's there
def hasParticipleMod(tree):
    f = write_to_temp(tree)
    pattern = 'S=mod > (S > ROOT) $ NP $ VP < (VP < VBG)'
    return tregex(f, pattern)


# checks whether the tree has a subject and finite main verb
def hasSubjFMV(tree):
    f = write_to_temp(tree)
    pattern = 'ROOT < (S < (NP $ VP))'
    if tregex(f, pattern) == '':
        return False
    return True

# removes non-restrictive appositives and relative clauses that modify
# the subject NP
def remove_internal_mods(tree):
    f = write_to_temp(tree)
    pattern = '/,/ $+ (/NP|SBAR/=mod > (NP > (S > ROOT)) !>1 NP)'
    return tsurgeon(f, pattern, 'delete mod')
    

# removes participle phrases that modify the subject NP
def remove_participle_mods(tree):
    f = write_to_temp(tree)
    pattern = 'S=mod > (S > ROOT) $ NP $ VP < (VP < VBG)'
    return tsurgeon(f, pattern, 'delete mod')


# removes leading modifiers to the subject NP
def remove_leading_mods(tree):
    f = write_to_temp(tree)
    pattern = '/PP/=mod $+ (/,/ $+ NP > (S > ROOT))'
    return tsurgeon(f, pattern, 'delete mod')


# removes verb modifiers offset by commas
def remove_verb_modifiers(tree):
    f = write_to_temp(tree)
    pattern = '/.?/=mod > VP $ (/VB.?/ $+ /,/)'
    return tsurgeon(f, pattern, 'delete mod')


# checks if a tree has conjoined VP, S or SBAR
def hasSubConjuncts(tree):
    f = write_to_temp(tree)
    pattern = 'CC=conj $+ /VP|SBAR/ !< /or|nor/'
    return tregex(f, pattern)


# checks if a tree has sentential conjuncts
def hasConjuncts(tree):
    f = write_to_temp(tree)
    pattern = 'S > S $+ (CC !< /or|nor/ $+ S)'
    return tregex(f, pattern)


# returns pair of conjoined sentences
def extractConjuncts(tree):
    f = write_to_temp(tree)
    pattern1 = 'S > S $+ CC'
    pattern2 = 'S > S $- CC'
    conjunct1 = tregex(f, pattern1).strip()
    conjunct2 = tregex(f, pattern2).strip()
    conjunct1 = '(ROOT %s (. .))' % conjunct1
    conjunct2 = '(ROOT %s (. .))' % conjunct2
    return (conjunct1, conjunct2)
    

# extracts sentences for conjoined VPs and SBARs
# FAILS WHEN CONJUNCTS OFFSET BY COMMAS
def extract_sub_conjuncts(tree):
    f = write_to_temp(tree)
    pattern1 = '/VP|SBAR/=conjunct $+ /CC/=conj'
    pattern2 = '/CC/=conj $+ /VP|SBAR/=conjunct'
    tree_str_1 = tsurgeon(f, pattern1, 'delete conjunct')
    g = write_to_temp(tree_str_1, "../temp/__temp2")
    tree_str_1 = tsurgeon(g, pattern2, 'delete conj')
    tree_str_2 = tsurgeon(f, pattern2, 'delete conjunct')
    g = write_to_temp(tree_str_2, "../temp/__temp2")
    tree_str_2 = tsurgeon(g, pattern1, 'delete conj')
    return (tree_str_1, tree_str_2)


##############  stanford parser wrapper ################

temp_file = "../temp/__parser_temp"
stanford_parser_jar = '../lib/stanford-parser-full-2015-04-20/stanford-parser.jar'
stanford_model_jar = '../lib/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models.jar'
document_preprocessor = 'edu.stanford.nlp.process.DocumentPreprocessor'

'''
tokenize
'''
def preprocess(paragraph):
    f = write_to_temp(paragraph)
    return check_output(['java', '-cp', stanford_parser_jar, '-mx100m', document_preprocessor, f], stderr=DEVNULL)
    
