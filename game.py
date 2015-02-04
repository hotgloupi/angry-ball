
import time

import cubeapp
import cube
from cube import gl, units
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller

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
        <p id="title">Angry Ball</p>
    </body>
</rml>
"""

class Game(cubeapp.game.Game):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.window.add_font(self.directory / 'FreeMono.ttf')
        document = self.window.load_document(DOCUMENT)
        self.title = document.by_id("title")
        self.cube = self.create_cube()
        self.light = self.renderer.new_light(
            gl.PointLightInfo(
                gl.vec3f(0, 2, -1),
                gl.Color3f("#888"),
                gl.Color3f("#333"),
            )
        )
        self.scene_view = self.scene.drawable(self.renderer)
        self.last_time = time.time()

    def create_cube(self):
        mat = gl.Material('cube')
        mat.ambient = gl.col3f('#100')
        mat.diffuse = gl.col3f('#f55')
        mat.specular = gl.col3f('#f00')
        mat.shininess = 5
        mat.shading_model = gl.material.ShadingModel.gouraud


        mesh =  cube.gl.Cube3f(cube.gl.vec3f(), 1).drawable(self.renderer)

        entity = self.entity_manager.create('Cube')
        transform = entity.add_component(
            Transform(gl.matrix.scale(gl.mat4f(), gl.vec3f(4)))
        )
        entity.add_component(Bindable(mat))
        entity.add_component(Drawable(mesh))
        class Animate:
            channels = ['tick']
            velocity = 10
            def __call__(self, ev, delta):
                transform.node.rotate(units.deg(45) * delta * self.velocity, gl.vec3f(1, .5, 0))
        entity.add_component(Controller(Animate()))
        return entity


    def render(self):
        new_time = time.time()
        self.title.text = "%.2f ms" % ((new_time - self.last_time) * 1000)
        self.last_time = new_time
        with self.renderer.begin(gl.mode_3d) as painter:
            painter.state.look_at(
                gl.vec3f(0,0,-10), gl.vec3f(0, 0, 0), gl.vec3f(0, 1, 0)
            )
            painter.state.perspective(
                units.deg(45), self.window.width / self.window.height, 0.005, 300.0
            )
            with painter.bind([self.light]):
                painter.draw([self.scene_view])
