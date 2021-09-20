from datetime import date, time, datetime

def dateFormatGoogleApi ():
    '''

    :return: Current and Previous date formated as string
    '''

    currentDate = str(date.today()).split('-')

    currentMonth = int(currentDate[1])
    lastMonth = currentMonth - 1
    currentDay = int(currentDate[2])
    currentYear = int(currentDate[0])

    if (lastMonth <= 0):
        lastMonth = 12
        currentYear = currentYear - 1

    if (currentDay <= 9 and currentDay >= 1):
        currentDay = '0' + str(currentDay)
    else:
        currentDay = str(currentDay)

    if (currentMonth <= 9 and currentMonth >= 1):
        currentMonth = '0' + str(currentMonth)
    else:
        currentMonth = str(currentMonth)

    if (lastMonth <= 9 and lastMonth >= 1):
        lastMonth = '0' + str(lastMonth)
    else:
        lastMonth = str(lastMonth)

    currentYear = str(currentYear)
    currentDateFormated = currentMonth + '-' + currentDay + '-' + currentYear
    lastDateFormated = lastMonth + '-' + currentDay + '-' + currentYear

    return currentDateFormated, lastDateFormated

def dateFormatNewsApi ():
    '''

    :return: Current and Previous date formated as string
    '''

    currentDate = str(date.today()).split('-')

    currentMonth = int(currentDate[1])
    lastMonth = currentMonth - 1
    currentDay = int(currentDate[2]) + 1
    currentYear = int(currentDate[0])

    if (lastMonth <= 0):
        lastMonth = '12'
        currentYear = currentYear - 1

    if (currentDay > 30):
        currentDay = '01'
        lastMonth += 1
    elif (currentDay <= 9 and currentDay >= 1 ):
        currentDay = '0' + str(currentDay)
    else:
        currentDay = str(currentDay)

    if (lastMonth <= 9 and lastMonth >= 1):
        lastMonth = '0' + str(lastMonth)
    else:
        lastMonth = str(lastMonth)

    currentYear = str(currentYear)


    lastDateFormated = currentYear + '-' + lastMonth + '-' + currentDay

    return lastDateFormated