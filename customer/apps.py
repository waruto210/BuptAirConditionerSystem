from django.apps import AppConfig


class CustomerConfig(AppConfig):
    name = 'customer'

    def ready(self):
        from .models import State, init_state
        from airconfig.config import config
        for room_id in config.room_list:
            state, flag = State.objects.get_or_create(room_id=room_id)
            if flag is True:
                init_state(state)
                state.save()
