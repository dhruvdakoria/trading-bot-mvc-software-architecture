################################################################################
# Application global read-only state using Singleton pattern
#
# Purpose: App singleton contains all of the read-only state data that must be accessible across the application like - 
# configuration data, Alpaca Trade API setup, logging and the database connection. Singleton pattern: https://en.wikipedia.org/wiki/Singleton_pattern.
#
# The app uses the Alpaca Trade API to access to execute orders for different trade strategies and retrieve details of the orders:
# - https://github.com/alpacahq/alpaca-trade-api-python
#
# The configuration for the app is stored in the config folder and the variables are referenced here and the config dir is put in .gitignore
#
# Author: Dhruv Dakoria
# Contact: dakoriad@mcmaster.ca
#
################################################################################

# App Class is a Singleton that manages read-only state of the application. 

import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST,TimeFrame
from alpaca_trade_api.stream import Stream
import config.appconfig as cfg
import boto3
from logger import *

class App():

    __instance = None
    
    # Creates/returns the singleton instance
    def __new__(cls):
        if (cls.__instance is None):
            cls.__instance = super(App, cls).__new__(cls)
            cls.__instance.setup()

        return cls.__instance

    # Setup the singleton based on the config file
    def setup(self):
        # setup the Trade API module using config from config/appconfig file
        self.tradeapi = tradeapi.REST(key_id=cfg.alpaca_api["apikey"], secret_key=cfg.alpaca_api["secretkey"], base_url="https://paper-api.alpaca.markets", api_version='v2')
        self.apiTimeFrame = TimeFrame
        
        self.connstream = Stream(
            cfg.alpaca_api["apikey"],
            cfg.alpaca_api["secretkey"],
            base_url="https://paper-api.alpaca.markets",
            data_feed='iex')

        # setup dynamodb connection based on config values
        self.dbconn = boto3.resource('dynamodb',aws_access_key_id=cfg.dynamodb["aws_access_key_id"], aws_secret_access_key=cfg.dynamodb["aws_secret_access_key"], region_name=cfg.dynamodb["region_name"]).Table(cfg.dynamodb["table_name"])
        self.cwlog = boto3.client('logs',aws_access_key_id=cfg.dynamodb["aws_access_key_id"], aws_secret_access_key=cfg.dynamodb["aws_secret_access_key"], region_name=cfg.dynamodb["region_name"])


        # Setup logging using template method and chain of responsibility pattern
        self.__logger = None
        if (cfg.logging["terminal"] == "TRUE"):
            self.__logger = TerminalLogger( self.__logger )
        if (cfg.logging["file"] == "TRUE"):
            self.log_filename = cfg.logging["log_filename"]
            self.__logger = FileLogger( self.__logger, self.log_filename )
        if (cfg.logging["cloudwatch_logging"] == "TRUE"):
            self.__logger = CloudWatchLogger( self.__logger, self.cwlog, cfg.cloudwatch["log_group"], cfg.cloudwatch["log_stream"])

    # Log a message
    def log(self,message):
        if self.__logger == None:
            return
        else:
            self.__logger.log(message)