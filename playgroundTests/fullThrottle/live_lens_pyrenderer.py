import os

import numpy as np

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

import pyrender
import trimesh


class LiveLensPyrenderer:
    def __init__(self, camera):
        self.camera = camera
        self.renderer = None

    def generate_overlay_frame(self, world):
        scene = pyrender.Scene(
            bg_color=(0, 0, 0, 0),
            ambient_light=(0.25, 0.25, 0.25),
        )

        self._add_world(scene, world)
        self._add_camera(scene)

        light_pose = self._camera_pose()
        scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.0), pose=light_pose)

        renderer = self._get_renderer()
        overlay, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
        return overlay

    def _get_renderer(self):
        if self.renderer is None:
            self.renderer = pyrender.OffscreenRenderer(self.camera.width, self.camera.height)
        return self.renderer

    def _add_world(self, scene, world):
        for point in world.points:
            if point.visible:
                self._add_sphere(scene, point.x, point.y, point.z, 0.03, point.color)

        for line in world.lines:
            if line.visible:
                self._add_line(scene, line)

        for sphere in world.spheres:
            if sphere.visible:
                self._add_sphere(scene, sphere.x, sphere.y, sphere.z, sphere.radius, sphere.color)

        for glyph in world.glyphs:
            if glyph.visible:
                self._add_sphere(scene, glyph.x, glyph.y, glyph.z, 0.04, glyph.color)

        for stl in world.stls:
            if stl.visible:
                self._add_stl(scene, stl)

    def _add_sphere(self, scene, x, y, z, radius, color):
        mesh = trimesh.creation.uv_sphere(radius=radius)
        mesh.apply_translation(self._world_position(x, y, z))
        scene.add(self._pyrender_mesh(mesh, color))

    def _add_line(self, scene, line):
        p1 = self._world_position(line.p1.x, line.p1.y, line.p1.z)
        p2 = self._world_position(line.p2.x, line.p2.y, line.p2.z)
        direction = p2 - p1
        length = np.linalg.norm(direction)
        if length <= 0:
            return

        mesh = trimesh.creation.cylinder(radius=0.01, height=length)
        transform = self._cylinder_pose(p1, p2)
        mesh.apply_transform(transform)
        scene.add(self._pyrender_mesh(mesh, line.color))

    def _add_stl(self, scene, stl):
        mesh = trimesh.load(stl.path, force="mesh")
        if mesh.is_empty:
            return

        mesh.apply_scale(stl.scale)
        mesh.apply_transform(self._object_pose(stl.x, stl.y, stl.z, stl.roll, stl.pitch, stl.yaw))
        scene.add(self._pyrender_mesh(mesh, stl.color))

    def _add_camera(self, scene):
        intrinsics = self.camera.intrinsics
        if intrinsics is None:
            yfov = np.deg2rad(60)
            camera = pyrender.PerspectiveCamera(yfov=yfov, znear=0.01, zfar=10000.0)
        else:
            camera = pyrender.IntrinsicsCamera(
                fx=intrinsics.fx,
                fy=intrinsics.fy,
                cx=intrinsics.cx,
                cy=intrinsics.cy,
                znear=0.01,
                zfar=10000.0,
            )

        scene.add(camera, pose=self._camera_pose())

    def _camera_pose(self):
        ext = self.camera.extrinsics
        return self._object_pose(ext.x, ext.y, ext.z, ext.roll, ext.pitch, ext.yaw)

    def _object_pose(self, x, y, z, roll, pitch, yaw):
        pose = np.eye(4, dtype=float)
        pose[:3, :3] = self._rotation_matrix(roll, pitch, yaw)
        pose[:3, 3] = self._world_position(x, y, z)
        return pose

    def _world_position(self, x, y, z):
        return np.array([x, y, -z], dtype=float)

    def _rotation_matrix(self, roll, pitch, yaw):
        roll = np.deg2rad(roll)
        pitch = np.deg2rad(pitch)
        yaw = np.deg2rad(yaw)

        cr, sr = np.cos(roll), np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)
        cy, sy = np.cos(yaw), np.sin(yaw)

        rz_roll = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]], dtype=float)
        rx_pitch = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=float)
        ry_yaw = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=float)
        return ry_yaw @ rx_pitch @ rz_roll

    def _cylinder_pose(self, p1, p2):
        midpoint = (p1 + p2) / 2
        direction = p2 - p1
        direction = direction / np.linalg.norm(direction)

        z_axis = np.array([0, 0, 1], dtype=float)
        axis = np.cross(z_axis, direction)
        axis_norm = np.linalg.norm(axis)

        if axis_norm <= 1e-9:
            rotation = np.eye(3, dtype=float)
            if np.dot(z_axis, direction) < 0:
                rotation = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=float)
        else:
            axis = axis / axis_norm
            angle = np.arccos(np.clip(np.dot(z_axis, direction), -1.0, 1.0))
            rotation = trimesh.transformations.rotation_matrix(angle, axis)[:3, :3]

        pose = np.eye(4, dtype=float)
        pose[:3, :3] = rotation
        pose[:3, 3] = midpoint
        return pose

    def _pyrender_mesh(self, mesh, color):
        material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=self._rgba_float(color),
            metallicFactor=0.0,
            roughnessFactor=1.0,
        )
        return pyrender.Mesh.from_trimesh(mesh, material=material, smooth=False)

    def _rgba_float(self, color):
        if len(color) == 3:
            color = (*color, 255)
        return tuple(channel / 255 for channel in color)

    def close(self):
        if self.renderer is not None:
            self.renderer.delete()
            self.renderer = None
