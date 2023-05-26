import mathutils

import math

from .import_options import ImportOptions

auto_smooth_angle_deg = 31
auto_smooth_angle_deg = 44.97
auto_smooth_angle_deg = 51.1
auto_smooth_angle_deg = 89.9  # 1.56905 - 89.9 so 90 degrees and up are affected
auto_smooth_angle = math.radians(auto_smooth_angle_deg)

# https://www.ldraw.org/article/218.html#coords
# LDraw uses a right-handed co-ordinate system where -Y is "up".
# https://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Understanding_Coordinates
# Blender uses a right-handed co-ordinate system where +Z is "up"
identity_matrix = mathutils.Matrix.Identity(4).freeze()
rotation_matrix = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X').freeze()  # rotate -90 degrees on X axis to make -Y up
import_scale_matrix = mathutils.Matrix.Scale(ImportOptions.import_scale, 4).freeze()
gap_scale_matrix = mathutils.Matrix.Scale(ImportOptions.gap_scale, 4).freeze()
transform_matrix = rotation_matrix @ import_scale_matrix


def reset_caches():
    global auto_smooth_angle
    global import_scale_matrix
    global gap_scale_matrix
    global transform_matrix

    auto_smooth_angle = math.radians(auto_smooth_angle_deg)
    import_scale_matrix = mathutils.Matrix.Scale(ImportOptions.import_scale, 4).freeze()
    gap_scale_matrix = mathutils.Matrix.Scale(ImportOptions.gap_scale, 4).freeze()
    transform_matrix = rotation_matrix @ import_scale_matrix
