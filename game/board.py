from cube import gl
from cubeapp.game.entity.component import Transform, Drawable, Bindable, Controller
from cubeapp.game.entity.component import Component
from cubeapp.game.entity import System
from cubeapp.game.event import Event

def pos_to_tile(board, pos):
    tile = gl.vec2i(
        (pos.x - board.border) // board.tile_width,
        (pos.y - board.border) // board.tile_height
    )
    if tile.x < 0: tile.x = 0
    if tile.y < 0: tile.y = 0
    if tile.x >= board.size.x: tile.x = board.size.x - 1
    if tile.y >= board.size.y: tile.y = board.size.y - 1
    return tile

class DrawGround(gl.Drawable):
    def __init__(self, board, size):
        self.vb, self.ib, self.size = board.vb, board.ib, size
        super().__init__()
    def draw(self, painter):
        with painter.bind([self.vb]):
            painter.draw_elements(gl.DrawMode.quads, self.ib, 0, self.size)

def load(file, game, border, screen_size):
    rows = []
    max_width = 0
    with open(str(file)) as f:
        for line in f:
            rows.append(line[:-1])
            max_width = max((max_width, len(rows[-1])))
    rows = list(row.ljust(max_width) for row in rows)
    size = gl.vec2u(max_width, len(rows))
    return create(
        game = game,
        size = size,
        tile_width = (screen_size.x - border * 2) / size.x,
        tile_height = (screen_size.y - border * 2) / size.y,
        border = border,
        rows = rows,
    )


class Cell:
    def __init__(self, color):
        self.color = color

    def __call__(self, board, tile):
        # Called when the player enter to this tile
        self.set_color(board, tile, gl.col3f('purple'))

    def prepare(self, board, tile):
        # Called at startup for each board cell
        self.set_color(board, tile, self.color)

    def set_color(self, board, tile, color):
        idx = int(tile.y + tile.x * board.size.y) * 4
        attr = board.vb[1]
        attr[idx] = color
        attr[idx + 1] = color
        attr[idx + 2] = color
        attr[idx + 3] = color
        board.vb.reload(1)

class SetBoardFriction:
    def __init__(self, friction):
        self.friction = friction

    def prepare(self, board, tile):
        pass

    def __call__(self, board, tile):
        board.event_manager.push(
            Event('set-board-friction',  friction = self.friction)
        )

# Mapping between ascii codes and controllers
# Multiple controllers can be set per character, their __call__ method will
# be triggered whenever the player cross a particular cell.
cell_controllers = {
    '@': (Cell(gl.col3f('red')), ),
    '#': (Cell(gl.col3f('white')), SetBoardFriction(friction = .5),),
    'x': (
        Cell(gl.col3f('#2342ff')),
        SetBoardFriction(friction = 5),
    ),
}

class CellManager(Controller):
    """Centralize all cell controllers"""
    channels = ['player-moved']
    def __init__(self, board):
        self.cells = {}
        self.current_tile = None
        self.board = board
        y = 0
        for row in self.board.rows:
            x = 0
            for c in row:
                if c != ' ':
                    tile = gl.vec2i(x, y)
                    controllers = self.cells[tile] = cell_controllers[c]
                    for controller in controllers:
                        controller.prepare(board, tile)
                x += 1
            y += 1

    def __call__(self, ev, delta):
        tile = pos_to_tile(self.board, ev.new)
        if tile != self.current_tile:
            self.current_tile = tile
            controllers = self.cells.get(tile, [])
            for controller in controllers:
                controller(self.board, tile)


def create(game, size, border, tile_width, tile_height, rows):
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
    indices = list(range(size.x * size.y * 4))
    for i in range(size.x):
        x = i * tile_width + border
        for j in range(size.y):
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
    ground_vb = game.renderer.new_vertex_buffer([
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
    ground_ib = game.renderer.new_index_buffer(
        gl.make_vba(
            gl.ContentKind.index,
            indices,
            gl.ContentHint.static_content
        )
    )
    # Set initial color
    #colors_attr = ground_vb[1]
    #colors_attr[0] = gl.col3f('blue')
    #colors_attr[1] = gl.col3f('blue')
    #ground_vb.reload(1)

    board = game.entity_manager.create(
        'board',
        ib = ground_ib,
        vb = ground_vb,
        size = size,
        tile_height = tile_height,
        tile_width = tile_width,
        border = border,
        rows = rows,
        event_manager = game.event_manager,
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
    board.add_component(Controller(CellManager(board = board)))

    return board

