import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
#coinmarketcap api
APP_KEY = '82fd1700-ce10-4e16-8961-8b1ac00867d6'

#price convertions
#latest prices of best 5
#news cryptos from messari
#sentiment or prediction





def get_latest_prices():
	url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
	parameters = {
	  'symbol':'BTC,ETH,LTC,XTZ,BCH'
	}
	headers = {
	  'Accepts': 'application/json',
	  'X-CMC_PRO_API_KEY': APP_KEY,
	}
	session = Session()
	session.headers.update(headers)

	try:
	  response = session.get(url, params=parameters)
	  data = json.loads(response.text)
	  return data
	except (ConnectionError, Timeout, TooManyRedirects) as e:
	  print(e)

def convert_to(btc_qty, crypto='btc'):
	url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
	parameters = {
	  'symbol':crypto, #btc default
	  'amount': btc_qty,
	  'convert':'USD'
	}
	headers = {
	  'Accepts': 'application/json',
	  'X-CMC_PRO_API_KEY': APP_KEY,
	}

	session = Session()
	session.headers.update(headers)

	try:
	  response = session.get(url, params=parameters)
	  data = json.loads(response.text)
	  return data
	except (ConnectionError, Timeout, TooManyRedirects) as e:
	  print(e)

def get_news():
	url = "https://data.messari.io/api/v1/news?as-markdown"
	session = Session()
	try:
		response = session.get(url)
		data = json.loads(response.text)
		return data
	except(ConnectionError, Timeout, TooManyRedirects) as e:
		print(e)



# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])


def start(user_id: str, channel: str, msg):

	if msg["type"] == "block":
		response = slack_web_client.chat_postMessage(channel=channel,user=user_id, blocks=msg["text"])	
	else:
		response = slack_web_client.chat_postMessage(channel=channel,user=user_id, text=msg["text"])




DIVIDER_BLOCK = {"type": "divider"}

