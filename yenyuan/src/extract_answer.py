'''
Created on April 14, 2016.

@author: bsennish
''' 

from __future__ import division

from math import log, sqrt

from re import match

from process_question import process_question
from nltk.stem.snowball import EnglishStemmer
from nltk.tokenize import word_tokenize

from wh_answering import get_answer_phrase, collect_name_entities
from simplify import simplify_sen



stemmer = EnglishStemmer()


def extract_answer(question, article):
    type, keywords = process_question(question)
    keywords_norm = normalize(keywords)
    #print(keywords_norm)
    sentences = article.sentences()
    tokenized = [[term.lower() for term in word_tokenize(sent)] for sent in sentences]
    tokenized_norm = [normalize(word_tokenize(sent)) for sent in sentences]
    ranked = []
    for i in range(len(sentences)):
        sent1 = tokenized[i]
        sent2 = tokenized_norm[i]
        similarity1 = cosine_similarity(keywords, sent1, tokenized)
        similarity2 = cosine_similarity(keywords_norm, sent2, tokenized_norm)
        similarity = (0.25 * similarity1) + (0.75 * similarity2)
        ranked.append((1 - similarity, sentences[i]))
    ranked = sorted(ranked)[:6]
    for pair in ranked:
        print(pair)
    ranked_sents = [word for (score, word) in ranked]
    if type == "WH":
        entities = collect_name_entities(question, ranked)
        return get_answer_phrase(question, ranked, entities)
    return yes_no(keywords_norm, ranked)
    

# TEMPORARY
def yes_no(keywords, ranked):
    top_sent = ranked[0][1]
    if ranked[0][0] > 0.002:
        return top_sent
    return "Yes"
    
    
def cosine_similarity(keywords, document, documents):
    query_vec = [get_tf_idf(term, keywords, documents) for term in keywords]
    document_vec = [get_tf_idf(term, document, documents) for term in keywords]
    dot_prod = dot_product(query_vec, document_vec)
    query_norm = sqrt(sum([n**2 for n in query_vec]))
    doc_norm = sqrt(sum([n**2 for n in document_vec]))
    if doc_norm == 0.0:
        return doc_norm
    return dot_prod/(query_norm * doc_norm)
    
    
def dot_product(vec1, vec2):
    products = [(vec1[i] * vec2[i]) for i in range(len(vec1))]
    return sum(products)
    
    
def get_tf_idf(term, document, documents):
    # Do normalization in the Article class
    tf = get_tf(term, document)
    idf = get_idf(term, documents)
    return tf*idf

    
def get_idf(term, documents):
    count = 0
    for doc in documents:
        if term in doc:
            count += 1
    idf = 1
    if count > 0:
        idf += log(len(documents)/count)
    return idf
        
    
    
def get_tf(term, document):
    tf = document.count(term)/len(document)
    return tf
    
    
def normalize(document):
    result = []
    for word in document:
        cleaned = stemmer.stem(word).lower()
        if not match(r"[^a-zA-Z\d\s:]", cleaned):
            result.append(cleaned)
    return result
    
