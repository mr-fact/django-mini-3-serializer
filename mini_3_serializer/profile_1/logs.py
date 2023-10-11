def start_end_log(func):
    def inner(self, *args, **kwargs):
        print(f'\t+++[{func.__name__}]')
        result = func(self, *args, **kwargs)
        print(f'\t---[{func.__name__}]')
        return result
    return inner
