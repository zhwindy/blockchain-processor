#encoding=utf-8

ENV = 'LOCAL'
# ENV = 'TEST'

UNI_CONTRACT = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"

if ENV == 'LOCAL':
    CONFIG = {
        "redis":{
            "host": "127.0.0.1",
            "port": 6379,
            "password": "redis-123456"
        },
        "mysql":{
            "host": "127.0.0.1",
            "port": 3306,
            "user": "coldlar",
            "passwd": "eth123456",
            "db": "eth"
        },
        "table": "tx_history",
        "node": "http://127.0.0.1:18759"
    }
else:
    CONFIG = {
        "redis":{
            "host": "101.201.126.224",
            "port": 6379,
            "password": "redis-123456"
        },
        "mysql":{
            "host": "101.201.126.224",
            "port": 3306,
            "user": "coldlar",
            "passwd": "eth123456",
            "db": "eth"
        },
        "table": "tx_history_test",
        "node": "http://101.201.126.224:18759"
    }
