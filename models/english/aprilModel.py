# %%

import nltk
from nltk.tokenize import word_tokenize

# nltk.download("punkt")
# nltk.download("averaged_perceptron_tagger")
from nltk.stem import WordNetLemmatizer

# nltk.download("wordnet")
# nltk.download("omw-1.4")
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from textblob import TextBlob
import pandas as pd
import string
import re
import sys
from nltk.corpus import stopwords

# nltk.download("stopwords")
from nltk.stem import SnowballStemmer
from textblob import TextBlob
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity

# %% [markdown]
# **Importing Dataset**

# %%

full_df = pd.read_csv(f"{sys.argv[1]}.csv")
full_df


# %% [markdown]
# **Text Preprocessing**

# %% [markdown]
# Spelling Correction

# %%
# Spelling Correction

full_df["keyAnswer"] = full_df["keyAnswer"].astype(str)
full_df["keySpell"] = full_df["keyAnswer"].apply(
    lambda txt: "".join(TextBlob(txt).correct())
)

# %%
full_df["studentAnswer"] = full_df["studentAnswer"].astype(str)
full_df["studentSpell"] = full_df["studentAnswer"].apply(
    lambda txt: "".join(TextBlob(txt).correct())
)

# %%
full_df[["keyAnswer", "keySpell"]]

# %% [markdown]
# Converting Abbreviation

# %%
contractions_dict = {
    "'s": " is",
    "ain't": "is not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "I'd": "I would",
    "I'd've": "I would have",
    "I'll": "I will",
    "I'll've": "I will have",
    "I'm": "I am",
    "I've": "I have",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have",
}

# %%
# Converting Abbreviation

contractions_re = re.compile("(%s)" % "|".join(contractions_dict.keys()))


def expand_contractions(text, contractions_dict=contractions_dict):
    def replace(match):
        return contractions_dict[match.group(0)]

    return contractions_re.sub(replace, text)


full_df["studentSpell"] = full_df["studentSpell"].apply(
    lambda x: expand_contractions(x)
)
full_df["keySpell"] = full_df["keySpell"].apply(lambda x: expand_contractions(x))

# %%
full_df[["studentAnswer", "studentSpell"]]

# %% [markdown]
# Case Folding

# %%
# Case Folding

full_df["keyLower"] = full_df["keySpell"].str.lower()
full_df["studentLower"] = full_df["studentSpell"].str.lower()

full_df[["studentSpell", "studentLower"]]

# %% [markdown]
# Removing Punctuation

# %%
# Removing Punctuation

PUNCT_TO_REMOVE = string.punctuation


def remove_punctuation(text):
    """custom function to remove the punctuation"""
    return text.translate(str.maketrans("", "", PUNCT_TO_REMOVE))


full_df["keyPunct"] = full_df["keyLower"].apply(lambda text: remove_punctuation(text))
full_df["studentPunct"] = full_df["studentLower"].apply(
    lambda text: remove_punctuation(text)
)

full_df[["studentLower", "studentPunct"]]

# %% [markdown]
# Stopword Removal

# %%
# Stopword Removal

STOPWORDS = set(stopwords.words("english"))


def remove_stopwords(text):
    """custom function to remove the stopwords"""
    return " ".join([word for word in str(text).split() if word not in STOPWORDS])


full_df["keyStopword"] = full_df["keyPunct"].apply(lambda text: remove_stopwords(text))
full_df["studentStopword"] = full_df["studentPunct"].apply(
    lambda text: remove_stopwords(text)
)

full_df[["studentPunct", "studentStopword"]]

# %% [markdown]
# Stemming

# %%
# Stemming

stemmer = SnowballStemmer("english")


def stem_words(text):
    return " ".join([stemmer.stem(word) for word in text.split()])


full_df["studentStem"] = full_df["studentStopword"].apply(lambda text: stem_words(text))
full_df["keyStem"] = full_df["keyStopword"].apply(lambda text: stem_words(text))

full_df[["studentStopword", "studentStem"]]

# %% [markdown]
# POS Tagging

