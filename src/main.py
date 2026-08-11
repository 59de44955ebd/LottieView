import base64
import json
import os
import sys
import traceback
import zipfile

APP_NAME = 'LottieView'
APP_VERSION = '0.2'
APP_DIR = os.path.dirname(__file__)
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(APP_DIR)

from webview2.standalone import *
from webview2.winapp.common_structs import SHELLEXECUTEINFOW
from resources import *

if IS_FROZEN:
    HMOD_RESOURCES = kernel32.GetModuleHandleW(None)
else:
    HMOD_RESOURCES = kernel32.LoadLibraryW(os.path.join(APP_DIR, 'resources.dll'))

SETTINGS.DEFAULT_CONTEXT_MENUS_ENABLED = False

# Use a local profile folder
if IS_FROZEN:
    SETTINGS.USER_DATA_FOLDER = os.path.join(APP_DIR, 'profile')

# Allow to use a custom runtime (download .cab and extract e.g. with 7-Zip as local folder 'runtime')
if os.path.isdir(os.path.join(APP_DIR, 'runtime')):
    SETTINGS.BROWSER_EXECUTABLE_FOLDER = os.path.join(APP_DIR, 'runtime')

TMP_DIR = os.environ['TMP']


########################################
#
########################################
class Main(WebView2):

    ########################################
    #
    ########################################
    def __init__(self):
        super().__init__(
            window_title = APP_NAME,
            h_accel = user32.LoadAcceleratorsW(HMOD_RESOURCES, LPCWSTR(1)),
            h_icon = user32.LoadIconW(HMOD_RESOURCES, LPCWSTR(1)),
            h_menu = user32.LoadMenuW(HMOD_RESOURCES, LPCWSTR(1)),
        )
        self.set_virtual_host_name_to_folder_mapping('app', os.path.join(APP_DIR, 'app'))
        self.load_url('https://app/index.html')

    ########################################
    #
    ########################################
    def on_menu(self, webview, idm):

        if idm == IDM_OPEN:
            self.open_file()

        elif idm == IDM_PRINT:
            self.show_print_ui()

        elif idm == IDM_EXIT:
            self.close()

        elif idm == IDM_FULLSCREEN:
            self.toggle_fullscreen()

        elif idm == IDM_ESCAPE_FULLSCREEN:
            self.escape_fullscreen()

        elif idm == IDM_ABOUT:
            self.about()

        elif idm == IDM_CHECK_UPDATE:
            self.check_update()

        elif idm == IDM_DEV_TOOLS:
            self.open_dev_tools()

    ########################################
    #
    ########################################
    def open_file(self):
        filename = self.show_open_file_dialog(
            title = 'Open File',
            filter_string = 'Lottie Files (*.lottie *.lottie_json *.json)\0*.lottie;*.lottie_json;*.json\0SVG Files (*.svg)\0*.svg\0\0'
        )
        if filename:
            self.load_file(filename)

    ########################################
    #
    ########################################
    def about(self):
        self.show_message_box(
            (
                f'{APP_NAME} v{APP_VERSION}\n\n'
                'A simple and small Windows desktop viewer for Lottie animation files (JSON and dotLottie) as well as SVG files.\n\n'
            ),
            'About'
        )

    ########################################
    #
    ########################################
    def check_update(self):
        command = f'"{os.path.join(APP_DIR, "update.ps1")}" "{APP_NAME}" {APP_VERSION} "https://github.com/59de44955ebd/{APP_NAME}"'
        if os.path.isfile(os.path.join(os.path.dirname(sys.executable), 'uninstall.exe')):
            command += f' "{APP_NAME}-x64-setup.exe"'
        sei = SHELLEXECUTEINFOW()
        sei.lpFile = 'powershell.exe'
        sei.lpParameters = command
        shell32.ShellExecuteExW(byref(sei))

    ########################################
    #
    ########################################
    def on_files_dropped(self, webview, files, target_id):
        self.load_file(files[0])

    ########################################
    #
    ########################################
    def load_file(self, filename):
        _, ext = os.path.splitext(filename.lower())
        if ext == '.json' or ext == '.lottie_json':
            self.load_json(filename)
        elif ext == '.lottie':
            self.load_lottie(filename)
        elif ext == '.svg':
            self.load_svg(filename)
        else:
            return
        self.set_window_title(f'{filename} - {APP_NAME}')

    ########################################
    #
    ########################################
    def load_json(self, filename):
        with open(filename, 'r') as f:
            json_data = f.read()
        self.execute_js(f"loadJSON({json_data});")

    ########################################
    #
    ########################################
    def load_lottie(self, filename):
        basename = os.path.basename(filename)
        target_dir = os.path.join(TMP_DIR, basename)
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        manifest = os.path.join(target_dir, 'manifest.json')
        if not os.path.isfile(manifest):
            return
        with open(manifest, 'r') as f:
            infos = json.loads(f.read())
        json_file = os.path.join(target_dir, 'animations', infos['animations'][0]['id'] + '.json')
        with open(json_file, 'r') as f:
            json_data = f.read()
        self.execute_js(f"loadJSON({json_data});")

    ########################################
    #
    ########################################
    def load_svg(self, filename):
        with open(filename, 'rb') as f:
            base64_bytes = base64.b64encode(f.read())
        data_uri = 'data:image/svg+xml;base64,' + base64_bytes.decode("ascii")
        self.execute_js(f"loadSVG('{data_uri}');")

    ########################################
    #
    ########################################
    def on_dom_content_loaded(self, webview):
        self.connect(EVENT.FILES_DROPPED, self.on_files_dropped)
        if len(sys.argv) > 1:
            self.load_file(sys.argv[1])


if __name__ == '__main__':
    sys.excepthook = traceback.print_exception
    Main().run()
