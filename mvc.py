################################################################################
# Model-View-Controller pattern
#
# Purpose: The core application functionality is carried out using the MVC pattern, with a view for user interface (terminal), 
# a model for database access, and controller for communication between view and model as well as executing business logic (in this case, report generation).  
# https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller. 
#
# Author: Dhruv Dakoria
# Contact: dakoriad@mcmaster.ca
#
################################################################################

from app import *
from trading_strategies.coin_toss import *
from trading_strategies.moving_avg_crossover import *
from report import *
from time import time

# View provides a User Interface and is responsible for getting user inputs
class View():
    # We used decorator @staticmethod because the methods will not access object instance variables.
    @staticmethod
    def main_page():
        print("----------------------------------")
        print("(1) Create a new trading report")
        print("(2) Print a trading report")
        print("(3) Exit")
        option = input("Enter number to select an option: ")
        return int(option)

    @staticmethod
    def create_report():
        print("----------------------------------")
        print("Enter the data below to create a report!")
        report_name = input("Name: ")
        print("\n\n****************************************\n\nSelect a Trading Strategy: coin-toss, moving-avg-crossover")
        strategy_name = input("Strategy Name: ")
        return report_name, strategy_name

    @staticmethod
    def get_coin_toss_input():
        symbol = input("\nEnter Stock/Crypto symbol for coin toss strategy (like BTCUSD, AAPL, TSLA, ETHUSD): ")
        quantity = input("Enter quantity of shares to trade with at a time: ")
        max_sells = input("Enter number of buy and sell transactions (buy+sell is 1 transaction): ")
        return(symbol,int(quantity),int(max_sells))

    @staticmethod
    def get_ma_crossover_input():
        symbol = input("\nEnter Stock/Crypto symbol for moving avg crossover strategy (like BTCUSD, AAPL, TSLA, ETHUSD): ")
        quantity = input("Enter quantity of shares to trade with at a time: ")
        sma_fast = input("Enter SMA fast (set 12): ")
        sma_slow = input("Enter SMA slow (set 24): ")
        run_time_in_min = input("Enter max run time for the trading strategy in minutes: ")
        return(symbol,int(quantity),int(sma_fast),int(sma_slow),int(run_time_in_min))

    @staticmethod
    def ask_for_retry():
        print("Do you wish to retry the same trading strategy (in case no trades were executed)?")
        print("(1) Retry")
        print("(2) Finish report creation")
        option = input("Enter number to select an option: ")
        return int(option)

    @staticmethod
    def print_report(report_names):
        i = 1
        for report in report_names:
            print("(" + str(i) + ") " + report)
            i = i + 1
        report_id = int(input("Enter number of the report to generate: "))
        output_filename = input("Enter filename for report output: ")
        return report_id, output_filename


