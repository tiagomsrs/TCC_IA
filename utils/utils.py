import re
import pandas as pd
import wget
import os
import nltk
from nltk.corpus import opinion_lexicon
import string

from zipfile import ZipFile
from newspaper import Article
from datetime import date, datetime, time
from bs4 import BeautifulSoup
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.tokenize import treebank

nltk.download('opinion_lexicon')
stopwords = stopwords.words('english')
tokenizer = treebank.TreebankWordTokenizer()

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

        except:
            print("Failed to download the content of url." + url)



    return completeMatrix[:]


def sentimentalAnalyzes(matrix):
    """
    :param matrix in the form of:
        [0[0] - title
          [1] - date
          [2] - link
        [1] - summary
    :return: lexical analyzes eight basic emotions (anger, fear, anticipation, trust, surprise, sadness, joy, and disgust)
                and two sentiments (negative and positive).
    """

    return None