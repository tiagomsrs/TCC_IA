import re
import pandas as pd
import wget
import os
import nltk
nltk.download('punkt')
from zipfile import ZipFile

nltk.download('opinion_lexicon')
nltk.download('stopwords')

from nltk.corpus import opinion_lexicon
import string
import matplotlib.pyplot as plt

from zipfile import ZipFile
from newspaper import Article
from datetime import date, datetime, time
from bs4 import BeautifulSoup
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.tokenize import treebank
from wordcloud import WordCloud

stopwordsEnglish = stopwords.words('english')
stopwordsPortuguese = stopwords.words('portuguese')

tokenizer = treebank.TreebankWordTokenizer()



file = 'NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'

# lexicon = pd.read_csv(file, names=['palavra', 'sentimento', 'pertence'], sep='\t')
# print(lexicon.sentimento.unique())
# print(lexicon.palavra.unique().shape)
# print(lexicon[lexicon.pertence == 1].sentimento.value_counts())
# lexicon[lexicon.pertence == 1].sentimento.value_counts().plot(kind = 'bar')
# print(lexicon[(lexicon.pertence == 1) & (lexicon.sentimento == 'positive')].head(-10))
#
# print('a')

def dateFormatGoogleApi ():
    """
    :return: Current and Previous date formated as string
    """

    currentDate = str(date.today()).split('-')

    currentMonth = int(currentDate[1])
    lastMonth = currentMonth - 1
    currentDay = int(currentDate[2])
    currentYear = int(currentDate[0])

    if (lastMonth <= 0):
        lastMonth = 12
        currentYear = currentYear - 1

    if (9 >= currentDay >= 1):
        currentDay = '0' + str(currentDay)
    else:
        currentDay = str(currentDay)

    if (9 >= currentMonth >= 1):
        currentMonth = '0' + str(currentMonth)
    else:
        currentMonth = str(currentMonth)

    if (9 >= lastMonth >= 1):
        lastMonth = '0' + str(lastMonth)
    else:
        lastMonth = str(lastMonth)

    currentYear = str(currentYear)
    currentDateFormated = currentMonth + '-' + currentDay + '-' + currentYear
    lastDateFormated = lastMonth + '-' + currentDay + '-' + currentYear

    return currentDateFormated, lastDateFormated

def dateFormatNewsApi ():
    """
    :return: Current and Previous date formated as string
    """

    currentDate = str(date.today()).split('-')

    currentMonth = int(currentDate[1])
    lastMonth = currentMonth - 1
    currentDay = int(currentDate[2]) + 1
    currentYear = int(currentDate[0])

    if (lastMonth <= 0):
        lastMonth = '12'
        currentYear = currentYear - 1

    if (currentDay > 30):
        currentDay = '01'
        lastMonth += 1
    elif (9 >= currentDay >= 1):
        currentDay = '0' + str(currentDay)
    else:
        currentDay = str(currentDay)

    if (9 >= lastMonth >= 1):
        lastMonth = '0' + str(lastMonth)
    else:
        lastMonth = str(lastMonth)

    currentYear = str(currentYear)
    lastDateFormated = currentYear + '-' + lastMonth + '-' + currentDay

    return lastDateFormated

def extractorGoogleApi (googleInput):
    """
    :param googleInput: Dataframe where:

        googleInput.values[0][0] - title
        googleInput.values[0][3] - date
        googleInput.values[0][5] - link

    :return: [title   date    link]
    """
    TITLE = 0
    DATE = 3
    LINK = 5

    dfTemp = list()

    for index in range(len(googleInput)):
        aux = [googleInput.values[index][TITLE], googleInput.values[index][DATE], googleInput.values[index][LINK]]
        dfTemp.append(aux)

    return dfTemp.copy()

def extractorNewsApi(newsInput):
    """
    :param newsInput: List where:

        newsInput[0]['title'] - title
        newsInput[0]['publishedAt'] - date
        newsInput[0]['url'] - link

    :return:
    """

    dfTemp = list()

    for index in range(len(newsInput)):
        aux = [newsInput[index]['title'], newsInput[index]['publishedAt'], newsInput[index]['url']]
        dfTemp.append(aux)

    return dfTemp.copy()

