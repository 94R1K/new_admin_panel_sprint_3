import random
import time
from functools import wraps


def backoff(
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
    exceptions=(Exception,),
):
    """
    Декоратор для повторного выполнения функции при указанных исключениях.

    Время ожидания увеличивается экспоненциально и ограничивается
    border_sleep_time. К нему добавляется случайное значение jitter.

    :param start_sleep_time: начальное время ожидания
    :param factor: множитель увеличения времени ожидания
    :param border_sleep_time: максимальное время ожидания
    :param exceptions: исключения, при которых выполняется повтор
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    jitter = random.uniform(0, sleep_time)
                    time.sleep(min(
                        sleep_time + jitter,
                        border_sleep_time
                    ))

                    sleep_time = min(
                        sleep_time * factor,
                        border_sleep_time,
                    )

        return inner

    return func_wrapper