import webbrowser
import time, json, os
from api import google_api
from api import news_api
from utils import utils
from flask import Flask, render_template,jsonify
from pathlib import Path

app = Flask(__name__)

WOIED = {
        "brazil": 23424768,
        "brasil": 23424768,
        "sweden": 23424954,
        "suecia": 23424954,
        "usa": 23424977,
        "world": 1,
        "mundo": 1,
        "argentina": 23424747
}

# use decorators to link the function to a url
@app.route('/')
def index():
    # http://192.168.1.104:5000/
    return render_template('index.html')


@app.route('/searchNews/<temas>/<language>/<user>/<page_size>')
def searchNews(temas, language='en', user='tiagomsrs', page_size=20):
    # TODO arrumar temas com espaços
    # http://192.168.1.104:5000/searchNews/brasil/pt

    inicio = time.time()

    googleOutput = google_api.GoogleApi(temas, language)

    if googleOutput == "":
        print("Failed to get the news from Google Api")
    news_1 = utils.extractorGoogleApi(googleOutput)

    temas_formatted = temas.strip().replace(" ","%20")
    newsOutput = news_api.NewsApi(temas_formatted, language, page_size)
    if newsOutput == "":
        print("Failed to get the news from News Api.")
        return ""

    news_2 = utils.extractorNewsApi(newsOutput)

    fim = time.time()
    print("Time spend to search Google e News API:" + str(fim - inicio))

    if news_1 or news_2:
        newsMatrix = utils.sitesRemoval(news_1 + news_2)

        inicio = time.time()
        completeMatrix = utils.summaryDownload(newsMatrix, page_size, temas, language)
        fim = time.time()
        print("Time spend to download the news summary: " + str(fim - inicio))

        inicio = time.time()
        arraySentimentalAnalyzed, order = utils.sentimentalAnalyzes(completeMatrix.copy(), language, user)
        fim = time.time()

        print("Time spend to format the news: " + str(fim - inicio))

    webbrowser.open('trendwordcloud.png')

    filename = user + "_tempNews.json"
    data_folder = Path("database/")
    file_to_open = data_folder / filename

    arraySentimentalAnalyzedDict = json.dumps(arraySentimentalAnalyzed)
    with open(file_to_open, 'w') as f:
        f.write(arraySentimentalAnalyzedDict)

    orderSorted = sorted(order.items(), key=lambda x: x[1], reverse=True)
    finalArray = list()
    for line in orderSorted:
        finalArray.append(arraySentimentalAnalyzed[line[0]])

    for line in range(len(finalArray)):
        finalArray[line][0] = str("Arrived at position {} and reordered to {}".format(finalArray[line][0], line))
    return jsonify(finalArray)

@app.route('/searchTrendsTwitter/<woeid>')
def searchTrendsTwitter(woeid):
    # http://192.168.1.104:5000/searchTrendsTwitter/brazil
    woeid = str(woeid).lower()
    top20TwitterTrends = utils.twitterTrendCollection(WOIED[woeid])
    return jsonify(top20TwitterTrends)


@app.route('/keywordTwitterSearch/<keyword>/<language>', methods=['GET'])
def keywordTwitterSearch(keyword, language='en'):
    #http://192.168.1.104:5000/keywordTwitterSearch/ps5/pt
    # keyword_formatted = keyword.strip().replace(" ", "%20")
    tweets = utils.collectTweetBasedOnPreferenceAndAnalyze(keyword, language)
    webbrowser.open('twitter.png')
    return jsonify(tweets)


@app.route('/savePositiveNews/<newsNumbers>/<user>', methods=['GET'])
def savePositiveNews(newsNumbers, user):
    #http://192.168.1.104:5000/savePositiveNews/5-6-7-8/tiagomsrs

    category = 'positiveWords'
    utils.updateUsers_db(newsNumbers, user, category)

    return "Database updated with positive words!"

@app.route('/saveNegativeNews/<newsNumbers>/<user>', methods=['GET'])
def saveNegativeNews(newsNumbers, user):
    #http://192.168.1.104:5000/saveNegativeNews/2-13/tiagomsrs

    category = 'negativeWords'
    utils.updateUsers_db(newsNumbers, user, category)

    return "Database updated with negative words!"


@app.route('/recoverLastUserNews/<user>', methods=['GET'])
def recoverLastUserNews(user):
    # http://192.168.1.104:5000/recoverLastUserNews/tiagomsrs
    filename = user + "_tempNews.json"
    data_folder = Path("database/")
    file_to_open = data_folder / filename
    with open(file_to_open) as json_file:
        data = json.load(json_file)

    return jsonify(data)


if __name__ == "__main__":
    IP = "192.168.10.180"
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True, host=IP)
    # git tag -a v1.4 -m "my version 1.4"
    # git push origin v1.4

