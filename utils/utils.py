import re
import pandas as pd
import wget
import os
import nltk
import unicodedata
import string
import concurrent.futures
import tweepy
import json
from nltk.corpus import opinion_lexicon
from newspaper import Article
from datetime import date, datetime
from bs4 import BeautifulSoup
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.tokenize import treebank
from wordcloud import WordCloud
from pathlib import Path
from nltk.stem import PorterStemmer
import snowballstemmer
import requests as req
import subprocess

from tweepy import Stream
nltk.download('punkt')
nltk.download('opinion_lexicon')
nltk.download('stopwords')

stopwordsEnglish = stopwords.words('english')
stopwordsPortuguese = stopwords.words('portuguese')
tokenizer = treebank.TreebankWordTokenizer()

TWITTER_CONSUMER_KEY = "ktAHnlHevDnBaQiF46RNJd9yy"
TWITTER_CONSUMER_SECRET = "2QQgh8SE1t6snv9bDCKre9JsBfHQov0S7Dn5ZRfVClBIa8uYQk"
TWITTER_ACCESS_TOKEN = "1251614775940984841-eJvICi2AVAGYBckaLp3QsNyzN5MAXS"
TWITTER_ACCESS_TOKEN_SECRET = "lve6sJt6DQEh127nlESUU9ei0sFk6zIULmNB3U0jG8MCh"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAADdZUgEAAAAAjqaN72bRtJpKk6JDtwYfrgXMQXo%3DyxWovPFP3HislduYDCuF5ln1622fE4BF4ibmKrteDnUyinD5hl"
DEFAULT_THRESHOLD = 10

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def dateFormatGoogleApi():
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

def dateFormatNewsApi():
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

def extractorGoogleApi(googleInput):
    """
    :param googleInput: Dataframe where:

        googleInput.values[0][0] - title
        googleInput.values[0][3] - date
        googleInput.values[0][5] - link

    :return: [title   date    link]
    """

    dfTemp = list()

    for index in range(len(googleInput)):
        aux = [googleInput[index]['title'],
               googleInput[index]['date'],
               googleInput[index]['link']]
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

def sitesRemoval(matrix):
    """

    :param matrix: Matrix with containing, title, date and links
    :return: matrix without news from Youtube
    """
    YOUTUBE = r"www.youtube.com"
    SLASHDOT = r"slashdot.org"
    outputMatrix = []

    for row in range(len(matrix)):
        if re.search(YOUTUBE, matrix[row][2]) or re.search(SLASHDOT, matrix[row][2]):
            continue
        else:
            outputMatrix.append(matrix[row][:])

    return outputMatrix[:]

def summaryDownload(matrix, page_size, temas, language='en'):
    """
    :param matrix: Complete matrix to download the content
    :return:
    """
    completeMatrix = []
    print("Arrive {} news to download. ".format(len(matrix)))

    with concurrent.futures.ThreadPoolExecutor() as executor:

        future_to_url = {executor.submit(summary_download_data, matrix, completeMatrix, row): row for row in range(len(matrix))}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print("Failed to download the summary")

    completeMatrixOutput = []



    for row in range(len(completeMatrix)):
        text = remove_punctuation(str(completeMatrix[row][1].lower()))
        text = remove_stopwords(text, language)
        temas = remove_punctuation(temas.strip().lower())
        temas = remove_stopwords(temas, language)
        if not re.search(temas, text):
            continue
        else:
            completeMatrixOutput.append(completeMatrix[row][:])

    print("It was possible to download {0} news .".format(len(completeMatrixOutput)))
    return completeMatrixOutput[:int(page_size)]

def summary_download_data(matrix, completeMatrix, row):
    """

    :param matrix:
    :param completeMatrix:
    :param row:
    :return:
    """
    url = matrix[row][2]
    article = Article(url)
    try:
        article.download()

        article.parse()
        article.nlp()
        content = article.summary

        if content:
            completeMatrix.append([matrix[row][:], content])
            return completeMatrix

    except Exception as e:
        print("Failed to download the content of url: " + url)
        print(e)

def clean_html(text):
    """

    :param text:
    :return:
    """
    soup = BeautifulSoup(text, "html")
    for s in soup(['script', 'style']):
        s.decompose()

    return "".join(soup.stripped_strings)

def remove_punctuation(text):
    """

    :param text:
    :return:
    """
    text = [word for word in text if word not in string.punctuation]
    text = ''.join(text)

    return text

def remove_stopwords(text, language='en'):
    """

    :param text:
    :param language:
    :return:
    """
    # TODO : tentar achar alguma maneira de detectar a linguagem que está o texto para evitar problema de stopword errado

    text = unidecode(text)

    if language == 'pt':
        text = [word.lower() for word in text.split() if word.lower() not in stopwordsPortuguese]
    elif language == 'en':
        text = [word.lower() for word in text.split() if word.lower() not in stopwordsEnglish]

    return " ".join(text)

