'''
Created on Mar 15, 2016

This file has all the wrapper functions for tregex and tsurgeon

@author: zhongzhu
'''
from subprocess import check_output


initial_tree = "../temp/__inittree"
marked_tree_file = "../temp/__auxmarkedtree"
decom_tree_file = "../temp/__decomptree"
temp_file = "../temp/__temp"

tregex_script = '../lib/stanford-tregex-2015-12-09/tregex.sh'
tsurgeon_script = '../lib/stanford-tregex-2015-12-09/tsurgeon.sh'

def has_aux(tree):
    with open(initial_tree, "w+") as f:
        f.write(str(tree))
    check_aux_result = check_output([tregex_script, '-s',
                    'ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
                    initial_tree])
    return check_aux_result

def insert_aux_node(tree):
    with open(marked_tree_file, "w+") as f:
        f.write(str(tree))
    tree_with_aux_node = check_output([tsurgeon_script,
                                '-treeFile',
                                marked_tree_file,
                                '-s',
                                '../scripts/insert_aux'])
    return tree_with_aux_node

def get_main_verb(tree_str):
    with open(marked_tree_file, "w+") as f:
        f.write(str(tree_str))
    main_verb = check_output([tregex_script, '-s', '/VB.?/ > (VP $ INSERT)', marked_tree_file])
    return main_verb

'''
from statement to question
'''
def inverse_aux(tree):
    with open(decom_tree_file, "w+") as f:
        f.write(str(tree))
    inversed_tree = check_output([tsurgeon_script, '-treeFile', decom_tree_file, '-s', '-po',
          'ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
          'move aux $+ clause'])
    return inversed_tree

'''
from question to statement
'''
def revert_aux(tree):
    with open(temp_file, "w+") as f:
        f.write(str(tree))
    inversed_tree = check_output([tsurgeon_script, '-treeFile', temp_file, '-s',
                                  '../scripts/sq_insert_target',
                                  '../scripts/sq_move_aux',
                                  '../scripts/sq_excise_target'])
    return inversed_tree

'''
remove the auxiliary verb in front
'''
def remove_aux(tree):
    write_temp(tree)
    inversed_tree = check_output([tsurgeon_script, '-treeFile', temp_file, '-s', '../scripts/sq_remove_aux'])
    return inversed_tree

def write_temp(tree):
    with open(temp_file, "w+") as f:
        f.write(str(tree))
