from ..models import Game


class CompetitionBaseClass:
    def __init__(self):
        self.url = "http://localhost"

    def update_game_information(self, game: Game) -> None:
        raise NotImplementedError
