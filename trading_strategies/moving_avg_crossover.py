from datetime import datetime, timedelta
import math
from app import *
import time

class MovingAverageCrossoverTrading:
    def __init__(self,symbol,quantity,sma_fast,sma_slow,run_time_in_min):
        self.__symbol = symbol
        self.__quantity = quantity
        self.__sma_fast = sma_fast
        self.__sma_slow = sma_slow
        self.__run_time_in_min = run_time_in_min

    # we run the loop every 60 seconds because we are trading with 1 min data, in order to get the most recent 1 min bar as soon as it is available to us.
    def get_pause(self):
        now = datetime.datetime.now()
        next_min = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        pause = math.ceil((next_min - now).seconds)
        App().log(f"Sleep for {pause}")
        return pause

    # Check our current position
    def get_position(self):
        positions = App().tradeapi.list_positions()
        for p in positions:
            if p.symbol == self.__symbol:
                return float(p.qty)
        return 0

    # Returns a series with the moving average
    def get_sma(self,series, periods):
        return series.rolling(periods).mean()

    # Checks whether we should buy (fast ma > slow ma)
    def get_signal(self,fast, slow):
        App().log(f"Fast {fast[-1]}  /  Slow: {slow[-1]}")
        return fast[-1] > slow[-1]

    # Get up-to-date 1 minute data from Alpaca and add the moving averages
    def get_bars(self):
        bars = App().tradeapi.get_crypto_bars(self.__symbol, TimeFrame.Minute).df
        bars = bars[bars.exchange == 'CBSE']
        bars[f'sma_fast'] = self.get_sma(bars.close, self.__sma_fast)
        bars[f'sma_slow'] = self.get_sma(bars.close, self.__sma_slow)
        return bars

    def executeTradeStrategy(self):
        App().log(f"------ Executing Moving Avg Crossover Trading Strategy with {self.__symbol}, quantity: {self.__quantity}, run time: {self.__run_time_in_min} mins ----------- ")
        timeout = time.time() + 60*self.__run_time_in_min  # set timeout to current time plus the user provided run time in mins
        transaction_details = []
        while True:
            # GET DATA
            bars = self.get_bars()
            # CHECK POSITIONS
            position = self.get_position()
            should_buy = self.get_signal(bars.sma_fast,bars.sma_slow)
            App().log(f"Position: {position} / Should Buy: {should_buy}")

            if position == 0 and should_buy == True:
                # WE BUY THE SECURITY
                buyorder=App().tradeapi.submit_order(self.__symbol, qty=self.__quantity, side='buy')
                time.sleep(4)
                getorder=App().tradeapi.get_order_by_client_order_id(buyorder.client_order_id)
                App().log(f'BOUGHT {self.__quantity} {self.__symbol}')
                App().log(f'Symbol: {self.__symbol} / Side: BUY / Quantity: {self.__quantity} / Price: ${getorder.filled_avg_price}')
                transaction_details.append({"order_side":getorder.side,"filled_qty":getorder.filled_qty,"filled_avg_price":getorder.filled_avg_price,"filled_at":str(getorder.filled_at)})
            
            elif position > 0 and should_buy == False:
                # WE SELL THE SECURITY
                sellorder=App().tradeapi.submit_order(self.__symbol, qty=self.__quantity, side='sell')
                time.sleep(4)
                getorder=App().tradeapi.get_order_by_client_order_id(sellorder.client_order_id)
                App().log(f'SOLD {self.__quantity} {self.__symbol}')
                App().log(f'Symbol: {self.__symbol} / Side: SELL / Quantity: {self.__quantity} / Price: ${getorder.filled_avg_price}')
                transaction_details.append({"order_side":getorder.side,"filled_qty":getorder.filled_qty,"filled_avg_price":getorder.filled_avg_price,"filled_at":str(getorder.filled_at)})
            
            time.sleep(self.get_pause())
            App().log("*"*20)
            if time.time() > timeout:
                break
        return transaction_details

# print(MovingAverageCrossoverTrading('ETHUSD',1,12,24,3).executeTradeStrategy())