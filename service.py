#encoding=utf-8
import redis
from config.env import ENV, CONFIG

redis_config = CONFIG['redis']
redis_client = redis.Redis(**redis_config)


def get_uni_all_history(contract, page):
    """
    查询历史记录
    """
    if not contract or len(str(contract)) != 42:
        result = {
            "message": "invalid contract address",
            "count": 0,
            "contract": contract,
            "data": []
        }
    else:
        result = {
            "message": "success",
            "total": 50,
            "page": page,
            "pageSize": 20,
            "contract": contract,
            "data": []
        }
    return result