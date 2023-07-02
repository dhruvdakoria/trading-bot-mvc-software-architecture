from time import time
import config.appconfig as cfg
import boto3
import time

dbconn=boto3.resource('dynamodb',aws_access_key_id=cfg.dynamodb["aws_access_key_id"], aws_secret_access_key=cfg.dynamodb["aws_secret_access_key"], region_name=cfg.dynamodb["region_name"]).Table(cfg.dynamodb["table_name"])

cwlog = boto3.client('logs',aws_access_key_id=cfg.dynamodb["aws_access_key_id"], aws_secret_access_key=cfg.dynamodb["aws_secret_access_key"], region_name=cfg.dynamodb["region_name"])

# cwlog.create_log_group(logGroupName='trade-bot')
cwlog.create_log_stream(
    logGroupName='trade-bot',
    logStreamName='dhruv-test'
)
cwlog.put_log_events(
    logGroupName='trade-bot',
    logStreamName='dhruv-test',
    logEvents=[
        {
            'timestamp': int(round(time.time() * 1000)),
            'message': 'This is my message'
        },
    ]
)

# dbconn.put_item(
#     Item={
#         'report_name': 'test2',
#         'strategy_name': 'coin-toss',
#         'symbol': 'TSLA',
#         'quantity': '5',
#         'max_sells': '2',
#         'transaction_details': str({"xyz":"abc"})
#     }
# )
# response = dbconn.get_item(
#     Key={'report_name': "test2"}
# )

# print(response)

# response=dbconn.scan(Select='SPECIFIC_ATTRIBUTES',ProjectionExpression='report_name')
# data = response['Count']
# # report_names=[]
# # for d in data:
# #     report_names.append(d['report_name'])
# print(data)
# print(report_names)