# %%
studentSplit = full_df["studentStopword"]
keySplit = full_df["keyStopword"]

studentSplitWords = [nltk.word_tokenize(str(sentence)) for sentence in studentSplit]
keySplitWords = [nltk.word_tokenize(str(sentence)) for sentence in keySplit]
full_df["studentSplit"] = studentSplitWords
full_df["keySplit"] = keySplitWords

# %%
# POS Tagging

full_df["keyPostag"] = full_df["keySplit"].apply(nltk.pos_tag)
full_df["studentPostag"] = full_df["studentSplit"].apply(nltk.pos_tag)

full_df[["keyPostag", "studentPostag"]]

# %% [markdown]
# Lemmatizing

# %%
# Lemmatizing

lemmatizer = WordNetLemmatizer()
wordnet_map = {"N": wordnet.NOUN, "V": wordnet.VERB, "J": wordnet.ADJ, "R": wordnet.ADV}


def lemmatize_words(text):
    pos_tagged_text = nltk.pos_tag(text.split())
    return " ".join(
        [
            lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN))
            for word, pos in pos_tagged_text
        ]
    )


full_df["studentLemmatized"] = full_df["studentStopword"].apply(
    lambda text: lemmatize_words(text)
)
full_df["keyLemmatized"] = full_df["keyStopword"].apply(
    lambda text: lemmatize_words(text)
)
full_df[["studentStopword", "studentLemmatized"]]

# %% [markdown]
# **TF-IDF**

# %% [markdown]
# TF

# %%
# TF for Lemmatized

full_df["keyLemmatized"] = full_df["keyLemmatized"].astype(str)
full_df["studentLemmatized"] = full_df["studentLemmatized"].astype(str)

for i in range(len(full_df)):
    doc1 = full_df["keyLemmatized"][i]
    doc2 = full_df["studentLemmatized"][i]
    docs = (doc1, doc2)

    countvectorizer = CountVectorizer()
    terms = countvectorizer.fit_transform(docs)

    columns = countvectorizer.get_feature_names_out()
    tf = pd.DataFrame(
        terms.toarray(), index=["keyLemmatized", "studentLemmatized"], columns=columns
    )

    # print(tf)

# %%
# TF for Stem

full_df["keyStem"] = full_df["keyStem"].astype(str)
full_df["studentStem"] = full_df["studentStem"].astype(str)

for i in range(len(full_df)):
    doc12 = full_df["keyStem"][i]
    doc22 = full_df["studentStem"][i]
    docs2 = (doc12, doc22)
    countvectorizer2 = CountVectorizer()
    terms2 = countvectorizer2.fit_transform(docs2)

    columns2 = countvectorizer2.get_feature_names_out()
    tf2 = pd.DataFrame(
        terms2.toarray(), index=["keyStem", "studentStem"], columns=columns2
    )

    # print(tf2)

# %% [markdown]
# IDF

# %%
# IDF for Lemmatized

for i in range(len(full_df)):
    doc1 = full_df["keyLemmatized"][i]
    doc2 = full_df["studentLemmatized"][i]
    docs = (doc1, doc2)

    countvectorizer = CountVectorizer()
    terms = countvectorizer.fit_transform(docs)

    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(terms)

    df_idf = pd.DataFrame(
        tfidf_transformer.idf_,
        index=countvectorizer.get_feature_names_out(),
        columns=["idf_weights"],
    )

    # print(df_idf)


# %%
# IDF for Stem

for i in range(len(full_df)):
    doc12 = full_df["keyStem"][i]
    doc22 = full_df["studentStem"][i]
    docs2 = (doc12, doc22)
    countvectorizer = CountVectorizer()
    terms2 = countvectorizer.fit_transform(docs2)

    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(terms2)

    df_idf2 = pd.DataFrame(
        tfidf_transformer.idf_,
        index=countvectorizer.get_feature_names_out(),
        columns=["idf_weights"],
    )

    # print(df_idf2)

# %% [markdown]
# TF-IDF

# %%
# TF-IDF for Lemmatized

