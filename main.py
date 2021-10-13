# import webbrowser
import time
from api import google_api
from api import news_api
from utils import utils






if __name__ == "__main__":
    LANGUAGUE = 'en'
    PAGE_SIZE = 20

    print('Entre com a quantidade de temas: ')
    # countTema = int(input())

    temas = ["sweden"]

    # while (countTema > 0):
    #     temas.append(str(input()))
    #     countTema -= 1


    inicio = time.time()

    try:
        googleOutput = google_api.GoogleApi(temas[0], LANGUAGUE)
        news_1 = utils.extractorGoogleApi(googleOutput)
    except Exception as e:
        print("Failed to get the news from Google Api")

    try:
        newsOutput = news_api.NewsApi(temas, LANGUAGUE, PAGE_SIZE)['articles']
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
        arraySentimentalAnalyzed = utils.sentimentalAnalyzes(completeMatrix.copy(), LANGUAGUE)
        fim = time.time()

        print("Time spend to format the news: " + str(fim - inicio))


        # chrome_path = '/usr/bin/google-chrome %s'
        #
        # for index in range(0, len(completeMatrix), 3):
        #     webbrowser.get(chrome_path).open(completeMatrix[index][0][2])

        # with open('test.txt', 'w') as f:
        #     f.write(str(completeMatrix))
        # f.close()

    BRAZIL_WOE_ID = 23424768
    SWEDEN_WOE_ID = 23424954
    USA_WOE_ID = 23424977
    WORLD_WOE_ID = 1
    ARGENTINA_WOE_ID = 23424747

    woeid = ARGENTINA_WOE_ID

    top20TwitterTrends = utils.twitterTrendCollection(woeid)

    for key, value in top20TwitterTrends.items():
        tweets = utils.collectTweetBasedOnPreferenceAndAnalyze(key, LANGUAGUE)
        break


    print(top20TwitterTrends)
