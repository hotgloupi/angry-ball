from cube import gl
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller

def power_matrix(shape):
    return gl.matrix.scale(
        gl.matrix.translate(
          gl.mat4f(),
            gl.vec3f(shape.x, shape.y - shape.h, -.2)
        ),
        gl.vec3f(shape.w, shape.h, 1)
    )

class Refill:
    channels = ['tick']
    velocity = 200
    def __init__(self, entity):
        self.entity = entity
        self.transform = self.entity.component('transform')

    def __call__(self, ev, delta):
        self.entity.shape.h += delta * self.velocity
        if self.entity.shape.h > 100:
            self.entity.shape.h = 100
        self.transform.node.value = power_matrix(self.entity.shape)

def create(shape, entity_manager):
    mat = gl.Material('power')
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
    power = entity_manager.create('power', shape = shape)

    transform = power.add_component(Transform(power_matrix(shape)))
    power.add_component(Bindable(mat))
    power.add_component(Drawable(mesh))

    refill = Controller(Refill(power))

    def start_power(ev, delta):
        power.add_component(refill)
    power.add_component(Controller(start_power, ['start-power']))

    def stop_power(ev, delta):
        power.remove_component(refill)
        power.shape.h = 1
        transform.node.value = power_matrix(power.shape)
    power.add_component(Controller(stop_power, ['stop-power']))

    return power
