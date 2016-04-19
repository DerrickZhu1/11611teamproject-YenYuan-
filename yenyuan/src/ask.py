#!/usr/bin/python
'''
Created on Apr 18, 2016

@author: zhongzhu
'''
import os
from subprocess import check_output
import sys
import traceback

from article import Article
from config import debug
from gen_question import question
import ranking
from script_wrapper import DEVNULL
from simplify import simplify_sen
from util import timer_log


def clean_temp_files():
    safe_remove("../temp/article.osent")
    safe_remove("../temp/article.parse")
    safe_remove("../temp/article.replaced")
    safe_remove("../temp/article.sst")
    safe_remove("../temp/article.tagged")
    safe_remove("../temp/article.txt")

def clean_up(file_name):
    content = ""
    with open(file_name) as of:
        ori_content = of.read()
        for section in ori_content.split("\n\n"):
            csection = ""
            for line in section.split("\n"):
                if line and line[-1] in ".?!": #ignore section header
                    csection += line + "\n"
            if csection:
                clean_temp_files()
                # resolve co-reference
                with open("../temp/article.txt", "w+") as tf:
                    tf.write(csection)
                try:
                    check_output(["./arkref.sh", "-input", "../../temp/article.txt"], cwd="../lib/arkref", stderr=DEVNULL)
                    with open("../temp/article.replaced") as replaced:
                        content += replaced.read() + "\n"
                    print("."),
                except:
                    print("Pre-processing failed")
    
    with open("../temp/article.clean", "w+") as clean:
        clean.write(content)


def safe_remove(path):
    try:
        os.remove(path)
    except:
        pass


def main():
    _, file_name, nquestion = sys.argv
    clean_up(file_name)
    timer_log("reference resolution")
    questions = []
#     replaced
    with open("../temp/article.clean") as farticle:
        article = Article(farticle.read())
        for sent in article.sentences():
            print(sent)
            try:
                for simp_s in simplify_sen(sent):
                    q_generated = question(simp_s)
                    questions.extend(q_generated)
                    for q in q_generated:
                        print(q)
                    print("")
            except:
                print("failed")
                if debug:
                    traceback.print_exc()
            timer_log("one sentence")
    
    print(ranking.get_top_questions('\n'.join(questions), nquestion))
    timer_log("ranking")

#     print(questions)

if __name__ == "__main__":
    main()