import random
import time
from collections.abc import Callable
from functools import wraps

from logger import logger


def backoff(
    exceptions=(Exception,),
    reconnect: Callable[[object], None] | None = None,
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
):
    """
    Декоратор для повторного выполнения функции при указанных исключениях.

    Время ожидания увеличивается экспоненциально и ограничивается
    border_sleep_time. К нему добавляется случайное значение jitter.

    :param exceptions: исключения, при которых выполняется повтор
    :param reconnect: callback, вызываемый перед повторной попыткой
    :param start_sleep_time: начальное время ожидания
    :param factor: множитель увеличения времени ожидания
    :param border_sleep_time: максимальное время ожидания
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            sleep_time = start_sleep_time

            while True:
                try:
                    return func(self, *args, **kwargs)
                except exceptions:
                    if reconnect is not None:
                        try:
                            reconnect(self)
                        except exceptions as reconnect_exc:
                            logger.warning(
                                "Не удалось переподключиться в %s: %s",
                                func.__name__,
                                reconnect_exc,
                            )

                    jitter = random.uniform(0, sleep_time)
                    time.sleep(min(sleep_time + jitter, border_sleep_time))

                    sleep_time = min(
                        sleep_time * factor,
                        border_sleep_time,
                    )

        return inner

    return func_wrapper
