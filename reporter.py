import pandas as pd
import io
import requests
from datetime import datetime
import flag
import tweepy
from country_isos import country_isos


def get_secrets():
    file = open("secrets.txt", "r")
    return file.read().split('\n')

url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

# retrieve dataframe
s = requests.get(url).content
confirmed = pd.read_csv(io.StringIO(s.decode('utf-8')))

# read the last update date
last_update_day = datetime.strptime(confirmed.columns[-1], "%m/%d/%y").date()

# group by countries and sum up all provinces
total_countries = confirmed.groupby("Country/Region").sum()

# compute the new cases since the day before
two_last_days = total_countries[total_countries.columns[-2:]]
new_cases = two_last_days[two_last_days.columns[-1]] - two_last_days[two_last_days.columns[-2]]

# get 5 worst countries
top_five_countries = new_cases.sort_values(ascending=False).head(5)

# build a tweet from scratch
tweet = "{} // #COVIDー19 NEW CASES TOP 5 COUNTRIES\n\n".format(last_update_day)
i = 1
for items in top_five_countries.iteritems():
    country = items[0]
    new_cases_number = items[1]
    total = total_countries[total_countries.columns[-1]][country]

    tweet += "{}. {} : +{} {}  +{}% (total: {})\n".format(i,
                                                          flag.flag(country_isos[country]),
                                                          new_cases_number,
                                                          '🔺',
                                                          round(
                                                              100 * (new_cases_number / (total - new_cases_number)),
                                                              1),
                                                          total
                                                          )
    i = i + 1

tweet += "\n#coronavirus"

# authenticate on twitter
secrets = get_secrets()
auth = tweepy.OAuthHandler(secrets[0], secrets[1])
auth.set_access_token(secrets[2], secrets[3])

# send final tweet
api = tweepy.API(auth)
api.update_status(tweet)
