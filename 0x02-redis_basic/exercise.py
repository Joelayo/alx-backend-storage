#!/usr/bin/env python3
'''A module for using the Redis NoSQL data storage.
'''
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''Tracks the number of calls made to a method in a Cache class.
    '''
    @wraps(method)
    def wrapper(self, *args, **kwds):
        '''Wraps the given method after incrementing its call counter.
        '''
        key_name = method.__qualname__
        self._redis.incr(key_name, 0) + 1
        return method(self, *args, **kwds)
    return wrapper


def call_history(method: Callable) -> Callable:
    '''Tracks the call details of a method in a Cache class.
    '''
    @wraps(method)
    def wrapper(self, *args, **kwds):
        '''Returns the method's output after storing its inputs and output.
        '''
        key_m = method.__qualname__
        inp_m = key_m + ':inputs'
        outp_m = key_m + ":outputs"
        data = str(args)
        self._redis.rpush(inp_m, data)
        fin = method(self, *args, **kwds)
        self._redis.rpush(outp_m, str(fin))
        return fin
    return wrapper


def replay(func: Callable):
    '''Displays the call history of a Cache class' method.
    '''
    r = redis.Redis()
    key_m = func.__qualname__
    inp_m = r.lrange("{}:inputs".format(key_m), 0, -1)
    outp_m = r.lrange("{}:outputs".format(key_m), 0, -1)
    calls_number = len(inp_m)
    times_str = 'times'
    if calls_number == 1:
        times_str = 'time'
    fin = '{} was called {} {}:'.format(key_m, calls_number, times_str)
    print(fin)
    for k, v in zip(inp_m, outp_m):
        fin = '{}(*{}) -> {}'.format(
            key_m,
            k.decode('utf-8'),
            v.decode('utf-8')
        )
        print(fin)


class Cache():
    '''Represents an object for storing data in a Redis data storage.
    '''
    def __init__(self):
        '''Initializes a Cache instance.
        '''
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Stores a value in a Redis data storage and returns the key.
        '''
        generate = str(uuid.uuid4())
        self._redis.set(generate, data)
        return generate

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''Retrieves a value from a Redis data storage.
        '''
        value = self._redis.get(key)
        return value if not fn else fn(value)

    def get_int(self, key):
        '''Retrieves an integer value from a Redis data storage.
        '''
        return self.get(key, int)

    def get_str(self, key):
        '''Retrieves a string value from a Redis data storage.
        '''
        value = self._redis.get(key)
        return value.decode("utf-8")
