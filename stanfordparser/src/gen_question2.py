'''
Edit to Zhong's first attempt.
Created on Mar 16, 2016
authors - zhongzhu, bsennish

Changes made:
Fixed issues with aux verb recognition.
Handled sentences with basic negation.
Implemented first pass post-processing.
Cleaned up the structure of the code.

TO DO (in the very near future):
Preprocessing on complex sentences.
Fix outstanding issues with simple constructions.
- Bugs with auxiliaries (have/has in particular)
- Deal with contractions
Better main verb recognition - maybe with dependency parsing.
Figure out how to stop tsurgeon from printing loads of stuff.
Get the post-processing right.
Maybe optimize - this is quite slow.
'''

from subprocess import check_output
import sys
import string

import nltk
from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

tag_aux_map = {"VBD": "did", "VB": "do", "VBZ": "does", "VBP": "do"}

init_tree_file = "__inittree"
marked_tree_file = "__auxmarkedtree"

tsurgeon_path = '../lib/stanford-tregex-2015-12-09/tsurgeon.sh'
tregex_path = '../lib/stanford-tregex-2015-12-09/tregex.sh'
parser_path = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"

parser = StanfordParser(model_path=parser_path)
lemmatizer = WordNetLemmatizer()


# Writes the initial tree string to the init file.
def init_file(tree):
    with open(init_tree_file, "w+") as f:
        f.write(str(tree))
    f.close()


# Allows us to form questions from sentences with simple negations.
def remove_negation(tree):
    words = tree.leaves()
    if 'not' in words:
        pattern = 'RB=neg < not'
        unnegated_treestr = check_output([tsurgeon_path,
                                '-treeFile',
                                init_tree_file,
                                '-s',
                                '-po',
                                pattern,
                                'prune neg'])
        with open(init_tree_file, "w+") as f:
            f.write(str(unnegated_treestr))
        f.close()
        tree = Tree.fromstring(unnegated_treestr)
    return tree


# Checks whether there are auxiliaries in the sentence.
def test_aux(tree):
    # Pattern partly from the Heilman dissertation - page 74.
    pattern = ('ROOT=root < (S=clause <+(/VP.*/) (VP [ < /(MD|VB.?)/=aux < ' +
              '(VP < /VB.?/=verb) | < (/(VB.?)/=aux < is|was|were|am|are|has' +
              '|have|had|do|does|did $ VP) | < (/(VB.?)/=aux < is|was|were|am|are)]))')  
    check_aux = check_output([tregex_path,
                    '-s',
                    pattern,
                    init_tree_file])
    if check_aux:
        return True
    return False


# Gets the main verb when there are no auxilliaries.
# Finds VB's that don't sister with any VPs
def get_main_verb(tree):
    pattern = '/(VB.?)/=main !$ VP'
    main_verb = check_output([tregex_path,
                    '-s',
                    pattern,
                    init_tree_file])
    main_verb = Tree.fromstring(main_verb)
    return main_verb


# Changes main verb to bare form.
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


# Changes the label of every auxiliary to AUX.
def mark_aux(tree):
    pattern = ('ROOT=root < (S=clause <+(/VP.*/) (VP [ < /(MD|VB.?)/=aux < ' +
              '(VP < /VB.?/=verb) | < (/(VB.?)/=aux < is|was|were|am|are|has' +
              '|have|had|do|does|did $ VP) | < (/(VB.?)/=aux < is|was|were|am|are)]))') 
    aux_marked_treestr = check_output([tsurgeon_path,
                                '-treeFile',
                                init_tree_file,
                                '-s',
                                '-po',
                                pattern,
                                'relabel aux AUX'])
    with open(marked_tree_file, "w+") as f:
        f.write(str(aux_marked_treestr))
    f.close()
    tree = Tree.fromstring(aux_marked_treestr)
    return tree


# Moves the most dominant auxiliary ahead of the clause.
def move_aux(tree):
    pattern = 'ROOT < (S=clause < (VP < AUX=aux))'
    transformed_treestr = check_output([tsurgeon_path,
                                '-treeFile',
                                marked_tree_file,
                                '-s',
                                '-po',
                                pattern,
                                'move aux $+ clause'])
    tree = Tree.fromstring(transformed_treestr)
    return tree


# If the sentence has no aux verb, inserts the proper do-form before the
# clause and changes the main verb to its bare form. 
def move_no_aux(tree):
    # Still need to account for cases where there is no obvious unique MV
    try:
        main_verb = get_main_verb(tree)
    except:
        return tree
    pos = main_verb.label()
    do_form = tag_aux_map[pos]
    pattern = 'ROOT <: S=clause'
    transformed_treestr = check_output([tsurgeon_path,
                                '-treeFile',
                                init_tree_file,
                                '-s',
                                '-po',
                                pattern,
                                'insert (%s %s) $+ clause' % (pos, do_form)])
    tree = Tree.fromstring(transformed_treestr)
    fix_inflection(tree, main_verb) 
    return tree


# Buggy
def detokenize(words):
    punct = string.punctuation
    dec = 0
    for i in range(len(words)):
        pos = i - dec
        for c in words[pos]:
            if c in punct:
                words[pos-1] += words[pos]
                words.remove(words[pos])
                dec += 1
                break


# Fix capitalization and punctuation on the question.
# STILL NEED TO ACCOUNT FOR OTHER PUNCTUATION: DETOKENIZE
def fix_output(tree):
    words = tree.leaves()
    pos = dict()
    for (word, tag) in tree.pos():
        pos[word] = tag
    words[0] = words[0][0].upper() + words[0][1:]
    punct = "?"
    if words[-1] in string.punctuation:
        words = words[:-1]
    if pos[words[1]] != "NNP" and words[1] != 'I':
        words[1] = words[1][0].lower() + words[1][1:]
    return " ".join(words) + punct


def main():
    print("Enter a simple declarative sentence:")
    inputstr = sys.stdin.readline()
    while True:  # Just do a keyboard interrupt to exit the loop.
        main_tree = parser.raw_parse(inputstr).next()
        init_file(main_tree)
        main_tree = remove_negation(main_tree)
        if test_aux(main_tree):
            main_tree = mark_aux(main_tree)
            main_tree = move_aux(main_tree)
        else:
            main_tree = move_no_aux(main_tree)
        print("\nQuestion:")
        print(fix_output(main_tree))
        print("\nEnter a simple declarative sentence:")
        inputstr = sys.stdin.readline()


if __name__=="__main__":
    main()
