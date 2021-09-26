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

    googlenews = GoogleNews(lang=lang, start=previusDate ,end=actualDate)
    # goooglenews = GoogleNews(period='d')
    googlenews.set_lang('en')
    googlenews.search(temas)

    result = googlenews.result()
    df = pd.DataFrame(result)

    return df



