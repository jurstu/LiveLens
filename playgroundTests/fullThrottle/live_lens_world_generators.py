def generate_empty_world(world, start_x=0, start_y=0, start_z=0):
    return world


def generate_axis_world(world, start_x=0, start_y=0, start_z=0):
    origin = world.add_point(start_x, start_y, start_z, name="origin")

    x_point = world.add_point(start_x + 1, start_y, start_z, name="x_axis")
    y_point = world.add_point(start_x, start_y + 1, start_z, name="y_axis")
    z_point = world.add_point(start_x, start_y, start_z + 1, name="z_axis")

    world.add_line(origin, x_point, color=(255, 0, 0, 255), name="x_axis")
    world.add_line(origin, y_point, color=(0, 255, 0, 255), name="y_axis")
    world.add_line(origin, z_point, color=(0, 0, 255, 255), name="z_axis")

    return world


def generate_marker_world(world, start_x=0, start_y=0, start_z=0):
    world.add_sphere(start_x, start_y, start_z, 1, name="marker")
    world.add_glyph(start_x, start_y, start_z, "marker", name="marker_label")
    return world
