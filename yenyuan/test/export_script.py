'''
Created on Mar 11, 2016

@author: zhongzhu
'''
import nltk

sentence = """At eight o'clock on Thursday morning
Arthur didn't feel very good."""
tokens = nltk.word_tokenize(sentence)
print(tokens)

# os.environ["STANFORDTOOLSDIR"] = "$HOME/Downloads"
# os.environ["CLASSPATH"] = "$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/stanford-postagger.jar:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/stanford-ner.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models.jar"
# os.environ["STANFORD_MODELS"] = "$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/models:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/classifiers"

# os.putenv("STANFORDTOOLSDIR", "$HOME/Downloads")
# os.putenv("CLASSPATH", "$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/stanford-postagger.jar:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/stanford-ner.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models.jar")
# os.putenv("STANFORD_MODELS", "$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/models:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/classifiers")