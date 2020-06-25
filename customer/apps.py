from django.apps import AppConfig


class CustomerConfig(AppConfig):
    name = 'customer'

    def ready(self):
        from .models import State, init_state
        from airconfig.config import config
        for room_id in config.room_list:
            state, _ = State.objects.get_or_create(room_id=room_id)
            init_state(state)
            state.save()
