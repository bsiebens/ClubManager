from urllib.parse import urljoin

import requests

from .base import CompetitionBaseClass
from ..models import Game


class RBIHF(CompetitionBaseClass):
    def __init__(self):
        super().__init__()
        self.url = "https://rbihf.be/modules/league/ajax/time.php"

    def update_game_information(self, game: Game) -> None:
        season = f"{game.season.start_time.strftime("%y")}{game.season.end_time.strftime("%y")}"
        payload = {"gameNr": game.competition_game_id, "season": season}
        headers = {
            "Cookie": "language=en",
            "Postman-Token": "clubmanager",
            "Host": "www.rbihf.be",
            "User-Agent": "PostmanRuntime/7.37.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate,br",
            "Connection": "keep-alive",
            "Referer": f"https://rbihf.be/game/{game.competition_game_id}",
            "X-Requested-With": "XMLHttpRequest",
        }

        req = requests.get(self.url, params=payload, headers=headers)

        if req.status_code == 200:
            game_data = req.json()
            game.is_live = game_data["live"]

            if game.is_home_game:
                game.score_team = game_data["scoreA"]
                game.score_opponent = game_data["scoreB"]
            else:
                game.score_team = game_data["scoreB"]
                game.score_opponent = game_data["scoreA"]

            game.save(update_fields=["is_live", "score_team", "score_opponent"])


class CEHL(CompetitionBaseClass):
    def __init__(self):
        super().__init__()
        self.url = "https://www.cehl.eu/ajax/"

    def update_game_information(self, game: Game) -> None:
        season = "{start}{end}".format(start=game.season.start_date.strftime("%y"), end=game.season.end_date.strftime("%y"))

        referer_url = urljoin("https://www.cehl.eu", f"game/{season}/{game.competition_game_id}")
        timeline_url = urljoin(self.url, "timeline.php")
        score_url = urljoin(self.url, "score.php")

        payload = {"nr": game.competition_game_id, "season": season}
        headers = {
            "Cookie": "language=en",
            "Postman-Token": "clubmanager",
            "Host": "www.cehl.eu",
            "User-Agent": "PostmanRuntime/7.37.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,br",
            "Connection": "close",
            "Referer": referer_url,
            "X-Requested-With": "XMLHttpRequest",
        }

        timeline_req = requests.get(timeline_url, params=payload, headers=headers)
        score_req = requests.get(score_url, params=payload, headers=headers)

        if timeline_req.status_code == 200:
            game.is_live = timeline_req.json()["live"] == 1

        if score_req.status_code == 200:
            game_data = score_req.json()

            if game.is_home_game:
                game.score_team = game_data["scoreA"]
                game.score_opponent = game_data["scoreB"]

            else:
                game.score_team = game_data["scoreB"]
                game.score_opponent = game_data["scoreA"]

        if timeline_req.status_code == 200 or score_req.status_code == 200:
            game.save(update_fields=["is_live", "score_team", "score_opponent"])
