import redis
from utils.utils import get_main_logger, get_mode, is_json
from config.config import get_config
import json

log = get_main_logger('redis_manager')
_conf = get_config()
MODE = get_mode()


class RedisManager:
    def __init__(self):
        self.dbs = {'assets': 0, 'tasks': 1}
        self.topics = {'assets': 'assets', 'tasks': 'tasks', 'reports': 'reports'}
        self.subscriptions = {}

    def get_redis(self, db=0):
        try:
            with redis.Redis(host=_conf[MODE]['redis_url'], port=_conf[MODE]['redis_port'], db=db) as r:
                return r
        except Exception as e:
            log.error(e.__str__())
            return False

    def subscribe_to_channel(self, db, channel: str, callback):
        r = self.get_redis(db).pubsub()
        r.psubscribe(**{channel: callback})
        self.subscriptions[channel] = r.run_in_thread(sleep_time=0.01)

    def unsubscribe_from_channel(self, db, channel):
        # subscrition = self.subscriptions[channel]
        pass

    def write_data(self, _key: str, _value: dict) -> bool:
        try:
            assert isinstance(_value, dict), '_value should be of type Dict'
            self.get_redis().set(_key, json.dumps(_value))
            return True
        except Exception as e:
            log.error(e.__str__())
            return False

    def get_data_by_key(self, _key: str):
        try:
            if is_json(self.get_redis().get(_key)):  # if the result is jsonifiable it json loads it
                return json.loads(self.get_redis().get(_key))
            else:  # else it just returns the result (probably string)
                return self.get_redis().get(_key)
        except Exception as e:
            log.error(e.__str__())
            return {}

    def get_data_by_wildcard(self, _wildcard: str) -> list:
        try:
            return [{key.decode('utf-8'): self.get_data_by_key(key) for key in self.get_redis().keys(_wildcard + '*') if self.get_redis().keys(_wildcard + '*')}]
        except Exception as e:
            log.error(e.__str__())
            return []

    def get_all_data(self) -> list:
        try:
            return [{key.decode('utf-8'): self.get_data_by_key(key) for key in self.get_redis().keys() if self.get_redis().keys()}]
        except Exception as e:
            log.error(e.__str__())
            return []

    def delete_all_keys(self):
        try:
            r = self.get_redis()
            for k in r.keys():
                r.delete(r.keys())
        except Exception as e:
            log.error(e.__str__())
            return []