def youtubeRemoval(matrix):
    """

    :param matrix: Matrix with containing, title, date and links
    :return: matrix without news from Youtube
    """
    YOUTUBE = r"www.youtube.com"
    outputMatrix = []

    for row in range(len(matrix)):
        if re.search(YOUTUBE, matrix[row][2]):
            continue
        else:
            outputMatrix.append(matrix[row][:])

    return outputMatrix[:]

def summaryDownload(matrix):
    """

    :param matrix: Complete matrix to donwload the content
    :return:
    """
    URL = 3
    completeMatrix = []

    print("Arrive {0} news to download. ".format(len(matrix)))

    for row in range(len(matrix)):

        url = matrix[row][2]
        article = Article(url)

        try:
            article.download()
            article.parse()
            article.nlp()
            content = article.summary

            if content :
                completeMatrix.append([matrix[row][:], content])

        except Exception as e:
            print("Failed to download the content of url: " + url)
            print(e)

    print("It was possible to download {0} news .".format(len(completeMatrix)))
    return completeMatrix[:]

def clean_html(text):
    soup = BeautifulSoup(text, 'html')
    for s in soup(['script', 'style']):
        s.decompose()

    return "".join(soup.stripped_strings)

def remove_punctuation(text):
    text = [word for word in text if word not in string.punctuation]
    text = ''.join(text)

    return text

def remove_stopwords(text, language):
    # TODO : tentar achar alguma maneira de detectar a linguagem que está o texto para evitar problema de stopword errado

    text = unidecode(text)

    if language == 'pt':
        text = [word.lower() for word in text.split() if word.lower() not in stopwordsPortuguese]
    elif language == 'en':
        text = [word.lower() for word in text.split() if word.lower() not in stopwordsEnglish]

    return " ".join(text)

def sentimentalAnalyzes(matrix, language):
    """
    :param language: language used on entire project
    :param matrix: in the form of:
        [0[0] - title
          [1] - date
          [2] - link
        [1] - summary
    :return: lexical analyzes eight basic emotions (anger, fear, anticipation, trust, surprise, sadness, joy, and disgust)
                and two sentiments (negative and positive).
    """
    SUMMARY = 1

    for row in range(len(matrix)):
        matrix[row][SUMMARY] = clean_html(matrix[row][SUMMARY])
        matrix[row][SUMMARY] = remove_punctuation(matrix[row][SUMMARY])
        matrix[row][SUMMARY] = remove_stopwords(matrix[row][SUMMARY], language)
        matrix[row][SUMMARY] = matrix[row][SUMMARY].lower()


    plotWordCloud(matrix, language)

    pos_list = set(opinion_lexicon.positive())
    neg_list = set(opinion_lexicon.negative())

    dataset['sentiment_clean'] = dataset['clean_text'].apply(sentiment, args=(pos_list, neg_list))

    # nrc_pos = set(pivot_lexicon[pivot_lexicon.positive == 1].palavra)
    # nrc_neg = set(pivot_lexicon[pivot_lexicon.negative == 1].palavra)
    # dataset['sentiment_clean_nrc'] = dataset['clean_text'].apply(sentiment, args=(nrc_pos, nrc_neg))


    return None


def sentimentCount(sentence, pos_list, neg_list):
    sent = 0
    words = [word for word in tokenizer.tokenize(sentence)]

    for word in words:
        if word in pos_list:
            sent += 1
        elif word in neg_list:
            sent -= 1

    return sent

def plotWordCloud(matrix, language):
    SUMMARY = 1

    if language == 'pt':
        wc = WordCloud(width=800, height=400, max_words=200, stopwords=stopwordsPortuguese)
    elif language == 'en':
        wc = WordCloud(width=800, height=400, max_words=200, stopwords=stopwordsEnglish)

    corpus = ""
    for row in range(len(matrix)):
        corpus += " " + matrix[row][SUMMARY]

    wc.generate(corpus)
    plt.figure(figsize=(10, 20))
    plt.imshow(wc)
    plt.axis('off')
    plt.show()