from constance.signals import config_updated
from django.dispatch import receiver


@receiver(config_updated)
def update_home_game_location(sender, key, old_value, new_value, **kwargs):
    """Updates the home location to a new value, will also retroactively change the old locations."""
    if key == 'CLUBMANAGER_CLUB_LOCATION' and old_value != new_value:
        ...

        # TODO Implement the actual logic once games have been implemented --> should be moved into the games/activities app once build!