def majorityCheck(array):
    """

    :param array:
    :return:
    """
    neg_count = len(list(filter(lambda x: (x < 0), array)))
    pos_count = len(list(filter(lambda x: (x > 0), array)))
    neutral_count = len(list(filter(lambda x: (x == 0), array)))

    arrayCount = [neg_count, neutral_count, pos_count]
    max_index = arrayCount.index(max(arrayCount))

    if max_index == 0:
        return "negative"
    elif max_index == 1:
        return "neutral"
    elif max_index == 2:
        return "positive"
    else:
        return "neutral"

def applyStemming(text, language):

    if language == 'pt':
        stemmer = snowballstemmer.stemmer('portuguese')
    elif language == 'en':
        stemmer = snowballstemmer.stemmer('english')

    textStem = stemmer.stemWords(text.split())
    return " ".join(textStem)

def convertToEnglish(text):

    text = str(text)
    text = text.replace("\""," ").replace("“", " ").replace("”", " ").replace("\n", " ")
    command = "curl -X POST -u \"apikey:g-uQG9zbH3j48WJwIlXMJXLWkzwE49bmulwFNrmqLGMu\" --header \"Content-Type: application/json\""
    command = command + " --data \"{"
    command = command + "\\\"text\\\": [\\\"{}\\\"], \\\"model_id\\\":\\\"pt-en\\\"".format(str(text)) + "}\""
    command = command + " \"https://api.au-syd.language-translator.watson.cloud.ibm.com/instances/ca766625-6d33-4457-80db-db8b5fe4f2da/v3/translate?version=2018-05-01\""

    subprocess1 = subprocess.Popen(command,
                                    shell=True, stdout=subprocess.PIPE)
    subprocess_return = subprocess1.stdout.read()
    string1 = subprocess_return.decode("utf-8")
    textConverted = json.loads(string1)['translations'][0]['translation']
    return textConverted

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
        matrix[row][SUMMARY] = matrix[row][SUMMARY].lower()

    plotWordCloud(matrix, language, "trendwordcloud.png")

    if language == 'pt':
        for row in range(len(matrix)):
            matrix[row][SUMMARY] = convertToEnglish(matrix[row][SUMMARY])
            matrix[row][SUMMARY] = remove_stopwords(matrix[row][SUMMARY], 'en')
            matrix[row][SUMMARY] = applyStemming(matrix[row][SUMMARY], language)
    else:
        for row in range(len(matrix)):
            matrix[row][SUMMARY] = remove_stopwords(matrix[row][SUMMARY], 'en')
            matrix[row][SUMMARY] = applyStemming(matrix[row][SUMMARY], language)

    pos_list_opinion_lexicon = set(opinion_lexicon.positive())
    neg_list_opinion_lexicon = set(opinion_lexicon.negative())
    sentimentalCounterOpinionLexicon = list()
    sentimentalCounterOpinionLexicon.append([sentimentCount(matrix[row][SUMMARY], pos_list_opinion_lexicon,neg_list_opinion_lexicon) for row in range(len(matrix))])

    file = "utils/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"
    lexicon = pd.read_csv(file, names=['palavra', 'sentimento', 'pertence'], sep='\t')
    pivot_lexicon = lexicon.pivot(index='palavra', columns='sentimento', values='pertence').reset_index()
    pos_list_nrc = set(pivot_lexicon[pivot_lexicon.positive == 1].palavra)
    neg_list_nrc = set(pivot_lexicon[pivot_lexicon.negative == 1].palavra)
    sentimentalCounterNRC = list()
    sentimentalCounterNRC.append([sentimentCount(matrix[row][SUMMARY], pos_list_nrc, neg_list_nrc) for row in range(len(matrix))])


    file = "utils/WKWSCISentimentLexicon_v1.1.tab"
    WKWSCI = pd.read_csv(file, sep='\t', header=0)
    pos_list_WKWSCI = set(WKWSCI.loc[WKWSCI['sentiment'] > 0].values[:,0])
    neg_list_WKWSCI = set(WKWSCI.loc[WKWSCI['sentiment'] < 0].values[:,0])
    sentimentalCounterWKWSCI = list()
    sentimentalCounterWKWSCI.append([sentimentCount(matrix[row][SUMMARY], pos_list_WKWSCI, neg_list_WKWSCI) for row in range(len(matrix))])

    arraySentimentalAnalyzed = list()
    for row in range(len(matrix)):
        array = [sentimentalCounterOpinionLexicon[0][row], sentimentalCounterNRC[0][row], sentimentalCounterWKWSCI[0][row]]
        arraySentimentalAnalyzed.append(majorityCheck(array))


    # TODO - precisa melhorar a precisão, pois numa notícia onde fala que o brasil atingiu 600k de mortes, está dando como positiva
    result = []
    for row in range(len(matrix)):
        array = [row, matrix[row][0][0], matrix[row][0][2], arraySentimentalAnalyzed[row]]
        result.append(array)

    return result

