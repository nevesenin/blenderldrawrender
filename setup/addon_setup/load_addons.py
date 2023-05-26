import os
import bpy
import sys
import traceback
from . environment import user_addon_directory, addon_directories

def setup_addon_links(addons_to_load):
    if not os.path.exists(user_addon_directory):
        os.makedirs(user_addon_directory)

    if not str(user_addon_directory) in sys.path:
        sys.path.append(str(user_addon_directory))

    for source_path, module_name in addons_to_load:
        if is_in_any_addon_directory(source_path):
            load_path = source_path
        else:
            load_path = os.path.join(user_addon_directory, module_name)
            create_link_in_user_addon_directory(source_path, load_path)

def load(addons_to_load ,options):
    for module_name in map(lambda item: item[1], addons_to_load):
        addon_disabled = False

        try:
            bpy.ops.preferences.addon_enable(module=module_name)
        except:
            traceback.print_exc()
    
        if module_name == 'io_scene_import_ldraw' and \
            (options.disable_ldraw_import or options.disable_ldraw_addons):
            addon_disabled = True

        if module_name == 'io_scene_import_ldraw_mm' and \
            (options.disable_ldraw_import_mm or options.disable_ldraw_addons):
            addon_disabled = True

        if module_name == 'io_scene_render_ldraw' and \
            (options.disable_ldraw_render or options.disable_ldraw_addons):
            addon_disabled = True

        if addon_disabled:
            try:
                bpy.ops.preferences.addon_disable(module=module_name)
            except:
                traceback.print_exc()
            print(f"ADDON MODULE DISABLED:  {module_name}")
            continue

        print(f"ADDON MODULE ENABLED:   {module_name}")

    # Save user preferences
    bpy.ops.wm.save_userpref()

def create_link_in_user_addon_directory(directory, link_path):
    if os.path.exists(link_path):
        os.remove(link_path)

    if sys.platform == "win32":
        import _winapi
        _winapi.CreateJunction(str(directory), str(link_path))
    else:
        os.symlink(str(directory), str(link_path), target_is_directory=True)

def is_in_any_addon_directory(module_path):
    for path in addon_directories:
        if path == module_path.parent:
            return True
    return False
