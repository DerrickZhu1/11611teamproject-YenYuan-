#!/bin/sh

export CLASSPATH=stanford-tregex.jar:lib/*:$CLASSPATH
java -mx100m edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon "$@"
