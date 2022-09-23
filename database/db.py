from boto3 import resource
from os import getenv

dynamodb = resource("dynamodb", aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
                                aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
                                region_name=getenv("REGION_NAME"))


tables = [
    {
        "TableName": "stocks_prices",
        "KeySchema": [
            {
                "AttributeName": "symbol",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "date",
                "KeyType": "RANGE"
            }
        ],
        "AttributeDefinitions": [
            {
                "AttributeName": "symbol",
                "AttributeType": "S"
            },
            {
                "AttributeName": "date",
                "AttributeType": "S"
            }        
        ]
    },
    {
        "TableName": "user_preferences",
        "KeySchema": [
            {
                "AttributeName": "user_id",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "created_at",
                "KeyType": "RANGE"
            }
        ],
        "AttributeDefinitions": [
            {
                "AttributeName": "user_id",
                "AttributeType": "S"
            },
            {
                "AttributeName": "created_at",
                "AttributeType": "S"
            }        
        ]
    },
    {
        "TableName": "users",
        "KeySchema": [
            {
                "AttributeName": "username",
                "KeyType": "HASH"
            },
            # {
            #     "AttributeName": "created_at",
            #     "KeyType": "RANGE"
            # }
        ],
        "AttributeDefinitions": [
            {
                "AttributeName": "username",
                "AttributeType": "S"
            },
            # {
            #     "AttributeName": "created_at",
            #     "AttributeType": "S"
            # }        
        ]
    }
]

def create_tables():
    try:
        for table in tables:
            dynamodb.create_table(
                TableName=table["TableName"],
                KeySchema=table["KeySchema"],
                AttributeDefinitions=table["AttributeDefinitions"],
                BillingMode="PAY_PER_REQUEST"
            )
    except Exception as e:
        print(e)