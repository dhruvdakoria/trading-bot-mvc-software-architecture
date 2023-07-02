# Name: 
Trading Bot Application 

# Project purpose and audience  
The purpose of this software will be to use free public API (alpaca-trade-api) to fetch stock data and use that data to execute paper trades using certain trading strategies. I will be using a cloud database - Amazon DynamoDB to store the trade and transactional data. The application logs will be logged locally to a file as well as to Amazon CloudWatch Logs and a report containing all information will be generated based on database entries.   

# Target Audience  
The target audience is stock market investing enthusiasts who would like to gather stock data and execute paper trades to test out an algorithmic trading strategy. 

# Identified Requirements
1. Users shall be able to provide a list of stocks they want to trade with. (FUNCTIONAL)  
2. The application shall be able to fetch market data (stock prices) using public RESTful APIs. (FUNCTIONAL)  
3. The application shall allow the creation or cancellation of trading orders. (FUNCTIONAL)  
4. The application shall allow the execution of paper trades based on a defined strategy. (FUNCTIONAL)  
5. The data for the executed/cancelled trades shall be written to a cloud database. (FUNCTIONAL)  
6.	Application logs shall be available to the users through a log file stored locally. (FUNCTIONAL)  
7.	Users shall be able to request a report of trades performed. (FUNCTIONAL)  
8.	API data should be live with the frequency of updates every minute. (NONFUNCTIONAL)  


# How to run this application

1. Install the necessary python packages to run the app
`python3 -m pip install requirements.txt`

2. Run the python app
`python3 main.py`

# Application Structure and information

1. The core application functionality is carried out using the MVC pattern
2. Application global read-only state uses Singleton pattern for things like configuration data, Alpaca Trade API setup, logging and the database connection.
3. Logging setup uses chain-of-reponsibility and template pattern
4. Config files stored in config/ dir
5. Logs stored locally are in logs/ dir and also streamed to Cloudwatch
6. Reports are locally stored in reports/ dir
7. Trading Strategies stored in trading_startegies/ dir