# Controller uses the view object to present the UI to the user, and manipulates
# data in the database using the model.  The controller also handles business
# logic such as creating report for the transactions.
class Controller():

    # Controller initialized with a view and model object
    def __init__(self,view, model):
        self.__view = view
        self.__model = model

    # Have the view present main page with options to create/print reports, exit
    def run(self):

        while True:
            option = self.__view.main_page()
            App().log("Selected main page option " + str(option))
            if (option == 1):
                self.__create_report()
            elif (option == 2):
                self.__print_report()
            else:
                print("Goodbye!")
                exit()

    # method to determine and setup the trading strategy object
    def __determine_strategy(self):
        self.report_name, self.strategy_name = self.__view.create_report()
        App().log("Created report: name=" + self.report_name)
        if self.strategy_name == "coin-toss":
            symbol,quantity,max_sells = self.__view.get_coin_toss_input()
            transaction_details_obj=CoinTossTrading(symbol,quantity, max_sells)
            inputarr = [symbol,quantity,max_sells]
        elif self.strategy_name == "moving-avg-crossover":
            symbol,quantity,sma_fast,sma_slow,run_time_in_min = self.__view.get_ma_crossover_input()
            transaction_details_obj=MovingAverageCrossoverTrading(symbol,quantity,sma_fast,sma_slow,run_time_in_min)
            inputarr = [symbol,quantity,sma_fast,sma_slow,run_time_in_min]
        else:
            print("Invalid Strategy Entered. Please retry.")
            quit()
        return self.report_name, self.strategy_name, inputarr, transaction_details_obj

    # create a report based on the determined trading strategy
    def __create_report(self):
        # continue the report gathering data and creation process until user decides to exit the program
        while True:

            # keep asking for search terms, append to the relevant list
            report_name, strategy_name, inputarr, transaction_details_obj = self.__determine_strategy()

            # depending on the object setup based on the trading strategy, execute the trading strategy
            transaction_details=transaction_details_obj.executeTradeStrategy()
            
            # provides option to retry the same trading strategy in case the timer ran out and no trade was executed
            print("\n\nTrading Strategy Execution Completed!")
            inputval = self.__view.ask_for_retry()
            if inputval == 1:
                print("\nContinuing with same trade startegy again\n")
            else:
                self.__model.create_report(report_name, strategy_name, inputarr, transaction_details)
                App().log("Finished created report\n")
                break
        

    # Present the user with a list of all possible reports, ask them to select a report to print and the output filename. 
    # Create the basic transaction report and then write it to the output file.
    def __print_report(self):

        # ask user to select the report to print
        report_names = self.__model.get_report_names()
        report_id, output_filename = self.__view.print_report(report_names)
        App().log("Printing report: name=" + report_names[(report_id - 1)])

        # Measure time to create and print the report and record start time
        start_time = time()

        # get report data using the model and create a basic transaction report
        strategy_name, inputdata, transaction_details = self.__model.get_report_data(report_id,report_names[(report_id - 1)])
        report = BasicTransactionReport(report_names[(report_id - 1)],strategy_name, inputdata, transaction_details)
        
        App().log("Basic transaction report created")

        # output the report
        output_file = open(f"reports/{output_filename}", "w")
        output_file.write(report.report_text())
        output_file.close()

        # Measure time to create and print the report using the end time
        end_time = time()
        total_time = round(end_time - start_time, 4)
        App().log("Report written to file: " + output_filename)
        App().log("Time to generate report: " + str(total_time) + "s")
        print("Report written to file!")


# Model handles interaction with the dynamodb database, used by the controller
class Model():

    # create a record in the dynamodb NoSQL database where report_name is set as primary key and based on the strategy we apply insert the trade data
    def create_report(self, report_name, strategy, inputarr, transaction_details):
        if strategy == 'coin-toss':
            App().dbconn.put_item(
                Item={
                    'report_name': report_name,
                    'strategy_name': strategy,
                    'symbol': inputarr[0],
                    'quantity': inputarr[1],
                    'max_sells': inputarr[2],
                    'transaction_details': str(transaction_details)
                }
            )
        elif strategy == 'moving-avg-crossover':
            App().dbconn.put_item(
                Item={
                    'report_name': report_name,
                    'strategy_name': strategy,
                    'symbol': inputarr[0],
                    'quantity': inputarr[1],
                    'sma_fast': inputarr[2],
                    'sma_slow': inputarr[3],
                    'run_time_in_min': inputarr[4],
                    'transaction_details': str(transaction_details)
                }
            )
        App().log("\n\nReport successfully inserted into database: name=" + report_name)



    # Returns the report names as a list by getting all items from the database
    def get_report_names(self):
        report_names = []
        response = App().dbconn.scan(Select='SPECIFIC_ATTRIBUTES',ProjectionExpression='report_name')
        data = response['Items']

        for d_item in data:
            report_names.append(d_item['report_name'])
        
        App().log("Report names retrieved: " + str(report_names))
        return report_names

    # Returns the report data by quering the DynamoDB database
    def get_report_data(self,report_id,report_name):
        inputdata = []
        response = App().dbconn.get_item(
            Key={'report_name': report_name}
        )['Item']
        App().log("Retrieved report data for report id: " + str(report_id))
        strategy_name = response['strategy_name']
        transaction_details = response['transaction_details']
        symbol = response['symbol']
        quantity = response['quantity']
        if strategy_name == 'coin-toss':
            max_sells = response['max_sells']
            inputdata.extend([symbol,quantity,max_sells])
        elif strategy_name == 'moving-avg-crossover':
            sma_fast = response['sma_fast']
            sma_slow = response['sma_slow']
            run_time_in_min = response['run_time_in_min']
            inputdata.extend([symbol,quantity,sma_fast,sma_slow,run_time_in_min])
        return strategy_name, inputdata, transaction_details