def _get_block(text, information):
		return [
			{"type": "section", "text": {"type": "mrkdwn", "text": text}},
			{"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
		]

def convertPrices2Msgs(data):
	data = data['data']
	sections = []

	for (k,v) in data.items():
		price = v["quote"]["USD"]["price"]
		blocks = _get_block(k, "Price: " + str(price))
		sections.append(blocks[0])
		sections.append(blocks[1])
		sections.append(DIVIDER_BLOCK)
	return sections

def convertCryptoSell2Msgs(data):
	data = data['data']
	sections = []

	value = data["quote"]["USD"]["price"]
	blocks = _get_block(str(data['amount']) + ' ' + data['symbol'], "Converted value in USD: " + str(value))
	sections.append(blocks[0])
	sections.append(blocks[1])
	sections.append(DIVIDER_BLOCK)
	return sections

def convertNews2Msgs(data):
	#data = json.loads(data)
	data = data['data']
	sections = []

	cont = 0
	for elem in data:
		blocks = _get_block( elem['title'], elem['url'])
		sections.append(blocks[0])
		sections.append(blocks[1])
		sections.append(DIVIDER_BLOCK)
		cont = cont + 1
		if cont >= 10:
			return sections
	return sections

def prediction():
	sections = []
	blocks = _get_block( "Top predictions", "<https://cryptoindex.com/predictions-widget.html|Overlook Hotel> ")
	sections.append(blocks[0])
	sections.append(blocks[1])
	sections.append(DIVIDER_BLOCK)
	return sections	

def help():
	sections = []
	blocks = _get_block( "CRYPTO BOT HELP", "Commands... ")
	sections.append(blocks[0])
	sections.append(blocks[1])
	sections.append(DIVIDER_BLOCK)
	blocks = _get_block( "Get crypto prices(BTC, ETH, LTC, BCH, XTZ)", "COMMAND: @crypto_bot prices")
	sections.append(blocks[0])
	sections.append(blocks[1])
	sections.append(DIVIDER_BLOCK)
	blocks = _get_block( "Convert any crypto amount to USD ", "COMMAND: @crypto_bot convert amount crypto ...\n amount=float value \n crypto=btc | eth | bch | ltc | xtz")
	sections.append(blocks[0])
	sections.append(blocks[1])
	sections.append(DIVIDER_BLOCK)
	blocks = _get_block( "Get crypto news related", "COMMAND: @crypto_bot news")
	sections.append(blocks[0])
	sections.append(blocks[1])
	sections.append(DIVIDER_BLOCK)
	blocks = _get_block( "Get crypto prediction", "Coming soon...")
	sections.append(blocks[0])
	sections.append(blocks[1])
	sections.append(DIVIDER_BLOCK)
	return sections	

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on("app_mention")
def message(payload):
	"""Display the onboarding welcome message after receiving a message
	that contains "start".
	"""
	event = payload.get("event", {})

	channel_id = event.get("channel")
	user_id = event.get("user")
	text = event.get("text")

	text = text.split()
	if text and text[1].lower() == "prices":
		data = get_latest_prices()
		text = convertPrices2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(user_id, channel_id, msg)

	if text and text[1].lower() == "convert":
		if len(text) == 4:
			crypto = text[3].lower()
			data = convert_to(float(text[2]),crypto=crypto)
		else:
			data = convert_to(float(text[2]))

		text = convertCryptoSell2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(user_id, channel_id, msg)
	if text and text[1].lower() == "news":
		data = get_news()
		text = convertNews2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(user_id, channel_id, msg)
	if text and text[1].lower() == "prediction":
		text = prediction()
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(user_id, channel_id, msg)

	if text and text[1].lower() == "help":
		text = help()
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(user_id, channel_id, msg)


if __name__ == "__main__":
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	logger.addHandler(logging.StreamHandler())
	ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
	app.run(port=3000)

"""
	{"status":
	{"timestamp":"2020-04-03T13:58:21.699Z","error_code":0,"error_message":null,"elapsed":13,"credit_count":1,"notice":null},
	"data":{
	"BCH":
	{"id":1831,"name":"Bitcoin Cash","symbol":"BCH","slug":"bitcoin-cash","num_market_pairs":461,"date_added":"2017-07-23T00:00:00.000Z",
				"tags":["mineable"],"max_supply":21000000,"circulating_supply":18365987.5,"total_supply":18365987.5,"platform":null,
				"cmc_rank":5,"last_updated":"2020-04-03T13:56:11.000Z","quote":{"USD":{"price":238.512892754,"volume_24h":4494823424.9577,
				"percent_change_1h":0.0790175,"percent_change_24h":4.86678,"percent_change_7d":5.69708,"market_cap":4380524806.9088,
				"last_updated":"2020-04-03T13:56:11.000Z"}}},
	"BTC":{"id":1,"name":"Bitcoin","symbol":"BTC","slug":"bitcoin",
				"num_market_pairs":7702,"date_added":"2013-04-28T00:00:00.000Z","tags":["mineable"],"max_supply":21000000,"circulating_supply":18302800,
				"total_supply":18302800,"platform":null,"cmc_rank":1,"last_updated":"2020-04-03T13:56:45.000Z","quote":{"USD":{"price":6905.93516821,"volume_24h":48861554826.4,"percent_change_1h":-0.249839,"percent_change_24h":3.38696,"percent_change_7d":3.59389,"market_cap":126397950196.71,"last_updated":"2020-04-03T13:56:45.000Z"}}},"ETH":{"id":1027,"name":"Ethereum","symbol":"ETH","slug":"ethereum","num_market_pairs":5037,"date_added":"2015-08-07T00:00:00.000Z","tags":["mineable"],"max_supply":null,"circulating_supply":110365224.249,"total_supply":110365224.249,"platform":null,"cmc_rank":2,"last_updated":"2020-04-03T13:56:26.000Z","quote":{"USD":{"price":145.037264106,"volume_24h":16025879258.027,"percent_change_1h":-0.134818,"percent_change_24h":5.05074,"percent_change_7d":5.96982,"market_cap":16007070177.52,"last_updated":"2020-04-03T13:56:26.000Z"}}},"LTC":{"id":2,"name":"Litecoin","symbol":"LTC","slug":"litecoin","num_market_pairs":570,"date_added":"2013-04-28T00:00:00.000Z","tags":["mineable"],"max_supply":84000000,"circulating_supply":64426280.703129,"total_supply":64426280.703129,"platform":null,"cmc_rank":7,"last_updated":"2020-04-03T13:56:07.000Z","quote":{"USD":{"price":40.7790846848,"volume_24h":3951019981.9072,"percent_change_1h":-0.0656214,"percent_change_24h":2.99945,"percent_change_7d":2.49477,"market_cap":2627244756.7196,"last_updated":"2020-04-03T13:56:07.000Z"}}},"XTZ":{"id":2011,"name":"Tezos","symbol":"XTZ","slug":"tezos","num_market_pairs":74,"date_added":"2017-10-06T00:00:00.000Z","tags":[],"max_supply":null,"circulating_supply":705020740.06349,"total_supply":705020740.06349,"platform":null,"cmc_rank":10,"last_updated":"2020-04-03T13:56:08.000Z","quote":{"USD":{"price":1.7282971936,"volume_24h":141095250.79035,"percent_change_1h":-0.982121,"percent_change_24h":2.10399,"percent_change_7d":0.883684,"market_cap":1218485366.4815,"last_updated":"2020-04-03T13:56:08.000Z"}}}}}
"""	