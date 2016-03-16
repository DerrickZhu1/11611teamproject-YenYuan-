'''
Created on Mar 16, 2016

@author: zhongzhu
'''
from subprocess import check_output


temp_file = "../temp/__parser_temp"
stanford_parser_jar = '../lib/stanford-parser-full-2015-04-20/stanford-parser.jar'
document_preprocessor = 'edu.stanford.nlp.process.DocumentPreprocessor'

def preprocess(paragraph):
    write_temp(paragraph)
    return check_output(['java', '-cp', stanford_parser_jar, '-mx100m', document_preprocessor, temp_file])
    
def write_temp(tree):
    with open(temp_file, "w+") as f:
        f.write(str(tree))