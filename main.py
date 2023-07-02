################################################################################
# Main application script
#
# Purpose: The purpose of this software will be to use free public API (alpaca-trade-api) to fetch stock data and use that data to execute paper trades using certain trading strategies.
# I will be using a cloud database - Amazon DynamoDB to store the trade and transactional data. 
# The application logs will be logged locally to a file as well as to Amazon CloudWatch Logs and a report containing all information will be generated based on database entries. 
#
#
# Author: Dhruv Dakoria
# Contact: dakoriad@mcmaster.ca
#
################################################################################

# This script runs the application using the MVC objects.
from mvc import *

controller = Controller(View(), Model())
controller.run()