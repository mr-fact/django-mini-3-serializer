from rest_framework.decorators import api_view


def start_end_log(func):
    def inner(self, *args, **kwargs):
        log_message = getattr(func, 'log_message', '')
        print(f'\t+++[{func.__name__} - {log_message}]')
        result = func(self, *args, **kwargs)
        print(f'\t---[{func.__name__} - {log_message}]')
        return result
    return inner


def message_log(message):
    def inner(func):
        func.log_message = message
        return func
    return inner
