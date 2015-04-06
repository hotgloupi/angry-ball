
import time

import cubeapp
from cube import gl, units
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller
from cubeapp.game.event import Event, Channel
from cubeapp.game import Game as BasicGame
from cube.system.inputs import Button

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

    def __init__(self, window, directory):
        super().__init__(window, directory)
        self.window.add_font(self.directory / 'FreeMono.ttf')
        document = self.window.load_document(DOCUMENT)
        self.title = document.by_id("title")
        size = gl.vec2u(10, 10)
        border = 10
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
            initial_player_pos = gl.vec3f(border + 10, border + 10, 0),
        )
        self.light = self.renderer.new_light(
            gl.PointLightInfo(
                gl.vec3f(0, 2, -1),
                gl.Color3f("#888"),
                gl.Color3f("#333"),
            )
        )
        self.power = power.create(
            shape = gl.Rectanglef(
                self.window.width - 35,
                self.window.height,
                30,
                1
            ),
            entity_manager = self.entity_manager
        )
        self.scene_view = self.scene.drawable(self.renderer)
        self.last_time = time.time()
        window.inputs.on_mousedown.connect(self.__on_mousedown)
        window.inputs.on_mouseup.connect(self.__on_mouseup)
        self.event_manager.push(
            Event(
                'board-size',
                board_size = gl.Rectanglef(
                    border,
                    border,
                    self.window.width - border * 2,
                    self.window.height - border * 2,
                )
            )
        )


    def __on_mousedown(self, button, keymod):
        self.event_manager.push(Event('start-power'))

    def __on_mouseup(self, button, keymod):
        self.event_manager.push(Event('stop-power'))
        mouse = self.window.system_window.mouse_position
        self.event_manager.push(
            Event(
                'move-player',
                pos = gl.vec3f(mouse.x, mouse.y, 0),
                power = self.power.shape.h
            )
        )

    #def __pointed_tile(self):
    #    return self.pos_to_tile(self.window.system_window.mouse_position)

    #def tile_to_pos(self, tile):
    #    return gl.vec3f(
    #        tile.x * self.tile_width + self.border,
    #        tile.y * self.tile_height + self.border,
    #        0
    #    )



    def render(self):
        new_time = time.time()
        #self.title.text = "%.2f ms" % ((new_time - self.last_time) * 1000)
        self.last_time = new_time
        with self.renderer.begin(gl.mode_2d) as painter:
            #painter.state.look_at(
            #    gl.vec3f(0,0,self.size * 2), gl.vec3f(0, 0, 0), gl.vec3f(0, 1, 0)
            #)
            #painter.state.perspective(
            #    units.deg(45), self.window.width / self.window.height, 0.005, 300.0
            #)
            with painter.bind([self.light]):
                painter.draw([self.scene_view])
