import sys
from collections import defaultdict
from collections.abc import Callable

import chess_tournament.controllers
from chess_tournament import dev_mode


class App():
    """Manage the initialization of models and fiels classes."""

    def __init__(self):
        self.loaded_models = set()
        self.pending_model_operations = defaultdict(list)

    def lazy_model_operation(self, func: Callable, model_key: str):
        """Store function to execute when the corresponding model will loaded.

        -----PARAMETERS------
        func : Callable to execute when the model will loaded if not already
        model_key : the key identifying the model
        """
        model_key = model_key.lower()
        if model_key in self.loaded_models:
            func()
        else:
            self.pending_model_operations[model_key].append(func)

    def register_model(self, model_name: str):
        """Add a model when loaded, and execute its pending operations."""
        model_name = model_name.lower()
        self.loaded_models.add(model_name)
        for func in self.pending_model_operations[model_name]:
            func()


app = App()

if __name__ == '__main__':
    params = sys.argv[1:]
    if '-d' in params or '--dev' in params:
        dev_mode.init_db()

    # import without loading controller, app has to be started before
    controller = chess_tournament.controllers.MainController()
    controller.loop()
