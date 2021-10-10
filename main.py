from api import google_api
from api import news_api
from utils import utils
import time
import webbrowser
import nltk



if __name__ == "__main__":
    language = 'en'
    page_size = 20

    print('Entre com a quantidade de temas: ')
    # countTema = int(input())
    temas = list()
    #
    # while (countTema > 0):
    #     temas.append(str(input()))
    #     countTema -= 1

    temas.append("brazil")

    inicio = time.time()

    try:
        googleOutput = google_api.GoogleApi(temas[0], language)
        news_1 = utils.extractorGoogleApi(googleOutput)
    except:
        print("Failed to get the news from Google Api")

    try:
        newsOutput = news_api.NewsApi(temas, language, page_size)['articles']
        news_2 = utils.extractorNewsApi(newsOutput)
    except:
        print("Failed to get the news from News Api")

    fim = time.time()
    print("Time spend to search Google e News API:" + str(fim - inicio))


    if news_1 and news_2:

        newsMatrix = utils.youtubeRemoval(news_1 + news_2)

        inicio = time.time()
        completeMatrix = utils.summaryDownload(newsMatrix)
        fim = time.time()
        print("Time spend to download the news summary: " + str(fim - inicio))

        inicio = time.time()
        completeMatrix = utils.sentimentalAnalyzes(completeMatrix.copy(), language)
        fim = time.time()

        print("Time spend to format the news: " + str(fim - inicio))


        # chrome_path = '/usr/bin/google-chrome %s'
        #
        # for index in range(0, len(completeMatrix), 3):
        #     webbrowser.get(chrome_path).open(completeMatrix[index][0][2])

        # with open('test.txt', 'w') as f:
        #     f.write(str(completeMatrix))
        # f.close()

