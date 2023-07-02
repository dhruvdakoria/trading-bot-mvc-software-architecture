from app import *
import random
import time

class CoinTossTrading:
    def __init__(self,symbol,quantity,max_sells):
        self.__symbol = symbol
        self.__quantity = quantity
        self.__maxsells = max_sells
        self.__soldcounter = 0

    # Check our current position
    def get_position(self):
        positions = App().tradeapi.list_positions()
        for p in positions:
            if p.symbol == self.__symbol:
                return float(p.qty)
        return 0

    # execute trade strategy coin toss
    def executeTradeStrategy(self):
        App().log(f"------ Executing Coin Toss Trading Strategy with {self.__symbol}, quantity: {self.__quantity}, max buy&sell transations: {self.__maxsells} ----------- ")
        transaction_details = []
        while True and self.__soldcounter < self.__maxsells:
            # GET OUR CURRENT POSITION
            position = self.get_position()
            # price = api.get_latest_quote(SYMBOL)
            # print(f"BTC Latest Price => {price}")
            
            # RANDOMLY CHECK IF WE SHOULD BUY OR SELL
            almighty_says_buy = random.choice([True, False])
            App().log(f"Holding: {position} / Buy: {almighty_says_buy}")

            # CHECK IF WE SHOULD BUY
            if position == 0 and almighty_says_buy == True:
                # WE BUY ONE SECURITY
                App().log('The almighty has decided:')
                buyorder=App().tradeapi.submit_order(self.__symbol, qty=self.__quantity, side='buy')
                time.sleep(4)
                getorder=App().tradeapi.get_order_by_client_order_id(buyorder.client_order_id)
                transaction_details.append({"order_side":getorder.side,"filled_qty":getorder.filled_qty,"filled_avg_price":getorder.filled_avg_price,"filled_at":str(getorder.filled_at)})
                App().log(f'Symbol: {self.__symbol} / Side: BUY / Quantity: {self.__quantity} / Price: ${getorder.filled_avg_price}')
            
            # CHECK IF WE SHOULD SELL
            elif position > 0 and almighty_says_buy == False:
                # WE SELL ONE SECURITY
                App().log('The almighty has decided:')
                sellorder=App().tradeapi.submit_order(self.__symbol, qty=self.__quantity, side='sell')
                time.sleep(4)
                getorder=App().tradeapi.get_order_by_client_order_id(sellorder.client_order_id)
                transaction_details.append({"order_side":getorder.side,"filled_qty":getorder.filled_qty,"filled_avg_price":getorder.filled_avg_price,"filled_at":str(getorder.filled_at)})
                App().log(f'Symbol: {self.__symbol} / Side: SELL / Quantity: {self.__quantity} / Price: ${getorder.filled_avg_price}')
                self.__soldcounter+=1

            App().log('Lets wait for the 8s before next decision...')
            App().log("*"*20)
            time.sleep(8)
        return transaction_details

# cointoss = CoinTossTrading('BTCUSD',2,2)
# print(cointoss.executeCoinToss())