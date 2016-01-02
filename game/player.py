
from pathlib import Path

from cube import gl, units, scene
from cubeapp.game.event import Event, Channel
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller

def player_matrix(pos, radius):
    return gl.matrix.rotate(
        gl.matrix.scale(
            gl.matrix.translate(gl.mat4f(), pos),
            gl.vec3f(radius, radius, 1)
        ),
        units.deg(0),
        gl.vec3f(1, 1, 0)
    )


class MovePlayer:
    channels = ['move-player']

    def __init__(self, player, event_manager):
        self.move = None
        self.player = player
        self.event_manager = event_manager

    def __call__(self, ev, delta):
        #print("SET POS", ev.channel.name, ev.pos, ev.power, self.player.pos)
        if ev.channel == 'move-player':
            print("MOVE", ev.key)
            self.player.impulsion = {
                'right': gl.vec3f(1, 0, 0),
                'up':    gl.vec3f(0, -1, 0),
                'left': gl.vec3f(-1, 0, 0),
                'down': gl.vec3f(0, 1, 0),
            }[ev.key] * 2000
            return

class AnimatePlayer:
    channels = ['tick', 'set-board-friction']
    velocity = 12
    friction = 1

    def __init__(self,
                 player,
                 event_manager):
        self.player = player
        self.event_manager = event_manager
        self.transform = self.player.component('transform')


    def __call__(self, ev, delta):
        if ev.channel == 'tick':
            acc = self.player.gravity + self.player.force + self.player.impulsion
            #print('ACC:', acc)
            self.player.velocity += acc * delta
            pos = self.player.pos + (
                self.player.velocity * delta +
                .5 * acc * delta ** 2
            )
            self.transform.node.value = player_matrix(pos, self.player.radius)
            self.event_manager.push(
                Event(
                    'player-moved',
                    old = self.player.pos,
                    new = pos,
                    player = self.player,
                )
            )
            self.player.pos = pos
            self.player.impulsion *= .2

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

    player = entity_manager.create(
        'player',
        velocity = gl.vec3f(0),
        gravity = gl.vec3f(0, 1000, 0),
        force = gl.vec3f(0),
        impulsion = gl.vec3f(0),
        radius = 30,
    )
    player.pos = initial_player_pos

    transform = player.add_component(
        Transform(player_matrix(player.pos, player.radius))
    )
    player.add_component(Bindable(mat, name = 'material'))
    player.add_component(Drawable(mesh))
    player.add_component(Controller(MovePlayer(player, event_manager)))
    player.add_component(Controller(
        AnimatePlayer(
            player = player,
            event_manager = event_manager,
        )
    ))
    return player
