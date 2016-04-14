from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tokenize import sent_tokenize, word_tokenize

import script_wrapper


def main():
    parser = StanfordParser(path_to_jar=script_wrapper.stanford_parser_jar, path_to_models_jar=script_wrapper.stanford_model_jar)
    st = StanfordNERTagger(model_filename='../lib/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz', path_to_jar="../lib/stanford-ner-2015-12-09/stanford-ner-3.6.0.jar")
    raw_sent = "Dempsey was drafted by Major League Soccer club New England Revolution."
    sent = word_tokenize(raw_sent)
    ne_tuple = st.cur_tag(sent)  # ##need write interface for tokenized sent (http://nlp.stanford.edu/software/crf-faq.shtml#tokenized)
    print ne_tuple
    
    print parser.raw_parse(raw_sent).next()

    return
    # find name entity
    f = 0
    ne_list = []
    for (ne, label) in ne_tuple:
        if label == 'PERSON':
            f = 1
        if f and label != 'PERSON':
            break
        if f:
            ne_list.append(ne)
    # print ne_list

    init_file(main_tree)
                    ####### my issue here: 1. don't know how to get NP. 2. is there a quicker way to find PERON ?
    # try head to ask who/what
    pattern = "S < NP=np"
    head = check_output(['bash',  ###add bash !!!!
                         tregex_path,
                         '-s',
                         pattern,
                         init_tree_file])
    print head

    def get_main_verbs(tree):
        pattern = '/(VB.?)/=main >+ (VP) (S > ROOT)'
        main_verbs = check_output(['bash',  ###add bash !!!!
                                   tregex_path,
                                   '-s',
                                   pattern,
                                   init_tree_file])
        print main_verbs
        main_verbs = main_verbs.split('\n')[:-1]
        main_verbs = [Tree.fromstring(main_verb) for main_verb in main_verbs]
        return main_verbs

if __name__ == "__main__":
    main()
