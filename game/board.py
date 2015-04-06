from cube import gl
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller

def pos_to_tile(board, pos):
    tile = gl.vec2i(
        (pos.x - board.border) // board.tile_width,
        (pos.y - board.border) // board.tile_height
    )
    if tile.x < 0: tile.x = 0
    if tile.y < 0: tile.y = 0
    if tile.x >= board.size: tile.x = board.size - 1
    if tile.y >= board.size: tile.y = board.size - 1
    return tile

class DrawGround(gl.Drawable):
    def __init__(self, board, size):
        self.vb, self.ib, self.size = board.vb, board.ib, size
        super().__init__()
    def draw(self, painter):
        with painter.bind([self.vb]):
            painter.draw_elements(gl.DrawMode.quads, self.ib, 0, self.size)

class PaintGround:
    channels = ['player-moved']
    def __init__(self, board):
        self.board = board

    def __call__(self, ev, delta):
        new_tile = pos_to_tile(self.board, ev.new)
        idx = int(new_tile.y + new_tile.x * self.board.size) * 4
        attr = self.board.vb[1]
        attr[idx] = gl.col3f('blue')
        attr[idx + 1] = gl.col3f('blue')
        attr[idx + 2] = gl.col3f('blue')
        attr[idx + 3] = gl.col3f('blue')
        self.board.vb.reload(1)

def create(renderer, entity_manager, size, border, tile_width, tile_height):
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
    ground_vb = renderer.new_vertex_buffer([
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
    ground_ib = renderer.new_index_buffer(
        gl.make_vba(
            gl.ContentKind.index,
            indices,
            gl.ContentHint.static_content
        )
    )
    colors_attr = ground_vb[1]
    colors_attr[0] = gl.col3f('blue')
    colors_attr[1] = gl.col3f('blue')
    ground_vb.reload(1)

    board = entity_manager.create(
        'board',
        ib = ground_ib,
        vb = ground_vb,
        size = size,
        tile_height = tile_height,
        tile_width = tile_width,
        border = border,
    )
    transform = board.add_component(
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
    board.add_component(Bindable(mat))
    board.add_component(Drawable(DrawGround(board, len(indices))))
    board.add_component(Controller(PaintGround(board)))
    return board

