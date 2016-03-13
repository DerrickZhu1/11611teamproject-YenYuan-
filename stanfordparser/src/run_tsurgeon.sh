# inverse auxiliary verb
#../lib/stanford-tregex-2015-12-09/tsurgeon.sh -treeFile tree1 -s -po "ROOT=root < (S=clause <+(/VP.*/) (VP < /(MD|VB.?)/=aux < (VP < /VB.?/=verb)))" "move aux $+ clause"

../lib/stanford-tregex-2015-12-09/tsurgeon.sh -treeFile tree -s ../scripts/insert_aux