def sentimentCount(sentence, pos_list, neg_list):
    """

    :param sentence:
    :param pos_list:
    :param neg_list:
    :return:
    """
    sent = 0
    words = [word for word in tokenizer.tokenize(sentence)]

    for word in words:
        if word in pos_list:
            sent += 1
        elif word in neg_list:
            sent -= 1

    return sent

def plotWordCloud(matrix, language,name):
    """

    :param matrix:
    :param language:
    :return:
    """
    SUMMARY = 1

    if language == 'pt':
        wc = WordCloud(width=800, height=400, max_words=200, stopwords=stopwordsPortuguese)
    elif language == 'en':
        wc = WordCloud(width=800, height=400, max_words=200, stopwords=stopwordsEnglish)

    corpus = ""
    for row in range(len(matrix)):
        corpus += " " + matrix[row][SUMMARY]

    wc.generate(corpus)
    # plt.figure(figsize=(30, 30))
    # plt.imshow(wc)
    # plt.axis('off')
    # # plt.show()
    wc.to_file(name)

def twitterTrendCollection(woeid):
    """
    This method returns the trending topics from a region posted on Twitter
    :param woeid:
    :return:
    """
    brazil_trends = api.get_place_trends(woeid)
    trends = json.loads(json.dumps(brazil_trends, indent=1))
    top20TwitterTrends = dict()

    for row in range(20):
        top20TwitterTrends[trends[0]['trends'][row]['name']] = trends[0]['trends'][row]['url']

    return top20TwitterTrends

def collectTweetBasedOnPreferenceAndAnalyze(keyword, language):
    """
    Collect 100 tweets and analyze their context
    :param keyword:
    :param language:
    :return:
    """
    ORIGINALTEXT = 1
    ANALYZEDTEXT = 2
    api = tweepy.API(auth)


    result = api.search_tweets(keyword, lang=language, result_type="mixed",count=50,tweet_mode='extended')

    tweets = []
    for index in range(result.count):
            tweet = [result[index]._json['user']['name'], result[index]._json['full_text'], "",
                     result[index]._json['created_at']]
            tweet[1].encode('utf-8', 'ignore')
            tweets.append(tweet)

    for row in range(result.count):
        tweets[row][ANALYZEDTEXT] = clean_html(tweets[row][ORIGINALTEXT])
        tweets[row][ANALYZEDTEXT] = remove_punctuation(tweets[row][ANALYZEDTEXT])
        tweets[row][ANALYZEDTEXT] = remove_stopwords(tweets[row][ANALYZEDTEXT], language)
        tweets[row][ANALYZEDTEXT] = tweets[row][ANALYZEDTEXT].lower()

    plotWordCloud(tweets, language,"twiter.png")

    return tweets


def cleantext(auxTitle):
    auxTitle = clean_html(auxTitle)
    auxTitle = remove_punctuation(auxTitle)
    auxTitle = remove_stopwords(auxTitle)
    auxTitle = auxTitle.lower()
    nltk.stem

    words = [word for word in tokenizer.tokenize(auxTitle)]
    return words


def updateUsers_db(newsNumbers, user, category):
    filename = user + "_tempNews.json"
    data_folder = Path("database/")
    userNews_db_file = data_folder / filename

    with open(userNews_db_file) as json_file:
        userNewsTemp = json.load(json_file)

    retrievednews = []
    numbers = newsNumbers.split('-')
    for news in numbers:
        try:
            auxTitle = userNewsTemp[int(news)][1]
            textCleaned = cleantext(auxTitle)
            retrievednews.append(textCleaned)
        except:
            print("Error to append tokezined title words")

    filename = "users_db.json"
    data_folder = Path("database/")
    user_db_file = data_folder / filename

    with open(user_db_file) as json_file:
        user_db = json.load(json_file)

    userProfileLoadedTemp = dict()
    for profile in user_db['users']:
        if (profile['id'] == user):
            userProfileLoadedTemp = profile
            break

    if len(userProfileLoadedTemp) < 2:
        newprofile = dict()
        newprofile['id'] = user
        newprofile['words'] = [dict()]
        newprofile['words'][0] = {"positiveWords": {}, "negativeWords": {}}

        for news in retrievednews:
            for word in news:
                if word in newprofile['words'][0][category]:
                    newprofile['words'][0][category][word] += 1
                else:
                    newprofile['words'][0][category][word] = 1
        user_db['users'].append(newprofile)

    else:
        for news in retrievednews:
            for word in news:
                if word in userProfileLoadedTemp['words'][0][category]:
                    userProfileLoadedTemp['words'][0][category][word] += 1
                else:
                    userProfileLoadedTemp['words'][0][category][word] = 1

    user_dbDict = json.dumps(user_db)
    with open(user_db_file, 'w') as f:
        f.write(user_dbDict)

    return None