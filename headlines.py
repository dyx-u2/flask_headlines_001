import datetime #for cookie use
import feedparser
from flask import Flask
import json
from flask import make_response #for cookie use
from flask import render_template
from flask import request
#import urllib2 -- combined with urllib in python 3, instead import urlopen from urllib
import urllib
from urllib.request import urlopen


app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
			 'cnn': 'http://rss.cnn.com/rss/edition.rss',
			 'fox': 'http://feeds.foxnews.com/foxnews/latest',
			 'iol': 'http://www.iol.co.za/cmlink/1.640',
			 'nyt': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'
			}

DEFAULTS = {'publication':'nyt',
			'city':'Davao, Philippines',
			'currency_from': 'USD',
			'currency_to': 'PHP'
			}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=fb828c3dad9b90afd8ec20b0613c1c67"

CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=bb679c54049f4d018c4b1e99eb29ea8c"


def get_value_with_fallback(key):
	if request.args.get(key):
		return request.args.get(key)
	if request.cookies.get(key):
		return request.cookies.get(key)
	return DEFAULTS[key]


@app.route("/")

def home():
	# get customized headlines, based on user input or default
	publication = get_value_with_fallback('publication')
	articles = get_news(publication)

	# get customized weather based on user input or default
	city = get_value_with_fallback('city')
	weather = get_weather(city)

	
	# get customized currency based on user input or default
	currency_from = get_value_with_fallback('currency_from')
	currency_to = get_value_with_fallback('currency_to')
	rate, currencies = get_rate(currency_from, currency_to)

	# save cookies and return template
	response = make_response(render_template(
		"home.html",
		articles=articles,
		weather=weather,
		currency_from=currency_from,
		currency_to=currency_to,
		rate=rate,
		currencies=sorted(currencies)))
	expires = datetime.datetime.now() + datetime.timedelta(days=365)
	response.set_cookie("publication", publication, expires=expires)
	response.set_cookie("city", city, expires=expires)
	response.set_cookie("currency_from", currency_from, expires=expires)
	response.set_cookie("currency_to", currency_to, expires=expires)
	return response


def get_news(query):
	# query = request.form.get("publication")   --> if using form
	if not query or query.lower() not in RSS_FEEDS:
		publication = DEFAULTS["publication"]
	else:	
		publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return feed['entries']
	
	# weather = get_weather("Davao, Philippines")

	# return render_template("home.html", 
		# articles=feed['entries'],
		# weather=weather
		# )


def get_weather(query):
	# api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=fb828c3dad9b90afd8ec20b0613c1c67"
	query = urllib.parse.quote(query)  #modified by DYX 
	url = WEATHER_URL.format(query)
	data = urlopen(url).read()
	parsed = json.loads(data) #loads = load string - to convert JSON string into Python dictionary
	weather = None
	if parsed.get("weather"):
		weather = {"description": parsed["weather"][0]["description"],
					"temperature": parsed["main"]["temp"],
					"city": parsed["name"],
					"country": parsed['sys']['country']
		}
	return weather



def get_rate(frm, to):
	all_currency = urlopen(CURRENCY_URL).read()
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate/frm_rate, parsed.keys())




if __name__ == "__main__":
	app.run(port=5000, debug=True)
