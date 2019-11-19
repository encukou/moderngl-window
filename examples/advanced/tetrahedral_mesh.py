from pathlib import Path
import numpy as np
from pyrr import Matrix44

import moderngl
import moderngl_window
from moderngl_window.opengl.vao import VAO
from moderngl_window import geometry
from base import CameraWindow


class TetrahedralMesh(CameraWindow):
    """Minimal WindowConfig example"""
    gl_version = (4, 1)
    title = "Basic Window Config"
    aspect_ratio = None
    resource_dir = (Path(__file__) / '../../resources').resolve()
    samples = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.mouse_exclusivity = True
        self.camera.projection.update(near=.01, far=100)
        self.camera.mouse_sensitivity = .5
        self.camera.velocity = 2.5

        self.quad_fs = geometry.quad_fs()

        # (172575,) | 57,525 vertices
        vertices = np.load(self.resource_dir / 'data/tetrahedral_mesh/mesh_nodes.npy')
        vertices = np.concatenate(vertices)

        # (259490, 4) (1037960,) indices
        indices = np.load(self.resource_dir / 'data/tetrahedral_mesh/element_nodes.npy')
        indices = np.concatenate(indices) - 1

        # Original geometry with indices
        self.geometry = VAO(name='geometry_indices')
        self.geometry.buffer(vertices, '3f', 'in_position')
        self.geometry.index_buffer(indices, index_element_size=4)

        self.prog_background = self.load_program('programs/tetrahedral_mesh/bg.glsl')
        self.prog_gen_tetra = self.load_program(
            vertex_shader='programs/tetrahedral_mesh/gen_tetra_vert.glsl',
            geometry_shader='programs/tetrahedral_mesh/gen_tetra_geo.glsl',
            fragment_shader='programs/tetrahedral_mesh/gen_tetra_frag.glsl',
        )
        self.prog_gen_tetra_lines = self.load_program(
            vertex_shader='programs/tetrahedral_mesh/gen_tetra_vert.glsl',
            geometry_shader='programs/tetrahedral_mesh/gen_tetra_geo.glsl',
            fragment_shader='programs/tetrahedral_mesh/lines_frag.glsl',
        )

    def render(self, time, frametime):
        self.ctx.wireframe = False
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.quad_fs.render(self.prog_background)

        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        # translate = Matrix44.from_translation((0.0, 3.0, -12.0), dtype='f4')
        translate = Matrix44.from_translation((0.0, 0.0, 0.0), dtype='f4')
        rotate = Matrix44.from_eulers((np.radians(180), 0, 0), dtype='f4')
        scale = Matrix44.from_scale((400, 400, 400), dtype='f4')
        mat = self.camera.matrix * translate * rotate * scale

        self.prog_gen_tetra['color'].value = 0.0, 0.8, 0.0
        self.prog_gen_tetra['m_cam'].write(mat)
        self.prog_gen_tetra['m_proj'].write(self.camera.projection.matrix)
        self.geometry.render(self.prog_gen_tetra, mode=moderngl.LINES_ADJACENCY)

        # # Uncomment for black lines
        self.ctx.wireframe = True
        self.prog_gen_tetra_lines['color'].value = 0.0, 0.0, 0.0
        self.prog_gen_tetra_lines['m_cam'].write(mat)
        self.prog_gen_tetra_lines['m_proj'].write(self.camera.projection.matrix)
        self.geometry.render(self.prog_gen_tetra_lines, mode=moderngl.LINES_ADJACENCY)


if __name__ == '__main__':
    moderngl_window.run_window_config(TetrahedralMesh)