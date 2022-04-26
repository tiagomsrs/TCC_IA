from GoogleNews import GoogleNews
import pandas as pd
from utils import utils


def GoogleApi (temas, lang):
    '''
    Optional choose custom day range (mm/dd/yyyy)

    :param this:
    :param temas:
    :return:
    '''

    [actualDate, previusDate] = utils.dateFormatGoogleApi()

    googlenews = GoogleNews(lang=lang, period='30d', encode='utf-8')

    googlenews.search(temas)
    result = googlenews.results(sort=True)
    googlenews.get_page(2)

    return result



