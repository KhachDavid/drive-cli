class File:
    def __init__(self, name, id):
        self.name = name
        self.id = id
    
    def __str__(self):
        return f'Name: {self.name}, ID: {self.id}'
