from api import google_api
from api import news_api
from utils import utils
import webbrowser
import nltk



if __name__ == "__main__":
    language = 'en'
    page_size = 20

    print('Entre com a quantidade de temas: ')
    countTema = int(input())
    temas = list()

    while (countTema > 0):
        temas.append(str(input()))
        countTema -= 1

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


    if news_1 and news_2:

        newsMatrix = utils.youtubeRemoval(news_1 + news_2)
        completeMatrix = utils.summaryDownload(newsMatrix)

        completeMatrix = utils.sentimentalAnalyzes(completeMatrix.copy(), language)

        print('a')
        # chrome_path = '/usr/bin/google-chrome %s'
        #
        # for index in range(0, len(completeMatrix), 3):
        #     webbrowser.get(chrome_path).open(completeMatrix[index][0][2])

        # with open('test.txt', 'w') as f:
        #     f.write(str(completeMatrix))
        # f.close()

