'''
Created on Apr 17, 2016
@author: XinLu (use Brock's hw3 code)
'''
import collections
import math


def read_questions():
    fq = open("../temp/questions.txt", "r")
    questions = []
    for k in range(4000):
        questions.append(fq.readline().replace('\n',''))
    return questions


def replaceUnknownWords(questions, threshold):
    text = ' '.join(questions)
    text = text.split()
    counts = collections.Counter(text)
    for i in range(len(questions)):
        questions[i]=questions[i].split()
        questions[i]=["UNKNOWNWORD" if (counts[x] <= threshold) else x for x in questions[i]]
        # print questions[i]
    return questions


# Returns a dictionary with mapping unigram:probability,
# a dictionary with mapping unigram:uniform probability,
# and the unigram counts.
def trainUnigramAndUniform(words):
    # words = words[2:]  # We exclude <START>
    types = set(words)
    counts = collections.Counter(words)
    total = len(words)
    uniform = float(1)/len(types)
    unigramModel = dict()
    uniformModel = dict()
    for word in types:
        count = counts[word]
        unigramModel[word] = float(count)/total
        uniformModel[word] = uniform
    counts['<START>'] = 1
    return unigramModel, uniformModel, counts


# Returns a dictionary with mapping (word1, word2):P(word2|word1)
# and the bigram counts.
def trainBigram(unigramCounts, words):
    # Include the first <START>
    bigrams = [(words[n+1], words[n+2]) for n in range(len(words)-2)]
    types = set(bigrams)
    bigramModel = dict()
    counts = collections.Counter(bigrams)
    for pair in types:
        (w1, w2) = pair
        count = counts[pair]
        bigramModel[pair] = float(count)/unigramCounts[w1]
    counts[('<START>', '<START>')] = 1
    return bigramModel, counts


# Returns a dictionary with mapping (word1, word2, word3):P(word3|word1,word2)
def trainTrigram(bigramCounts, words):
    trigrams = [(words[n], words[n+1], words[n+2])
                for n in range(len(words)-2)]
    types = set(trigrams)
    trigramModel = dict()
    counts = collections.Counter(trigrams)
    for trip in types:
        (w1, w2, w3) = trip
        count = counts[trip]
        trigramModel[trip] = float(count)/bigramCounts[(w1, w2)]
    return trigramModel


# Takes a trigram and returns the interpolated probability from the four
# models trained above.
def interpolatedProb(uniformModel, unigramModel, bigramModel, trigramModel,
                     lambda1, lambda2, lambda3, lambda4, trip):
    (w1, w2, w3) = trip
    prob = ((lambda1 * trigramModel.get(trip, 0) +
             lambda2 * bigramModel.get((w2, w3), 0) +
             lambda3 * unigramModel[w3] +
             lambda4 * uniformModel[w3]))
    return prob


def perplexity(trigramModel, bigramModel, unigramModel, uniformModel,
               lambda1, lambda2, lambda3, lambda4, words, testSet):
    v = len(testSet)
    # Get testSet trigrams
    trigrams = [(testSet[n], testSet[n+1], testSet[n+2]) for n in range(v-2)]
    # Calculate perplexity
    s = 0.0
    n = 0
    for trip in trigrams:
        inter=interpolatedProb(uniformModel, unigramModel, bigramModel,
                         trigramModel, lambda1, lambda2, lambda3,
                         lambda4, trip)
        # print inter
        lq = math.log(inter)
        s += lq
        n += 1
    return math.exp(-s/n)


def add_start_stop(questions):
    for i in range(len(questions)):
        questions[i] = ["<START>", "<START>"] + questions[i] + ["<STOP>"]
    return questions


def preprocess(testText):
    testSet=[]
    testText=testText.split('\n')
    for i in range(len(testText)):
        testSet.append(("<START> <START> " + testText[i] + " <STOP>").split())
    return testText,testSet[0:len(testSet)-1]


def get_top_questions(questions, nquestion):
    # store_question()
    questions1=read_questions()
    questions2=replaceUnknownWords(questions1, 3)
    questions3=add_start_stop(questions2)
    words = []
    for question in questions3:
        words = words + question
    unigramModel, uniformModel, unigramCounts = trainUnigramAndUniform(words)
    trainBigram(unigramCounts, words)
    bigramModel, bigramCounts = trainBigram(unigramCounts, words)
    trigramModel = trainTrigram(bigramCounts, words)
    lambda1=0.25
    lambda2=0.25
    lambda3=0.25
    lambda4=0.25
    testText,testSet=preprocess(questions)

    types = set(words)
    unk = "UNKNOWNWORD"
    perplexities=[]
    for test in testSet:
        # First replace words in testSet that are not in the training set
        test = [unk if (x not in types) else x for x in test]
        # Output perplexity
        perplexities.append([perplexity(trigramModel, bigramModel, unigramModel, uniformModel,
                     lambda1, lambda2, lambda3, lambda4, words, test), test])
    
    return [t[1] for t in sorted(perplexities)]

