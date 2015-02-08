
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

class Game(BasicGame):

    def __init__(self, window, directory):
        super().__init__(window, directory)
        self.window.add_font(self.directory / 'FreeMono.ttf')
        document = self.window.load_document(DOCUMENT)
        self.title = document.by_id("title")
        self.size = 5
        self.border = 10
        self.tile_width = (self.window.width - self.border * 2) / self.size
        self.tile_height = (self.window.height - self.border * 2) / self.size
        self.ground = self.create_ground(self.size, self.border, self.tile_width, self.tile_height)
        self.player_pos = gl.vec3f(self.border + 10, self.border + 10, 0)
        self.player = self.create_player()
        self.light = self.renderer.new_light(
            gl.PointLightInfo(
                gl.vec3f(0, 2, -1),
                gl.Color3f("#888"),
                gl.Color3f("#333"),
            )
        )
        self.power_size = 1
        self.power = self.create_power()
        self.scene_view = self.scene.drawable(self.renderer)
        self.last_time = time.time()
        window.inputs.on_mousedown.connect(self.__on_mousedown)
        window.inputs.on_mouseup.connect(self.__on_mouseup)


    def __on_mousedown(self, button, keymod):
        self.event_manager.push(Event('start-power'))

    def __on_mouseup(self, button, keymod):
        self.event_manager.push(Event('stop-power'))
        mouse = self.window.system_window.mouse_position
        self.event_manager.push(
            Event(
                'move-player',
                pos = gl.vec3f(mouse.x, mouse.y, 0),
                power = self.power_size
            )
        )

    def __pointed_tile(self):
        return self.pos_to_tile(self.window.system_window.mouse_position)

    def tile_to_pos(self, tile):
        return gl.vec3f(
            tile.x * self.tile_width + self.border,
            tile.y * self.tile_height + self.border,
            0
        )

    def pos_to_tile(self, pos):
        tile = gl.vec2i(
            (pos.x - self.border) // self.tile_width,
            (pos.y - self.border) // self.tile_height
        )
        if tile.x < 0: tile.x = 0
        if tile.y < 0: tile.y = 0
        if tile.x >= self.size: tile.x = self.size - 1
        if tile.y >= self.size: tile.y = self.size - 1
        return tile


    def create_ground(self, size, border, tile_width, tile_height):
        mat = gl.Material('ground')
        mat.ambient = gl.col3f('#888')
        mat.diffuse = gl.col3f('#000')
        mat.specular = gl.col3f('#000')
        #mat.shininess = 0
        #mat.shading_model = gl.material.ShadingModel.gouraud
        mat.add_color(
            gl.ShaderParameterType.vec3,
            gl.StackOperation.add
        )
        coords = []
        colors = []
        indices = list(range(size * size * 4))
        for i in range(size):
            x = i * tile_width + border
            for j in range(size):
                y = j * tile_height + border
                coords.extend([
                    gl.vec3f(x, y, 0),
                    gl.vec3f(x, y + tile_height, 0),
                    gl.vec3f(x + tile_width, y + tile_height, 0),
                    gl.vec3f(x + tile_width, y, 0),
                ])
                colors.extend([
                    gl.col3f('#356712'),
                    gl.col3f('#356712'),
                    gl.col3f('#356712'),
                    gl.col3f('#356712'),
                ])
        self.ground_vb = self.renderer.new_vertex_buffer([
            gl.make_vba(
                gl.ContentKind.vertex,
                coords,
                gl.ContentHint.static_content
            ),
            gl.make_vba(
                gl.ContentKind.color,
                colors,
                gl.ContentHint.static_content
            )
        ])
        self.ground_ib = self.renderer.new_index_buffer(
            gl.make_vba(
                gl.ContentKind.index,
                indices,
                gl.ContentHint.static_content
            )
        )
        colors_attr = self.ground_vb[1]
        colors_attr[0] = gl.col3f('blue')
        colors_attr[1] = gl.col3f('blue')
        self.ground_vb.reload(1)
        entity = self.entity_manager.create('ground')
        transform = entity.add_component(
            Transform(
                gl.matrix.translate(
                    #gl.matrix.scale(
                       gl.mat4f(),
                    #    gl.vec3f(size, size, 1)
                    #),
                    gl.vec3f(-.5, -.5, 0)
                )
            )
        )
        class DrawGround(gl.Drawable):
            def __init__(self, vb, ib, size):
                self.vb, self.ib, self.size = vb, ib, size
                super().__init__()
            def draw(self, painter):
                with painter.bind([self.vb]):
                    painter.draw_elements(gl.DrawMode.quads, self.ib, 0, self.size)

        entity.add_component(Bindable(mat))
        entity.add_component(Drawable(DrawGround(self.ground_vb, self.ground_ib, len(indices))))
        class PaintGround:
            channels = ['player-moved']
            def __init__(self, game):
                self.game = game

            def __call__(self, ev, delta):
                new_tile = self.game.pos_to_tile(ev.new)
                idx = int(new_tile.y + new_tile.x * self.game.size) * 4
                attr = self.game.ground_vb[1]
                attr[idx] = gl.col3f('blue')
                attr[idx + 1] = gl.col3f('blue')
                attr[idx + 2] = gl.col3f('blue')
                attr[idx + 3] = gl.col3f('blue')
                self.game.ground_vb.reload(1)
                pass
        entity.add_component(Controller(PaintGround(game = self)))
        return entity

    def create_player(self):
        mat = gl.Material('player')
        mat.ambient = gl.col3f('lightblue')
        #mat.diffuse = gl.col3f('black')
        #mat.specular = gl.col3f('black')
        mat.opacity = 1
        mesh = gl.Spheref(gl.vec3f(0, 0, 0), 100).drawable(self.renderer)
        light = self.renderer.new_light(
            gl.PointLightInfo(
                gl.vec3f(0, 8, -1),
                gl.Color3f("#888"),
                gl.Color3f("#333"),
            )
        )
        player = self.entity_manager.create('player')
        def player_matrix(pos):
            return gl.matrix.scale(
                gl.matrix.translate(gl.mat4f(), pos),
                gl.vec3f(20, 20, 1)
            )

        transform = player.add_component(
            Transform(player_matrix(self.player_pos))
        )

        #player.add_component(Bindable(light, name = 'light'))
        player.add_component(Bindable(mat, name = 'material'))
        player.add_component(Drawable(mesh))
        #def change_colors(ev, delta):
        #    mat.ambiant = rand_color()
        #
        class AnimatePlayer:
            channels = ['tick']
            velocity = 12
            def __init__(self, game, power, dir):
                self.game = game
                self.power = power
                self.dir = gl.vector.normalize(dir)
            def __call__(self, ev, delta):
                if self.power <= 1:
                    return
                self.power -= 1
                pos = self.new_pos(delta)
                if pos.x < self.game.border or \
                   pos.x >= self.game.window.width - self.game.border:
                    self.dir.x *= -1
                    pos = self.new_pos(delta)
                if pos.y < self.game.border or \
                   pos.y >= self.game.window.height - self.game.border:
                    self.dir.y *= -1
                    pos = self.new_pos(delta)
                self.game.event_manager.push(
                    Event('player-moved', old = self.game.player_pos, new = pos)
                )
                self.game.player_pos = pos
                transform.node.value = player_matrix(pos)

            def new_pos(self, delta):
                return self.game.player_pos + self.dir * delta * self.power * self.velocity

        class MovePlayer:
            channels = ['move-player']
            def __init__(self, game):
                self.game = game
                self.move = None
            def __call__(self, ev, delta):
                print("SET POS", ev.channel.name, ev.pos, ev.power, self.game.player_pos)
                if self.move is not None:
                    player.remove_component(self.move)
                    self.move = None
                dir = ev.pos - self.game.player_pos
                if dir == gl.vec3f(0):
                    return
                self.move = player.add_component(Controller(
                    AnimatePlayer(
                        game = self.game,
                        power = ev.power,
                        dir = dir,
                    )
                ))
            #transform.node.translate(gl.vec3f(ev.pos.x, ev.pos.y, 0))
        player.add_component(Controller(MovePlayer(self)))
        return player

    def create_power(self):
        mat = gl.Material('ground')
        mat.ambient = gl.col3f('#888')
        mat.diffuse = gl.col3f('#000')
        mat.specular = gl.col3f('#000')
        #mat.shininess = 0
        #mat.shading_model = gl.material.ShadingModel.gouraud
        mat.add_color(
            gl.ShaderParameterType.vec3,
            gl.StackOperation.add
        )
        mesh = gl.Mesh()
        mesh.mode = gl.DrawMode.quads
        mesh.kind = gl.ContentKind.vertex
        mesh.append(gl.vec3f(0, 0, 0))
        mesh.append(gl.vec3f(0, 1, 0))
        mesh.append(gl.vec3f(1, 1, 0))
        mesh.append(gl.vec3f(1, 0, 0))
        mesh.kind = gl.ContentKind.color
        mesh.append(gl.col3f('red'))
        mesh.append(gl.col3f('green'))
        mesh.append(gl.col3f('green'))
        mesh.append(gl.col3f('red'))
        mesh.kind = gl.ContentKind.normal
        mesh.append(gl.vec3f(0, 0, 1))
        mesh.append(gl.vec3f(0, 0, 1))
        mesh.append(gl.vec3f(0, 0, 1))
        mesh.append(gl.vec3f(0, 0, 1))
        entity = self.entity_manager.create('power')
        def power_matrix(size):
                return gl.matrix.scale(
                    gl.matrix.translate(
                      gl.mat4f(),
                        gl.vec3f(self.window.width - 30, self.window.height - size, -.2)
                    ),
                    gl.vec3f(30, size, 1)
                )

        transform = entity.add_component(Transform(power_matrix(self.power_size)))
        entity.add_component(Bindable(mat))
        entity.add_component(Drawable(mesh))
        game = self
        class Refill:
            channels = ['tick']
            velocity = 100
            def __call__(self, ev, delta):
                game.power_size += delta * self.velocity
                if game.power_size > 100:
                    game.power_size = 100
                transform.node.value = power_matrix(game.power_size)

        refill = Controller(Refill())
        def start_power(ev, delta):
            entity.add_component(refill)
        def stop_power(ev, delta):
            entity.remove_component(refill)
            game.power_size = 1
            transform.node.value = power_matrix(game.power_size)

        entity.add_component(Controller(start_power, ['start-power']))
        entity.add_component(Controller(stop_power, ['stop-power']))


        return entity

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
