# import webbrowser
import time
from api import google_api
from api import news_api
from utils import utils
from flask import Flask, render_template,jsonify


app = Flask(__name__)
PAGE_SIZE = 20

WOIED = {
        "brazil": 23424768,
        "sweden": 23424954,
        "usa": 23424977,
        "world": 1,
        "argentina": 23424747
}

# use decorators to link the function to a url
@app.route('/')
def index():
    # http://192.168.1.23:5000/
    return render_template('index.html')


@app.route('/searchNews/<temas>/<language>')
def searchNews(temas, language='en'):
    # TODO arrumar temas com espaços
    # http://192.168.1.23:5000/searchNews/brasil/pt

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

    return jsonify(arraySentimentalAnalyzed)


@app.route('/searchTrendsTwitter/<woeid>')
def searchTrendsTwitter(woeid):
    # http://192.168.1.23:5000/searchTrendsTwitter/brazil
    top20TwitterTrends = utils.twitterTrendCollection(WOIED[woeid])
    return jsonify(top20TwitterTrends)


@app.route('/keywordTwitterSearch/<keyword>/<language>', methods=['GET'])
def keywordTwitterSearch(keyword, language='en'):
    #http://192.168.1.23:5000/keywordTwitterSearch/ps5/pt
    tweets = utils.collectTweetBasedOnPreferenceAndAnalyze(keyword, language)
    return jsonify(tweets)


if __name__ == "__main__":
    app.run(debug=True, host='192.168.1.23')



