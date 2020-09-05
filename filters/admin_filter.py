from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

class AdminFilter(BoundFilter):
    key = "is_admin"
    required = True
    default = False
    is_admin: bool

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    def check(self):
        pass



