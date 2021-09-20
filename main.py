from api import google_api
from api import news_api
from utils import utils



if __name__ == "__main__":
    print('Entre com a quantidade de temas: ')
    countTema = int(input())
    temas = list()
    while (countTema > 0):
        temas.append(str(input()))
        countTema -= 1

    df = google_api.GoogleApi(temas[0])
    print(df)

    np = news_api.NewsApi(temas)
    print(np)

