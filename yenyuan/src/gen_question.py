'''
Edit to Zhong's first attempt.
Created on Mar 16, 2016
authors - zhongzhu, bsennish

Changes made:
Fixed issues with aux verb handling.
- Treat have|has|had as aux only when sistered to a VP
Improved main verb recognition.
- Can handle sentences with embedded clauses.
- Can handle conjoined VP's
Handled sentences with basic negation.
Implemented improved, but still imperfect post-processing.
Cleaned up the structure of the code.

TO DO (in the very near future):
Preprocessing on complex sentences.
Fix outstanding issues with simple constructions.
- Deal with contractions (I'm, you're, etc.)
Better main verb recognition - maybe with dependency parsing.
Figure out how to stop tsurgeon from printing loads of stuff.
Maybe optimize - this is quite slow.
'''

import string
import sys

import nltk
from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tree import Tree

import script_wrapper


tag_aux_map = {"VBD": "did", "VB": "do", "VBZ": "does", "VBP": "do"}


parser_path = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"

parser = StanfordParser(model_path=parser_path)
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


# Allows us to form questions from sentences with simple negations.
def remove_negation(tree):
    words = tree.leaves()
    if 'not' in words or 'n\'t' in words:
        tree = script_wrapper.remove_negation(tree)
    return tree


# Gets the main verb when there are no auxilliaries.
# Finds VB's that directly descend from the root by ROOT < S < VP < main
def get_main_verbs(tree):
    main_verbs = script_wrapper.get_main_verbs(tree).split('\n')[:-1]
    main_verbs = [Tree.fromstring(main_verb) for main_verb in main_verbs]
    return main_verbs


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




# If the sentence has no aux verb, inserts the proper do-form before the
# clause and changes the main verb to its bare form. 
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
    transformed_treestr = script_wrapper.insert_do(tree, pos, do_form)
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
    for (word, tag) in tree.pos():
        pos[word] = tag
    words[0] = words[0][0].upper() + words[0][1:]
    punct = "?"
    if words[-1] in string.punctuation:
        words = words[:-1] + [punct]
    else:
        words += [punct]
    if pos[words[1]] != "NNP" and words[1] != 'I':
        words[1] = words[1][0].lower() + words[1][1:]
    return " ".join(detokenize(words))


def main():
    print("Enter a simple declarative sentence:")
    inputstr = sys.stdin.readline()
    while True:  # Just do a keyboard interrupt to exit the loop.
        main_tree = parser.raw_parse(inputstr).next()
        '''
        main_tree_str = save_embedded_clause(main_tree_str)
        print(main_tree_str)
        '''
        main_tree_str = remove_negation(main_tree)
        if script_wrapper.test_aux(main_tree_str):
            main_tree_str = script_wrapper.mark_aux(main_tree_str)
            main_tree_str = script_wrapper.move_aux(main_tree_str)
        else:
            main_tree_str = move_no_aux(main_tree_str)
        main_tree = Tree.fromstring(main_tree_str)
        print("\nQUESTION:")
        print(fix_output(main_tree))
        print("\nEnter a simple declarative sentence:")
        inputstr = sys.stdin.readline()


if __name__ == "__main__":
    main()
