################################################################################
# Report generation class
#
# Purpose: The classes in this module allow for reports to be generated. Currently
# report generation is only limited to the Basic Transaction report but can be
# extended using the decorator pattern
# Author: Dhruv Dakoria
# Contact: dakoriad@mcmaster.ca
#
################################################################################

from app import *
import ast


# Creates basic transaction report containing the overview of transactions
class BasicTransactionReport():

    # constructor method
    def __init__(self,report_name,strategy_name, inputdata, transaction_details):
        self.__report_name = report_name
        self.__strategy_name = strategy_name
        self.__inputdata = inputdata
        self.__transaction_details = transaction_details

    # creates text for the report depending on the type of the report
    def create_report_text_string(self):
        report_text = f"Transation Details from trading strategy {self.__strategy_name}\n\n"
        if self.__strategy_name == 'coin-toss':
            report_text += f"Trade Symbol = {self.__inputdata[0]}\nQuantity traded with at a time = {self.__inputdata[1]}\nMax buy and sell combined transactions = {self.__inputdata[2]}\n\n"
        elif self.__strategy_name == 'moving-avg-crossover':
            report_text += f"Trade Symbol = {self.__inputdata[0]}\nQuantity traded with at a time = {self.__inputdata[1]}\nSMA Fast = {self.__inputdata[2]}\nSMA Slow = {self.__inputdata[3]}\nMax Run time = {self.__inputdata[4]}\n\n"
        else:
            report_text += f"Invalid strategy name"
        return report_text

    # Puts strategy and transaction data into report_text string and logs
    def report_text(self):
        App().log(f"Building report {self.__report_name} with strategy name {self.__strategy_name}")
        report_text=self.create_report_text_string()
             
        # convert string representation of list with json to a list with proper json
        App().log("Transaction details", self.__transaction_details)
        upd_transaction_details = ast.literal_eval(self.__transaction_details.replace("\'", "\""))
        
        # loop through transaction details and add to string
        if len(upd_transaction_details) == 0:
            App().log(f"\nNo transaction happended during the period of the report when trading stretgy was executed\n")
        else:
            for i in range(len(upd_transaction_details)):
                report_text += f"-------------- Transaction {i+1} ----------------\n"
                for k, v in upd_transaction_details[i].items():
                    report_text += f"{k} = {v.upper()}\n"
                report_text += "\n\n"

        App().log(f"Report {self.__report_name} with strategy name {self.__strategy_name} created")

        return report_text