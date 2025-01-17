import bpy

from .import_options import ImportOptions
from .ldraw_color import LDrawColor
from . import group
from . import strings
from . import ldraw_props
from . import ldraw_meta
from . import ldraw_mesh
from . import matrices

top_empty = None
gap_scale_empty = None


def reset_caches():
    global top_empty
    global gap_scale_empty

    top_empty = None
    gap_scale_empty = None


# TODO: to add rigid body - must apply scale and cannot be parented to empty
def create_object(key, mesh, geometry_data, color_code, matrix, collection):
    obj = bpy.data.objects.new(mesh.name, mesh)
    obj[strings.ldraw_filename_key] = geometry_data.file.name
    obj[strings.ldraw_color_code_key] = color_code
    color = LDrawColor.get_color(color_code)
    obj.color = color.linear_color_a

    ldraw_props.set_props(obj, geometry_data.file, color_code)
    __process_top_object_matrix(obj, matrix)
    __process_top_object_edges(obj)
    ldraw_meta.do_meta_step(obj)
    __link_obj_to_collection(obj, collection)
    __create_edge_obj(key, obj, geometry_data, color_code, collection)

    return obj


def __process_top_object_matrix(obj, obj_matrix):
    global top_empty

    import_scale_matrix = matrices.rotation_matrix @ matrices.import_scale_matrix

    if ImportOptions.parent_to_empty:
        if top_empty is None:
            top_empty = bpy.data.objects.new(group.top_collection.name, None)
            top_empty.ldraw_props.invert_import_scale_matrix = True
            group.link_obj(group.top_collection, top_empty)

        top_empty.matrix_world = import_scale_matrix

        matrix_world = obj_matrix
        matrix_world = __process_gap_scale_matrix(obj, matrix_world)
        obj.matrix_world = matrix_world

        obj.parent = top_empty  # must be after matrix_world set or else transform is incorrect
    else:
        matrix_world = import_scale_matrix @ obj_matrix
        matrix_world = __process_gap_scale_matrix(obj, matrix_world)
        obj.matrix_world = matrix_world

        obj.ldraw_props.invert_import_scale_matrix = True


def __process_gap_scale_matrix(obj, matrix_world):
    if ImportOptions.make_gaps:
        matrix_world = matrix_world @ matrices.gap_scale_matrix
        obj.ldraw_props.invert_gap_scale_matrix = True
    return matrix_world


def __process_top_object_edges(obj):
    if ImportOptions.bevel_edges:
        bevel_modifier = obj.modifiers.new("Bevel", type='BEVEL')
        bevel_modifier.limit_method = 'WEIGHT'
        bevel_modifier.width = ImportOptions.bevel_width
        bevel_modifier.segments = ImportOptions.bevel_segments

    if ImportOptions.smooth_type_value() == "edge_split":
        edge_modifier = obj.modifiers.new("Edge Split", type='EDGE_SPLIT')
        edge_modifier.use_edge_sharp = True
        # need this or else items with right angles but aren't marked as sharp aren't shaded properly
        # see the back blue window stripes in 10252-1 - Volkswagen Beetle.mpd
        edge_modifier.use_edge_angle = True
        edge_modifier.split_angle = matrices.auto_smooth_angle


def __create_edge_obj(key, obj, geometry_data, color_code, collection):
    if ImportOptions.import_edges:
        edge_key = f"e_{key}"
        edge_mesh = ldraw_mesh.get_mesh(edge_key)
        edge_obj = bpy.data.objects.new(edge_mesh.name, edge_mesh)
        edge_obj[strings.ldraw_filename_key] = f"{geometry_data.file.name}_edges"
        edge_obj[strings.ldraw_color_code_key] = color_code
        color = LDrawColor.get_color(color_code)
        edge_obj.color = color.edge_color_d

        ldraw_meta.do_meta_step(edge_obj)

        __link_obj_to_collection(edge_obj, collection)

        edge_obj.parent = obj
        edge_obj.matrix_world = obj.matrix_world


def __link_obj_to_collection(obj, _collection):
    group.link_obj(_collection, obj)

    group.link_obj(group.parts_collection, obj)

    if group.current_step_group is not None:
        group.link_obj(group.current_step_group, obj)

    if ImportOptions.meta_group:
        if group.next_collection is not None:
            group.link_obj(group.next_collection, obj)
        else:
            group.link_obj(group.ungrouped_collection, obj)
