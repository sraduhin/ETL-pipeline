import inspect
import re
import sys
from json import JSONDecodeError


from search.state import State


class Redis:
    """Заглушка, позволяющая проводить тесты без использования Redis."""

    def __init__(self) -> None:
        self.data = {}

    def get(self, name):
        return self.data.get(name)

    def set(self, name, value):
        self.data[name] = value


def test_get_empty_state() -> None:
    redis = Redis()
    storage = RedisStorage(redis)
    state = State(storage)

    assert state.get_state('key') is None


def test_save_new_state() -> None:
    redis = Redis()
    storage = RedisStorage(redis)
    state = State(storage)

    state.set_state('key', 123)

    assert redis.data == {'data': '{"key": 123}'}


def test_retrieve_existing_state() -> None:
    redis = Redis()
    redis.data = {'data': '{"key": 10}'}
    storage = RedisStorage(redis)
    state = State(storage)

    assert state.get_state('key') == 10


def test_save_state_and_retrieve() -> None:
    redis = Redis()
    storage = RedisStorage(redis)
    state = State(storage)

    state.set_state('key', 123)

    # Принудительно удаляем объекты
    del state
    del storage

    storage = RedisStorage(redis)
    state = State(storage)

    assert state.get_state('key') == 123


def test_error_on_corrupted_data() -> None:
    try:
        redis = Redis()
        redis.data = {'data': '{"key":}'}

        storage = RedisStorage(redis)
        State(storage)

    except JSONDecodeError:
        assert True
        return

    assert False


def run_tests(pattern: str = 'test_*') -> None:
    search_pattern = re.compile(pattern)
    for name, func in inspect.getmembers(sys.modules[__name__]):
        if search_pattern.match(name):
            func()


if __name__ == '__main__':
    run_tests()
