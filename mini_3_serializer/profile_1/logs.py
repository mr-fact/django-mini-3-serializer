from rest_framework.decorators import api_view


def start_end_log(func):
    def inner(self, *args, **kwargs):
        log_message = getattr(func, 'log_message', '')
        log_level = getattr(func, 'log_level', 0)
        log_level_spaces = log_level * '  '
        print(f'{log_level_spaces}+++[{func.__name__} - {log_message}]')
        result = func(self, *args, **kwargs)
        print(f'{log_level_spaces}---[{func.__name__} - {log_message}]')
        return result
    return inner


def message_log(message):
    def inner(func):
        func.log_message = message
        return func
    return inner


def level_log(level):
    def inner(func):
        func.log_level = level
        return func
    return inner
