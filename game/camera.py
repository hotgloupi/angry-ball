from cube import gl, units, scene
from cubeapp.game.event import Event, Channel
from cubeapp.game.entity.component import Controller

class MoveCamera:
    channels = ['player-moved']

    def __init__(self, cam):
        self.cam = cam

    def __call__(self, ev, delta):
        vec = ev.new - self.cam.pos
        d =  gl.vector.length(vec)
        if d > 0.1:
            self.cam.pos += vec * delta * 5


def create(entity_manager, initial_player_pos):
    cam = entity_manager.create(
        'camera',
        pos = initial_player_pos,
    )
    cam.add_component(Controller(MoveCamera(cam)))
    return cam
