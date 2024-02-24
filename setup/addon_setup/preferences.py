import os
import sys
import json
import copy
import configparser
from pathlib import Path
from shutil import copyfile

from . import handle_fatal_error

class Preferences():
    """Marshall LDraw Blender settings."""

    __sectionKey = "TN"
    __sectionName = "ImportLDraw"
    __updateIni = False
    __configFile = None

    def __init__(self, configfile, prefsfile, sectionkey):

        self.__sectionKey = sectionkey
        if self.__sectionKey == "MM":
            self.__sectionName = "ImportLDrawMM"
        assert prefsfile != "", "Preferences file path was not specified."
        self.__configFile = configfile

        self.__config = configparser.RawConfigParser()
        self.__prefsRead = self.__config.read(self.__configFile)
        if self.__prefsRead and not self.__config[self.__sectionName]:
            self.__prefsRead = False

        # If the ImportLDrawPreferences.ini includes attributes from an older version that
        # has been changed or removed, or if the Python addon version is newer than the version
        # defined in the calling application, the following attributes are updated.
        # Version 1.5 and later attribute updates:
        for section in self.__config.sections():
            if section == "ImportLDraw":
                addList = ['realgapwidth,0.0002', 'realscale,0.02']
                for addItem in addList:
                    pair = addItem.split(",")
                    if not self.__config.has_option(section, pair[0]):
                        self.__config.set(section, pair[0], str(pair[1]))
                        self.__updateIni = True
                popList = ['gapwidth', 'scale']
                for popItem in popList:
                    if self.__config.has_option(section, popItem):
                        self.__config[section].pop(popItem)
                        self.__updateIni = True
            elif section == "ImportLDrawMM":
                addList = ['colorstrategy,material']
                addList += ['casesensitivefilesystem,True'] if sys.platform == "linux" else ['casesensitivefilesystem,False']
                for addItem in addList:
                    pair = addItem.split(",")
                    if not self.__config.has_option(section, pair[0]):
                        self.__config.set(section, pair[0], str(pair[1]))
                        self.__updateIni = True
                popList = ['preservehierarchy', 'treatmodelswithsubpartsasparts', 'gapscalestrategy', 'gaptarget']
                for popItem in popList:
                    if self.__config.has_option(section, popItem):
                        self.__config[section].pop(popItem)
                        self.__updateIni = True

        self.__prefsFilepath = prefsfile

        self.__default_settings = {}
        if self.__sectionKey == "MM":
            self.__settings = dict()
            self.__default_settings = {
                'add_environment': self.__config[self.__sectionName]['addenvironment'],
                'additional_search_paths': self.__config[self.__sectionName]['additionalsearchpaths'],
                'bevel_edges': self.__config[self.__sectionName]['beveledges'],
                'bevel_weight': self.__config[self.__sectionName]['bevelweight'],
                'bevel_width': self.__config[self.__sectionName]['bevelwidth'],
                'bevel_segments': self.__config[self.__sectionName]['bevelsegments'],
                'blend_file': self.__config[self.__sectionName]['blendfile'],
                'blendfile_trusted': self.__config[self.__sectionName]['blendfiletrusted'],
                'camera_border_percent': self.__config[self.__sectionName]['cameraborderpercent'],
                'case_sensitive_filesystem': self.__config[self.__sectionName]['casesensitivefilesystem'],
                'chosen_logo': self.__config[self.__sectionName]['chosenlogo'],
                'color_strategy': self.__config[self.__sectionName]['colorstrategy'],
                'crop_image': self.__config[self.__sectionName]['cropimage'],
                'custom_ldconfig_file': self.__config[self.__sectionName]['customldconfigfile'],
                'display_logo': self.__config[self.__sectionName]['displaylogo'],
                'environment_file': self.__config[self.__sectionName]['environmentfile'],
                'frames_per_step': self.__config[self.__sectionName]['framesperstep'],
                'gap_scale': self.__config[self.__sectionName]['gapscale'],
                'import_cameras': self.__config[self.__sectionName]['importcameras'],
                'import_edges': self.__config[self.__sectionName]['importedges'],
                'import_lights': self.__config[self.__sectionName]['importlights'],
                'import_scale': self.__config[self.__sectionName]['importscale'],
                'ldraw_path': self.__config[self.__sectionName]['ldrawpath'],
                'make_gaps': self.__config[self.__sectionName]['makegaps'],
                'merge_distance': self.__config[self.__sectionName]['mergedistance'],
                'meta_bfc': self.__config[self.__sectionName]['metabfc'],
                'meta_clear': self.__config[self.__sectionName]['metaclear'],
                'meta_group': self.__config[self.__sectionName]['metagroup'],
                'meta_pause': self.__config[self.__sectionName]['metapause'],
                'meta_print_write': self.__config[self.__sectionName]['metaprintwrite'],
                'meta_save': self.__config[self.__sectionName]['metasave'],
                'meta_step': self.__config[self.__sectionName]['metastep'],
                'meta_step_groups': self.__config[self.__sectionName]['metastepgroups'],
                'meta_texmap': self.__config[self.__sectionName]['metatexmap'],
                'no_studs': self.__config[self.__sectionName]['nostuds'],
                'overwrite_image': self.__config[self.__sectionName]['overwriteimage'],
                'parent_to_empty': self.__config[self.__sectionName]['parenttoempty'],
                'position_camera': self.__config[self.__sectionName]['positioncamera'],
                'prefer_studio': self.__config[self.__sectionName]['preferstudio'],
                'prefer_unofficial': self.__config[self.__sectionName]['preferunofficial'],
                'profile': self.__config[self.__sectionName]['profile'],
                'recalculate_normals': self.__config[self.__sectionName]['recalculatenormals'],
                'remove_doubles': self.__config[self.__sectionName]['removedoubles'],
                'render_percentage': self.__config[self.__sectionName]['renderpercentage'],
                'render_window': self.__config[self.__sectionName]['renderwindow'],
                'resolution': self.__config[self.__sectionName]['resolution'],
                'resolution_height': self.__config[self.__sectionName]['resolutionheight'],
                'resolution_width': self.__config[self.__sectionName]['resolutionwidth'],
                'search_additional_paths': self.__config[self.__sectionName]['searchadditionalpaths'],
                'set_end_frame': self.__config[self.__sectionName]['setendframe'],
                'set_timeline_markers': self.__config[self.__sectionName]['settimelinemarkers'],
                'shade_smooth': self.__config[self.__sectionName]['shadesmooth'],
                'smooth_type': self.__config[self.__sectionName]['smoothtype'],
                'starting_step_frame': self.__config[self.__sectionName]['startingstepframe'],
                'studio_ldraw_path': self.__config[self.__sectionName]['studioldrawpath'],
                'transparent_background': self.__config[self.__sectionName]['transparentbackground'],
                'treat_shortcut_as_model': self.__config[self.__sectionName]['treatshortcutasmodel'],
                'triangulate': self.__config[self.__sectionName]['triangulate'],
                'use_colour_scheme': self.__config[self.__sectionName]['usecolourscheme'],
                'use_freestyle_edges': self.__config[self.__sectionName]['usefreestyleedges'],
                'verbose': self.__config[self.__sectionName]['verbose']
            }

    def set(self, option, value):
        if self.__sectionName not in self.__config:
            self.__config[self.__sectionName] = {}
        self.__config[self.__sectionName][option] = str(value)

    def save(self):
        if self.__sectionKey == "MM":
            self.__settings = {}
            for k, v in self.__default_settings.items():
                value = self.__config[self.__sectionName][k.replace("_", "").lower()]
                self.__settings[k] = self.evaluate_value(value)
            self.write_json()
        else:
            self.write_ini()

    def save_config_ini(self):
        if self.__updateIni:
            self.__prefsFilepath = self.__configFile
            self.write_ini(True)

    def write_ini(self, configini=False):
        try:
            folder = os.path.dirname(self.__prefsFilepath)
            Path(folder).mkdir(parents=True, exist_ok=True)
            config = copy.deepcopy(self.__config)
            if not configini:
                for section in config.sections():
                    if section != self.__sectionName:
                        config.remove_section(section)
            with open(self.__prefsFilepath, 'w', encoding='utf-8', newline="\n") as configFile:
                config.write(configFile)
            return True
        except OSError as e:
            handle_fatal_error(f"Could not save INI preferences. I/O error({e.errno}): {e.strerror}")
        except Exception:
            handle_fatal_error(f"Could not save INI preferences. Unexpected error: {sys.exc_info()[0]}")
        return False

    def write_json(self):
        try:
            folder = os.path.dirname(self.__prefsFilepath)
            Path(folder).mkdir(parents=True, exist_ok=True)
            with open(self.__prefsFilepath, 'w', encoding='utf-8', newline="\n") as configFile:
                configFile.write(json.dumps(self.__settings, indent=2))
            return True
        except OSError as e:
            print(f"Could not save JSON preferences. I/O error({e.errno}): {e.strerror}")
        except Exception:
            print(f"Could not save JSON preferences. Unexpected error: {sys.exc_info()[0]}")
        return False

    def copy_ldraw_parameters(self, ldraw_parameters_file, addon_ldraw_parameters_file):
        try:
            copyfile(ldraw_parameters_file, addon_ldraw_parameters_file)
        except IOError as e:
            print(f"Could not Copy LDraw parameters. I/O error({e.errno}): {e.strerror}")

    def evaluate_value(self, x):
        if x == 'True':
            return True
        elif x == 'False':
            return False
        elif self.is_int(x):
            return int(x)
        elif self.is_float(x):
            return float(x)
        else:
            return x

    def is_float(self, x):
        try:
            f = float(x)
        except (TypeError, ValueError):
            return False
        else:
            return True

    def is_int(self, x):
        try:
            f = float(x)
            i = int(f)
        except (TypeError, ValueError):
            return False
        else:
            return f == i

    def importer(self):
        return self.__sectionName

if __name__ == "__main__":
    print("Marshall {0} LDraw Blender settings.".format(Preferences.importer()), end=f"\n{'-' * 34}\n")