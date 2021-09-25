from api import google_api
from api import news_api
from utils import utils
import nltk



if __name__ == "__main__":

    # nltk.download('punkt')

    print('Entre com a quantidade de temas: ')
    countTema = int(input())
    temas = list()
    while (countTema > 0):
        temas.append(str(input()))
        countTema -= 1

    try:
        googleOutput = google_api.GoogleApi(temas[0])
    except (RuntimeError, TypeError, NameError):
        print("Failed to get the news from Google Api")
    finally:
        news_1 = utils.extractorGoogleApi (googleOutput)

    try:
        newsOutput = news_api.NewsApi(temas)['articles']
    except (RuntimeError, TypeError, NameError):
        print("Failed to get the news from News Api")
    finally:
        news_2 = utils.extractorNewsApi(newsOutput)


    newsMatrix = utils.youtubeRemoval(news_1 + news_2)
    completeMatrix = utils.summaryDownload(newsMatrix)
    print('a')

    # with open('test.txt', 'w') as f:
    #     f.write(str(np[1]['content']))
    # f.close()

