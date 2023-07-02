################################################################################
# Logger implements Chain-of-Responsibility pattern and Template Method Pattern
#
# Purpose: Defines a general logger class for carrying out logging
# functionality, as well as logger subclasses for terminal, file, and streaming logs to AWS cloudwatch logs
# Chain of responsbility pattern: https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern
#
# In order to avoid the call super anti-pattern, we use the Template method pattern with the create_log_entry methods:
# https://en.wikipedia.org/wiki/Template_method_pattern
#
#
# Author: Dhruv Dakoria
# Contact: dakoriad@mcmaster.ca
#
################################################################################

from abc import ABC, abstractmethod
import datetime
import time

# Define what it means to be a logger object in chain-of-responsiblity pattern
class Logger(ABC):

    # create_log_entry is a hook method that will be implemented in subclasses
    @abstractmethod
    def create_log_entry(self, message): pass

    # Calls hook method create_log_entry, which will be different for each subclass
    def log(self, message):

        self.create_log_entry(message)

        if (self.__next_logger == None):
            return
        else:
            self.__next_logger.log(message)

    def __init__(self,next_logger):
        self.__next_logger = next_logger

# Logs directly to a file, appends message on next line
class FileLogger(Logger):

    def __init__(self,next_logger,log_filename):
        self.__log_file = open(log_filename, "a+")
        super().__init__(next_logger)

    def create_log_entry(self, message):
        self.__log_file.write(str(datetime.datetime.now()) + ": " + message + "\n")

# Logs message directly to the terminal
class TerminalLogger(Logger):

    def create_log_entry(self, message):
        print(str(datetime.datetime.now()) + ": " + message)

# Logs message to CloudWatch Log group and stream, appends log to existing stream using sequence token from previous log
class CloudWatchLogger(Logger):

    def __init__(self,next_logger,cwlog,cwloggroup,cwlogstream):
        self.__cwlog = cwlog
        self.__cwloggroup = cwloggroup
        self.__cwlogstream = cwlogstream
        super().__init__(next_logger)

    # create log entry in cloudwatch log stream
    def create_log_entry(self, message):
        # loop through log streams inside a log group
        for logstream in self.__cwlog.describe_log_streams(logGroupName=self.__cwloggroup)['logStreams']:
            if logstream['logStreamName'] == self.__cwlogstream:
                # if an entry exists in the logstream (meaning it has a uploadSequenceToken) then put next log event by passing the sequenceToken
                if "uploadSequenceToken" in logstream:
                    self.__cwlog.put_log_events(
                        logGroupName=self.__cwloggroup,
                        logStreamName=self.__cwlogstream,
                        logEvents=[
                            {
                                'timestamp': int(round(time.time() * 1000)),
                                'message': message
                            },
                        ],
                        sequenceToken=logstream['uploadSequenceToken']
                    )
                # if its the first entry in the log stream put event without token
                else:
                    self.__cwlog.put_log_events(
                        logGroupName=self.__cwloggroup,
                        logStreamName=self.__cwlogstream,
                        logEvents=[
                            {
                                'timestamp': int(round(time.time() * 1000)),
                                'message': message
                            },
                        ]
                    )