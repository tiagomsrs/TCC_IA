# import webbrowser
import time, json, os
from api import google_api
from api import news_api
from utils import utils
from flask import Flask, render_template,jsonify
from pathlib import Path

app = Flask(__name__)
PAGE_SIZE = 20

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


@app.route('/searchNews/<temas>/<language>/<user>')
def searchNews(temas, language='en', user='tiagomsrs'):
    # TODO arrumar temas com espaços
    # http://192.168.1.104:5000/searchNews/brasil/pt

    inicio = time.time()
    try:
        googleOutput = google_api.GoogleApi(temas[0], language)
        news_1 = utils.extractorGoogleApi(googleOutput)
    except Exception as e:
        print("Failed to get the news from Google Api")

    try:
        newsOutput = news_api.NewsApi(temas, language, PAGE_SIZE)['articles']
        news_2 = utils.extractorNewsApi(newsOutput)
    except Exception as e:
        print("Failed to get the news from News Api.")

    fim = time.time()
    print("Time spend to search Google e News API:" + str(fim - inicio))

    if news_1 and news_2:
        newsMatrix = utils.youtubeRemoval(news_1 + news_2)

        inicio = time.time()
        completeMatrix = utils.summaryDownload(newsMatrix)
        fim = time.time()
        print("Time spend to download the news summary: " + str(fim - inicio))

        inicio = time.time()
        arraySentimentalAnalyzed = utils.sentimentalAnalyzes(completeMatrix.copy(), language)
        fim = time.time()

        print("Time spend to format the news: " + str(fim - inicio))

        # chrome_path = '/usr/bin/google-chrome %s'
        #
        # for index in range(0, len(completeMatrix), 3):
        #     webbrowser.get(chrome_path).open(completeMatrix[index][0][2])

        # with open('test.txt', 'w') as f:
        #     f.write(str(completeMatrix))
        # f.close()

    filename = user + "_tempNews.json"
    data_folder = Path("database/")
    file_to_open = data_folder / filename

    arraySentimentalAnalyzedDict = json.dumps(arraySentimentalAnalyzed)
    with open(file_to_open, 'w') as f:
        f.write(arraySentimentalAnalyzedDict)

    return jsonify(arraySentimentalAnalyzed)


@app.route('/searchTrendsTwitter/<woeid>')
def searchTrendsTwitter(woeid):
    # http://192.168.1.104:5000/searchTrendsTwitter/brazil
    woeid = str(woeid).lower()
    top20TwitterTrends = utils.twitterTrendCollection(WOIED[woeid])
    return jsonify(top20TwitterTrends)


@app.route('/keywordTwitterSearch/<keyword>/<language>', methods=['GET'])
def keywordTwitterSearch(keyword, language='en'):
    #http://192.168.1.104:5000/keywordTwitterSearch/ps5/pt
    tweets = utils.collectTweetBasedOnPreferenceAndAnalyze(keyword, language)
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
    IP = "192.168.1.104"
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True, host=IP)