for i in range(len(full_df)):
    doc1 = full_df["keyLemmatized"][i]
    doc2 = full_df["studentLemmatized"][i]
    docs = (doc1, doc2)
    countvectorizer = CountVectorizer()
    terms = countvectorizer.fit_transform(docs)
    X = tfidf_transformer.fit_transform(terms)
    tf_idf = pd.DataFrame(X.toarray(), columns=countvectorizer.get_feature_names_out())
    # print(tf_idf)

# %%
# TF-IDF for Stem

for i in range(len(full_df)):
    doc12 = full_df["keyStem"][i]
    doc22 = full_df["studentStem"][i]
    docs2 = (doc12, doc22)
    countvectorizer = CountVectorizer()
    terms2 = countvectorizer.fit_transform(docs2)

    X2 = tfidf_transformer.fit_transform(terms2)
    tf_idf2 = pd.DataFrame(
        X2.toarray(), columns=countvectorizer.get_feature_names_out()
    )
    # print(tf_idf2)

# %% [markdown]
# **Cosine Similarity**

# %%
# Cosine Similarity for Lemmatized

tfidf_vectorizer = TfidfVectorizer()
similarity = []

full_df["keyLemmatized"] = full_df["keyLemmatized"].astype(str)
full_df["studentLemmatized"] = full_df["studentLemmatized"].astype(str)

for i in range(len(full_df)):
    doc1 = full_df["keyLemmatized"][i]
    doc2 = full_df["studentLemmatized"][i]
    docs = (doc1, doc2)
    tfidf_matrix = tfidf_vectorizer.fit_transform(docs)
    tfidf_tokens = tfidf_vectorizer.get_feature_names_out()
    df_tfidfvect = pd.DataFrame(
        data=tfidf_matrix.toarray(),
        index=["keyLemmatized", "studentLemmatized"],
        columns=tfidf_tokens,
    )
    # print(df_tfidfvect)

    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
    # print("Cosine Similarity =", cosine_sim[0][0])
    # print("\n")
    similarity.append(cosine_sim[0][0])

full_df["cosineSimilarityLemma"] = similarity

# cosinelemma = full_df['cosineSimilarityLemma']
# cosinelemma.to_csv('cosinelemma.csv')

# %%
# Cosine Similarity for Stem

tfidf_vectorizer2 = TfidfVectorizer()
similarity2 = []

full_df["keyStem"] = full_df["keyStem"].astype(str)
full_df["studentStem"] = full_df["studentStem"].astype(str)

for i in range(len(full_df)):
    doc12 = full_df["keyStem"][i]
    doc22 = full_df["studentStem"][i]
    docs2 = (doc12, doc22)
    tfidf_matrix2 = tfidf_vectorizer2.fit_transform(docs2)
    tfidf_tokens2 = tfidf_vectorizer2.get_feature_names_out()
    df_tfidfvect2 = pd.DataFrame(
        data=tfidf_matrix2.toarray(),
        index=["keyStem", "studentStem"],
        columns=tfidf_tokens2,
    )
    # print(df_tfidfvect2)

    cosine_sim2 = cosine_similarity(tfidf_matrix2[0], tfidf_matrix2[1])
    # print("Cosine Similarity =", cosine_sim2[0][0])
    # print("\n")
    similarity2.append(cosine_sim2[0][0])

full_df["cosineSimilarityStem"] = similarity2

# %% [markdown]
# **Scoring**

# %%
# Scoring for Lemmatized
scoring = full_df["cosineSimilarityLemma"]

scoring = scoring.mul(5)

# full_df = full_df.drop('scoreModel', axis=1)
full_df["scoreModelLemma"] = scoring

full_df[["scoreModelLemma"]]

# %%
# Scoring for Stemming
scoring2 = full_df["cosineSimilarityStem"]

scoring2 = scoring2.mul(5)

full_df["scoreModelStem"] = scoring2

full_df[["scoreModelStem"]]

# %% [markdown]
# Uji Analisis (Abaikan)

# %%
full_df.to_json()

# %%
# newfile = open("HasilPenilaianENG.json", "w")
# newfile.write(full_df.to_json())
# newfile.close()

print(full_df.to_json())
