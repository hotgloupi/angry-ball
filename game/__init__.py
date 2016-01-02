
import time

import cubeapp
from cube import gl, units
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller
from cubeapp.game.event import Event, Channel
from cubeapp.game import Game as BasicGame
from cube.system.inputs import Button, KeySym, KeyMod

DOCUMENT = """
<rml>
    <head>
    <style>
    body {
        font-family: FreeMono;
        font-size: 30pt;
        color: white;
    }
    </style>
    </head>
    <body>
        <p id="title">8cube framework</p>
    </body>
</rml>
"""

from . import player
from . import board
from . import power

class Game(BasicGame):

    bindings = {
        'keyboard': {
            'up': KeySym.up,
            'down': KeySym.down,
            'left': KeySym.left,
            'right': KeySym.right,
        }
    }

    def __init__(self, window, directory):
        super().__init__(window, directory, bindings = self.bindings)
        self.window.add_font(self.directory / 'FreeMono.ttf')
        self.resource_manager.add_path(str(self.directory / 'resource'))
        document = self.window.load_document(DOCUMENT)
        self.title = document.by_id("title")
        size = gl.vec2u(10, 10)
        border = 5
        self.board = board.load(
            self.directory / 'resource/map/00.txt',
            game = self,
            border = border,
            screen_size = self.window.size,
        )
        self.player = player.create(
            entity_manager = self.entity_manager,
            event_manager = self.event_manager,
            renderer = self.renderer,
            initial_player_pos = gl.vec3f(border + 200, border + 200, 0),
        )
        self.light = self.renderer.new_light(
            gl.PointLightInfo(
                gl.vec3f(0, 2, -1),
                gl.Color3f("#888"),
                gl.Color3f("#333"),
            )
        )
        self.scene_view = self.scene.drawable(self.renderer)
        self.last_time = time.time()
        window.inputs.on_mousedown.connect(self.__on_mousedown)
        window.inputs.on_mouseup.connect(self.__on_mouseup)

        for key in ('up', 'down', 'left', 'right'):
            slot = getattr(self.input_translator.keyboard, key).key_held
            slot.connect(
                lambda ev, key = key: self.event_manager.push(
                    Event('move-player', key = key)
                )
            )


    def __on_mousedown(self, button, keymod):
        pass

    def __on_mouseup(self, button, keymod):
        pass



    def render(self):
        new_time = time.time()
        #self.title.text = "%.2f ms" % ((new_time - self.last_time) * 1000)
        self.last_time = new_time
        with self.renderer.begin(gl.mode_2d) as painter:
            #painter.state.look_at(
            #    gl.vec3f(0,0,-1), gl.vec3f(0, 0, 1), gl.vec3f(0, 1, 0)
            #)
            #painter.state.perspective(
            #    units.deg(45), self.window.width / self.window.height, 0.005, 300.0
            #)
            #painter.state.look_at(
            #    gl.vec3f(self.window.width / 2, self.window.height / 2, -800),
            #    gl.vec3f(self.window.width / 2, self.window.height / 2, 0),
            #    gl.vec3f(0, 1, 0)
            #)
            #painter.state.perspective(
            #    units.deg(45), self.window.width / self.window.height, 0.005, 3000.0
            #)
            painter.state.view = gl.matrix.translate(gl.mat4f(), -self.player.pos + gl.vec3f(self.window.width / 2, self.window.height / 2, 0))
            with painter.bind([self.light]):
                painter.draw([self.scene_view])
