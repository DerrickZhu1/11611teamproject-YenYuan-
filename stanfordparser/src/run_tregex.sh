# find the main verb phrase to decompose the verb
../lib/stanford-tregex-2015-12-09/tregex.sh -s "ROOT < (S=clause < (VP=mainvp [ < (/VB.?/=tensed !< is|was|were|am|are|has|have|had|do|does|did) | < /VB.?/=tensed !< VP ]))" tree

# find the (decomposed) verb ready to be inversed 
#../lib/stanford-tregex-2015-12-09/tregex.sh "ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))" tree

#../lib/stanford-tregex-2015-12-09/