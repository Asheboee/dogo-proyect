from enums.value_permission import ValuePermission

class Permission ():
    def __init__(self, id: int, value: ValuePermission):
        self.id = id
        self.value = value