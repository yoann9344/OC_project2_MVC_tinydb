from collections import defaultdict

import chess_tournament.main


class App():
    def __init__(self):
        self.loaded_models = set()
        self.pending_model_operations = defaultdict(list)

    def lazy_model_operation(self, func, model_key: str):
        model_key = model_key.lower()
        if model_key in self.loaded_models:
            func()
        else:
            self.pending_model_operations[model_key].append(func)

    def register_model(self, model_name):
        self.loaded_models.add(model_name)
        for func in self.pending_model_operations[model_name]:
            func()


app = App()


if __name__ == '__main__':
    chess_tournament.main.run()
