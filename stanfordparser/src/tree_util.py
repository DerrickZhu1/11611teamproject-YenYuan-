'''
Created on Mar 15, 2016

This file has all the wrapper functions for tregex and tsurgeon

@author: zhongzhu
'''
from subprocess import check_output

initial_tree = "__inittree"
marked_tree_file = "__auxmarkedtree"
decom_tree_file = "__decomptree"

tregex_script = '../lib/stanford-tregex-2015-12-09/tregex.sh'
tsurgeon_script = '../lib/stanford-tregex-2015-12-09/tsurgeon.sh'

def has_aux(tree_str):
    with open(initial_tree, "w+") as f:
        f.write(str(tree_str))
    check_aux_result = check_output([tregex_script, '-s',
                    'ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
                    initial_tree])
    return check_aux_result

def insert_aux_node(tree_str):
    with open(marked_tree_file, "w+") as f:
        f.write(str(tree_str))
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

def inverse_aux(tree_str):
    with open(decom_tree_file, "w+") as f:
        f.write(str(tree_str))
    inversed_tree = check_output([tsurgeon_script, '-treeFile', decom_tree_file, '-s', '-po',
          'ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))',
          'move aux $+ clause'])
    return inversed_tree