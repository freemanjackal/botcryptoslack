# About botcryptoslack
This is a slack bot that provide specific information about crypto markets.

## Functionalities
* Get the latest prices of 5 cryptocurrencies (BTC, ETH, LTC, BCH,  XTZ)
* Get news related to crypto market
* Make conversion of a specific amount of any cryptocurrency(listed in [coinmarketcap](https://coinmarketcap.com)) to USD.

## Crypto bot commands
The commands used by cryptobot are not slack commands. They work by mentioning the bot followed by specific keywords.

### Commands:
1.     @crypto_bot help 
2.     @crypto_bot prices
3.     @crypto_bot convert [ammount] [ccoin-symbol] 
  Examples:
  
    @crypto_bot convert 0.1
    
    @crypto_bot convert 0.1 btc
    
Those 2 commands are equivalent because btc is the default crypto symbol

    @crypto_bot convert 2.3 eth
Where amount is the specified amount of any coin to USD.  ccoin-symbol is an optional parameter where btc is the default value.

4.     @crypto_bot news 
Return 10 top news from messari.io related to cryptos

## Future commands
Add options like crypto predictions.


