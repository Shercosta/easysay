import json
import math
from numpy.linalg import norm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import nltk
import re
import sys
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import string
from string import digits
from sklearn.pipeline import Pipeline
from spell import spell_check

# from Lemma import lemmatization

# print("Masukkan Kunci Jawaban:")
kj = sys.argv[1]
# print("Masukkan Jawaban Siswa:")
jawaban = sys.argv[2]


def case_folding(text):
    pattern = r"[" + string.punctuation + "]"
    punct = re.sub(pattern, " ", str(text))
    case_fold = punct.lower()
    return case_fold


def spellcheck(text):
    text = spell_check(text)
    return text


def tokenization(text):
    tokens = re.split(" ", text)
    return tokens


def remove_digits(text):
    text = [item for item in text if item.isalpha()]
    return text


sw = nltk.corpus.stopwords.words("indonesian")


def remove_SW(text):
    text = [item for item in text if not item in sw]
    return text


factory = StemmerFactory()
stemmer = factory.create_stemmer()


def stemming(text):
    text = [stemmer.stem(item) for item in text]
    return text


# def lemma(text):
#     text = lemmatization(text)
#     return text


def term(q, ans):
    for i in q:
        if i == "":
            q.remove("")
    for i in ans:
        if i == "":
            ans.remove("")

    BoWQ = set(q)
    BoWA = set(ans)

    uniqueWords = BoWQ.union(BoWA)
    # print(uniqueWords)

    numOfWordsQ = dict.fromkeys(uniqueWords, 0)
    for word in q:
        numOfWordsQ[word] += 1

    numOfWordsA = dict.fromkeys(uniqueWords, 0)
    for word in ans:
        numOfWordsA[word] += 1

    # print('Unique words', numOfWordsA)

    term = pd.DataFrame([numOfWordsQ, numOfWordsA])
    term = term.transpose()
    term.columns = ["TF_Q", "TF_Ans"]

    # display(term)

    dfQ = dict.fromkeys(uniqueWords, 0)
    for word in BoWQ:
        dfQ[word] += 1

    dfA = dict.fromkeys(uniqueWords, 0)
    for word in BoWA:
        dfA[word] += 1

    term["DF_Q"] = dfQ.values()
    term["DF_A"] = dfA.values()

    DF = []
    for i in range(len(uniqueWords)):
        DF.append(term["DF_Q"][i] + term["DF_A"][i])
    term["DF"] = DF
    # display(term)

    idfDict = []

    for i in range(len(term["DF"])):
        idfDict.append(math.log10((2 + 1) / (term["DF"][i] + 1)) + 1)
        # print(idfDict)
    term["IDF"] = idfDict

    # display(term)

    tfidfQ = []
    tfidfA = []
    for i in range(len(uniqueWords)):
        tfidfQ.append(term["TF_Q"][i] * term["IDF"][i])
        tfidfA.append(term["TF_Ans"][i] * term["IDF"][i])

    term["TF-IDF_Q"] = np.array(tfidfQ)
    term["TF-IDF_A"] = np.array(tfidfA)

    cosine = np.dot(tfidfQ, tfidfA) / (np.linalg.norm(tfidfQ) * np.linalg.norm(tfidfA))

    if math.isnan(cosine):
        cosine = 0
    skor = round((cosine * 100), 2)
    return skor


case_fold_q = case_folding(kj)
case_fold_ans = case_folding(jawaban)
spell_q = spell_check(case_fold_q)
spell_ans = spell_check(case_fold_ans)
token_q = tokenization(spell_q)
token_ans = tokenization(spell_ans)
token_q = remove_digits(token_q)
token_ans = remove_digits(token_ans)
filter_q = remove_SW(token_q)
filter_ans = remove_SW(token_ans)

stem_q = stemming(filter_q)
stem_ans = stemming(filter_ans)

# lemma_q = lemma(filter_q)
# lemma_ans = lemma(filter_ans)

# print("Skor Tanpa pre-processing: ", term(tokenization(kj),tokenization(jawaban)))
# print("Skor Menggunakan Stemming: ", term(stem_q, stem_ans))
# print("Skor Menggunakan Lemmatization: ", term(lemma_q, lemma_ans))

sctScore = str(term(stem_q, stem_ans))
newfile = open(f"{sys.argv[3]}.txt", "a")
# newfile.write(
#     '{"kj":"'
#     + case_fold_q
#     + '",\n"ans":"'
#     + case_fold_ans
#     + '",\n"score":'
#     + sctScore
#     + "}"
# )
newfile.write(f"{sctScore}\n")
newfile.close()
print("done")
