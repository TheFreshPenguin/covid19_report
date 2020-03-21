import pandas as pd
import io
import requests
from datetime import date, datetime
import flag
import tweepy
from country_isos import country_isos


def get_secrets():
    file = open("secrets.txt", "r")
    return file.read().split('\n')


def emoji_face(new_cases_number):
    emoji_sick_faces = {5000: '🤮', 2500: '🤢', 1000: '😷', 500: '🤒'}

    for key in emoji_sick_faces:
        if new_cases_number >= key:
            return emoji_sick_faces[key]
    return '🥺'


file1 = open("registered_date.txt", "r")
registered__date = file1.read()
file1.close()

url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
      "/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
s = requests.get(url).content
confirmed = pd.read_csv(io.StringIO(s.decode('utf-8')))
last_update_day = datetime.strptime(confirmed.columns[-1], "%m/%d/%y").date()

if last_update_day != datetime.strptime(registered__date, "%Y-%m-%d").date():

    total_countries = confirmed.groupby("Country/Region").sum()
    two_last_days = total_countries[total_countries.columns[-2:]]
    new_cases = two_last_days[two_last_days.columns[-1]] - two_last_days[two_last_days.columns[-2]]
    top_five_countries = new_cases.sort_values(ascending=False).head(5)

    tweet = "{} // COVID-19 NEW CASES TOP 5 COUNTRIES REPORT\n\n".format(last_update_day)
    i = 1
    for items in top_five_countries.iteritems():
        country = items[0]
        new_cases_number = items[1]
        total = total_countries[total_countries.columns[-1]][country]

        tweet += "{}. {} : +{} {}  +{}% (total: {})\n".format(i,
                                                              flag.flag(country_isos[country]),
                                                              new_cases_number,
                                                              emoji_face(new_cases_number),
                                                              round(
                                                                  100 * (new_cases_number / (total - new_cases_number)),
                                                                  1),
                                                              total
                                                              )
        i = i + 1

    secrets = get_secrets()
    auth = tweepy.OAuthHandler(secrets[0], secrets[1])
    auth.set_access_token(secrets[2], secrets[3])

    api = tweepy.API(auth)
    api.update_status(tweet)

    file1 = open("registered__date.txt", "w")
    file1.write(str(last_update_day))
    file1.close()