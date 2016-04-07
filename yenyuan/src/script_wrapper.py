'''
Created on Apr 7, 2016

@author: zhongzhu
'''
from os.path import devnull
from subprocess import check_output


DEVNULL = open(devnull, 'wb')

tsurgeon_path = '../lib/stanford-tregex-2015-12-09/tsurgeon.sh'
tregex_path = '../lib/stanford-tregex-2015-12-09/tregex.sh'

# use this method to write the string to a temp file before use the script
def write_to_temp(tree):
    temp_file = "__temp"
    with open(temp_file, "w+") as f:
        f.write(str(tree))
        f.close()
    return temp_file

# remove negation
def remove_negation(tree):
    f = write_to_temp(tree)
    pattern = 'VP < RB=neg'
    unnegated_treestr = check_output([tsurgeon_path, '-treeFile', f, '-s', '-po', pattern, 'prune neg'], stderr=DEVNULL)
    return unnegated_treestr


# Checks whether there are auxiliaries in the sentence.
def test_aux(tree):
    f = write_to_temp(tree)
    # Pattern partly from the Heilman dissertation - page 74.
    pattern = ('ROOT=root < (S=clause <+(/VP.*/) (VP [ < /(MD|VB.?)/=aux < ' + 
              '(VP < /VB.?/=verb) | < (/(VB.?)/=aux < is|was|were|am|are|has' + 
              '|have|had|do|does|did $ VP) | < (/(VB.?)/=aux < ' + 
              'is|was|were|am|are)]))')  
    check_aux = check_output([tregex_path, '-s', pattern, f], stderr=DEVNULL)
    if check_aux:
        return True
    return False

def get_main_verbs(tree):
    f = write_to_temp(tree)
    pattern = '/(VB.?)/=main >+ (VP) (S > ROOT)'
    main_verbs = check_output([tregex_path, '-s', pattern, f], stderr=DEVNULL)
    return main_verbs

# Changes the label of every auxiliary to AUX.
def mark_aux(tree):
    f = write_to_temp(tree)
    pattern = ('ROOT=root < (S=clause <+(/VP.*/) (VP [ < /(MD|VB.?)/=aux < ' + 
              '(VP < /VB.?/=verb) | < (/(VB.?)/=aux < is|was|were|am|are|has' + 
              '|have|had|do|does|did $ VP) | < (/(VB.?)/=aux < ' + 
              'is|was|were|am|are)]))') 
    aux_marked_treestr = check_output([tsurgeon_path, '-treeFile', f, '-s', '-po', pattern, 'relabel aux AUX'], stderr=DEVNULL)
    return aux_marked_treestr


# Moves the most dominant auxiliary ahead of the clause.
def move_aux(tree):
    f = write_to_temp(tree)
    pattern = 'ROOT < (S=clause < (VP < AUX=aux))'
    transformed_treestr = check_output([tsurgeon_path, '-treeFile', f, '-s', '-po', pattern, 'move aux $+ clause'], stderr=DEVNULL)
    return transformed_treestr


# insert proper 'do' verb to the tree
def insert_do(tree, pos, do_form):
    f = write_to_temp(tree)
    pattern = 'ROOT <: S=clause'
    transformed_treestr = check_output([tsurgeon_path, '-treeFile', f, '-s', '-po', pattern, 'insert (%s %s) $+ clause' % (pos, do_form)], stderr=DEVNULL) 
    return transformed_treestr

# remove the auxiliary verb in front
def remove_aux(tree):
    f = write_to_temp(tree)
    inversed_tree = check_output([tsurgeon_path, '-treeFile', f, '-s', '../scripts/sq_remove_aux'], stderr=DEVNULL)
    return inversed_tree

# from question to statement
def revert_aux(tree):
    f = write_to_temp(tree)
    inversed_tree = check_output([tsurgeon_path, '-treeFile', f, '-s', '../scripts/sq_insert_target',
                                  '../scripts/sq_move_aux',
                                  '../scripts/sq_excise_target'],
                                  stderr=DEVNULL)
    return inversed_tree
