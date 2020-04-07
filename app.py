import os
import logging
from flask import Flask, request
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import model
#coinmarketcap api

#price convertions
#latest prices of best 5
#news cryptos from messari
#sentiment or prediction

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)


#dictionary to memory save tokens
tokens = {}


client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = ", ".join(["chat:write", "channels:read", "channels:join", "app_mentions:read", "chat:write.customize", "im:history"])

#auth request

@app.route("/begin_auth", methods=["GET"])
def pre_install():
	return f'<a href="https://slack.com/oauth/v2/authorize?client_id=1034315777795.1044752003316&scope=chat:write,channels:join,commands,im:history,im:write,app_mentions:read,channels:history"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x"></a>'

@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
  # Retrieve the auth code from the request params
	global tokens
	auth_code = request.args['code']

  # An empty string is a valid token for this request
	client = WebClient(token="")

  # Request the auth tokens from Slack
	response = client.oauth_v2_access(
		client_id=os.environ["SLACK_CLIENT_ID"],
		client_secret=os.environ["SLACK_CLIENT_SECRET"],
		code=auth_code
	)

	# Save the bot token to an environmental variable or to your data store
	# for later use
	model.insert_token(response['team']["id"], response['access_token'])
	#tokens[response['team']["id"]] = response['access_token']


	# Don't forget to let the user know that auth has succeeded!
	return "Authorization complete!"

"""
slash commands functions
"""
@app.route("/slash_commands", methods=["GET", "POST"])
def slash_commands():
	 text = request.args['text']
	 team_id = request.args['team_id']
	 channel = request.args['channel']
	 user_id = request.args['user_id']
	 command = request.args['command']

	 text = text.split()

	 if text and text[1].lower() == "/crypto_prices":
		data = get_latest_prices()
		text = convertPrices2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)

	if command == "/crypto_convert":
		if len(text) == 2:
			crypto = text[1].lower()
			data = convert_to(float(text[0]),crypto=crypto)
		else:
			data = convert_to(float(text[0]))

		text = convertCryptoSell2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)
	if command == "/crypto_news":
		data = get_news()
		text = convertNews2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)
	if command == "/crypto_prediction":
		text = prediction()
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)

	if command == "/crypto_bot_help":
		text = help()
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)
	 
	 	text = comand + " " + text
	 	msgs(text, team_id,  user_id, channel)
	


headers = {
	  'Accepts': 'application/json',
	  'X-CMC_PRO_API_KEY': os.environ['APP_KEY_COINM_API'],
	  'Content-Type': 'application/json'
	}

def get_latest_prices():
	url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
	parameters = {
	  'symbol':'BTC,ETH,LTC,XTZ,BCH'
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








def start(team_id: str, user_id: str, channel: str, msg):
	# Initialize a Web API client
	#slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
	token = model.get_token(team_id)
	slack_web_client = WebClient(token)

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
	blocks = _get_block( "Top predictions", "<https://cryptoindex.com/predictions-widget.html|Overlook> ")
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
	blocks = _get_block( "Slack commands", "Coming soon...")
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

	team_id = payload.get("team_id")

	channel_id = event.get("channel")
	user_id = event.get("user")
	text = event.get("text")
	text = text.split()
	msgs(text, team_id, user_id, channel_id)

def msgs(text, team_id, user_id, channel_id):
	if text and text[1].lower() == "prices":
		data = get_latest_prices()
		text = convertPrices2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)

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
		return start(team_id, user_id, channel_id, msg)
	if text and text[1].lower() == "news":
		data = get_news()
		text = convertNews2Msgs(data)
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)
	if text and text[1].lower() == "prediction":
		text = prediction()
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)

	if text and text[1].lower() == "help":
		text = help()
		msg = {}
		msg["type"] = "block"
		msg["text"] = text
		return start(team_id, user_id, channel_id, msg)


@slack_events_adapter.on("message")
def message_priv(payload):
	event = payload.get("event", {})

	if event.get("channel_type") == "im":
		team_id = payload.get("team_id")
		channel_id = event.get("channel")
		user_id = event.get("user")
		text = event.get("text")
		text = text.split()
		msgs(text, team_id, user_id, channel_id)


if __name__ == "__main__":
	logger = logging.getLogger()
	os.environ['DATABASE_URL'] = 'localhost:5432@postgres'
	logger.setLevel(logging.DEBUG)
	logger.addHandler(logging.StreamHandler())
	ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
	app.run(port=3000)
	