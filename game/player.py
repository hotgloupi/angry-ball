
from pathlib import Path

from cube import gl, units, scene
from cubeapp.game.event import Event, Channel
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller

def player_matrix(pos):
    return gl.matrix.rotate(
        gl.matrix.scale(
            gl.matrix.translate(gl.mat4f(), pos),
            gl.vec3f(200, 200, 1)
        ),
        units.deg(0),
        gl.vec3f(1, 1, 0)
    )


class MovePlayer:
    channels = ['move-player', 'board-size']

    def __init__(self, player, event_manager):
        self.move = None
        self.player = player
        self.board_size = None
        self.event_manager = event_manager

    def __call__(self, ev, delta):
        if ev.channel == 'board-size':
            self.board_size = ev.board_size
            return
        if self.board_size is None:
            return
        #print("SET POS", ev.channel.name, ev.pos, ev.power, self.player.pos)
        if self.move is not None:
            self.player.remove_component(self.move)
            self.move = None
        dir = ev.pos - self.player.pos
        if dir == gl.vec3f(0):
            return
        self.move = self.player.add_component(Controller(
            AnimatePlayer(
                player = self.player,
                power = ev.power,
                dir = dir,
                board_size = self.board_size,
                event_manager = self.event_manager,
            )
        ))

class AnimatePlayer:
    channels = ['tick', 'set-board-friction']
    velocity = 12
    friction = 1

    def __init__(self,
                 player,
                 power,
                 dir,
                 board_size,
                 event_manager):
        self.player = player
        self.power = power
        self.dir = gl.vector.normalize(dir)
        self.board_size = board_size
        self.event_manager = event_manager
        self.transform = self.player.component('transform')

    def __call__(self, ev, delta):
        if ev.channel == 'set-board-friction':
            self.friction = ev.friction
            return
        if self.board_size is None:
            return
        if self.power <= 1:
            return
        self.power -= 1
        pos = self.new_pos(delta)
        if pos.x < self.board_size.x or \
           pos.x >= self.board_size.x + self.board_size.w:
            self.dir.x *= -1
            pos = self.new_pos(delta)
        if pos.y < self.board_size.y or \
           pos.y >= self.board_size.y + self.board_size.h:
            self.dir.y *= -1
            pos = self.new_pos(delta)

        self.event_manager.push(
            Event('player-moved', old = self.player.pos, new = pos)
        )
        self.player.pos = pos
        self.transform.node.value = player_matrix(pos)

    def new_pos(self, delta):
        return self.player.pos + self.dir * delta * self.power * self.velocity / self.friction

def create(entity_manager, event_manager, renderer, initial_player_pos = (0, 0)):
    s = """
tess 6
shader img/rabbit.tif
s 1.0 -4.0 2.0 4.0 20 20
    """
    sc = scene.from_string(s, "nff")
    mesh = sc.meshes[0]
    mat = sc.materials[0]
    light = renderer.new_light(
        gl.PointLightInfo(
            gl.vec3f(0, 8, -1),
            gl.Color3f("#888"),
            gl.Color3f("#333"),
        )
    )
    #mat.textures[0].texture.generate_mipmap()

    player = entity_manager.create('player')
    player.pos = initial_player_pos

    transform = player.add_component(
        Transform(player_matrix(player.pos))
    )
    player.add_component(Bindable(mat, name = 'material'))
    player.add_component(Drawable(mesh))
    player.add_component(Controller(MovePlayer(player, event_manager)))
    return player
