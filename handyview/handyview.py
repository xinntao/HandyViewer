import actions as actions
import glob
import os
import re
import sys
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QDockWidget, QFileDialog,
                             QGridLayout, QInputDialog, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QToolBar, QWidget)
from view_scene import HVScene, HVView
from widgets import ColorLabel, HLine, HVLable, MessageDialog, show_msg

FORMATS = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.ppm', '.PPM',
           '.bmp', '.BMP', '.gif', '.GIF', '.tiff')

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    CURRENT_PATH = sys._MEIPASS
else:
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


def get_img_list(path, include_names=None, exclude_names=None):
    img_list = []
    if path == '':
        path = './'
    # deal with include and exclude names
    for img_path in sorted(glob.glob(os.path.join(path, '*'))):
        img_path = img_path.replace('\\', '/')
        img_name = os.path.split(img_path)[-1]
        base, ext = os.path.splitext(img_name)
        if ext in FORMATS:
            if include_names is not None:
                flag_add = False
                for include_name in include_names:
                    if include_name in base:
                        flag_add = True
            elif exclude_names is not None:
                flag_add = True
                for exclude_name in exclude_names:
                    if exclude_name in base:
                        flag_add = False
            else:
                flag_add = True
            if flag_add:
                img_list.append(img_path)
    # natural sort for numbers in name
    img_list.sort(
        key=lambda s:
        [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)])
    return img_list


class Canvas(QWidget):
    """The main canvas to show the image, information panel."""

    def __init__(self, parent):
        super(Canvas, self).__init__()
        self.parent = parent
        try:
            self.key = sys.argv[1]
        except IndexError:
            # show the icon image
            self.key = os.path.join(CURRENT_PATH, 'icon.png')

        try:
            open(self.key, 'r')
        except IOError:
            print(f'There was an error opening {self.key}')
            sys.exit(1)

        # initialize widgets and layout
        self.init_widgets_layout()

        self.include_names = None
        self.exclude_names = None
        self.qview_bg_color = 'white'
        # list of image list
        # the first list is the main list, the others are for comparisons
        self.img_list = [[]]
        self.img_list_idx = 0

        if self.key.endswith(FORMATS):
            self.get_main_img_list()
            self.show_image(init=True)
        else:
            print('Unsupported file format.')
            sys.exit(1)

    def init_widgets_layout(self):
        # QGraphicsView - QGraphicsScene - QPixmap
        self.qscene = HVScene(self)
        self.qview = HVView(self.qscene, self)

        # name label showing image index and image path
        self.name_label = HVLable('', self, 'green', 'Times', 15)
        # goto edit and botton for indexing
        self.goto_edit = QLineEdit()
        self.goto_edit.setPlaceholderText('Index. Default: 1')
        goto_btn = QPushButton('GO', self)
        goto_btn.clicked.connect(self.goto_button_clicked)

        # info label showing image shape, size and color type
        self.info_label = HVLable('', self, 'blue', 'Times', 12)
        # zoom label showing zoom ratio
        self.zoom_label = HVLable('1.00', self, 'green', 'Times', 12)
        # mouse position and mouse rgb value
        mouse_pos_text = ('Cursor position:\n (ignore zoom)\n'
                          ' Height(y): 0.0\n Width(x):  0.0')
        self.mouse_pos_label = HVLable(mouse_pos_text, self, 'black', 'Times',
                                       12)
        self.mouse_rgb_label = HVLable(' (255, 255, 255, 255)', self, 'black',
                                       'Times', 12)
        # pixel color at the mouse position
        self.mouse_color_title = HVLable('RGBA:', self, 'black', 'Times', 12)
        self.mouse_color_label = ColorLabel(color=(255, 255, 255))

        # selection rectangle position and length
        selection_pos_text = ('Rect Pos: (H, W)\n Start: 0, 0\n'
                              ' End  : 0, 0\n Len  : 0, 0')
        self.selection_pos_label = HVLable(selection_pos_text, self, 'black',
                                           'Times', 12)

        # include and exclude names
        self.include_names_label = HVLable('', self, 'black', 'Times', 12)
        self.exclude_names_label = HVLable('', self, 'black', 'Times', 12)
        # comparison folders
        self.comparison_label = HVLable('', self, 'red', 'Times', 12)

        # ---------
        # layouts
        # ---------
        main_layout = QGridLayout(self)
        # QGridLayout:
        # int row, int column, int rowSpan, int columnSpan
        main_layout.addWidget(self.name_label, 0, 0, 1, 50)

        name_grid = QGridLayout()
        name_grid.addWidget(self.goto_edit, 0, 0, 1, 1)
        name_grid.addWidget(goto_btn, 0, 1, 1, 1)
        main_layout.addLayout(name_grid, 1, 0, 1, 10)

        main_layout.addWidget(self.qview, 0, 0, -1, 50)
        # blank label for layout
        blank_label = HVLable('', self, 'black', 'Times', 12)
        main_layout.addWidget(blank_label, 61, 0, 1, 1)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F9:
            self.toggle_bg_color()
        elif event.key() == QtCore.Qt.Key_R:
            self.qview.set_zoom(1)
        elif event.key() == QtCore.Qt.Key_C:
            self.compare_folders(1)
        elif event.key() == QtCore.Qt.Key_V:
            self.compare_folders(-1)
        elif event.key() == QtCore.Qt.Key_Space:
            self.dir_browse(1)
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.dir_browse(-1)
        elif event.key() == QtCore.Qt.Key_Right:
            self.dir_browse(1)
        elif event.key() == QtCore.Qt.Key_Left:
            self.dir_browse(-1)
        elif event.key() == QtCore.Qt.Key_Up:
            self.qview.zoom_in()
        elif event.key() == QtCore.Qt.Key_Down:
            self.qview.zoom_out()

    def goto_button_clicked(self):
        goto_str = self.goto_edit.text()
        if goto_str == '':
            self.dirpos = 0
        elif goto_str.isdigit():
            self.dirpos = int(goto_str) - 1
        else:
            return
        self.key = self.img_list[self.img_list_idx][self.dirpos]
        self.show_image()

    def get_main_img_list(self):
        # if key is a folder, get the first image path
        if os.path.isdir(self.key):
            self.key = sorted(glob.glob(os.path.join(self.key, '*')))[0]

        # fix the key pattern passed from windows system when double click
        self.key = self.key.replace('\\', '/')

        if self.key.endswith(FORMATS):
            # get image list
            self.path, self.img_name = os.path.split(self.key)
            self.img_list[self.img_list_idx] = get_img_list(
                self.path, self.include_names, self.exclude_names)
            # get current position
            try:
                self.dirpos = self.img_list[self.img_list_idx].index(self.key)
            except ValueError:
                # self.key may not in self.img_list after refreshing
                self.dirpos = 0
            # save open file history
            self.save_open_history()
        else:
            show_msg('Critical', 'Critical', f'Wrong key! {self.key}')

    def update_cmp_img_list(self, cmp_path):
        path, _ = os.path.split(cmp_path)
        self.img_list.append(
            get_img_list(path, self.include_names, self.exclude_names))
        # all the image list should have the same length
        all_same_len = True
        lens_img_list = [len(self.img_list[0])]
        for img_list in self.img_list[1:]:
            lens_img_list.append(len(img_list))
            if len(img_list) != lens_img_list[0]:
                all_same_len = False

        show_str = 'Number for each folder:\n\t' + '\n\t'.join(
            map(str, lens_img_list))
        self.comparison_label.setText(show_str)
        if all_same_len is False:
            msg = ('Comparison folders have differnet number of images.\n'
                   f'{show_str}')
            show_msg('Warning', 'Warning!', msg)

    def compare_folders(self, direction):
        if len(self.img_list) > 1:
            self.img_list_idx += direction
            if self.img_list_idx > (len(self.img_list) - 1):
                self.img_list_idx = 0
            elif self.img_list_idx < 0:
                self.img_list_idx = (len(self.img_list) - 1)
            try:
                self.key = self.img_list[self.img_list_idx][self.dirpos]
            except IndexError:
                self.dirpos = len(self.img_list[self.img_list_idx]) - 1
                self.key = self.img_list[self.img_list_idx][self.dirpos]
            self.show_image()
            # when in main folder (1st folder), show red color
            if self.img_list_idx == 0:
                self.comparison_label.setStyleSheet('QLabel {color : red;}')
            else:
                self.comparison_label.setStyleSheet('QLabel {color : black;}')

    def save_open_history(self):
        try:
            with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                if len(lines) == 5:
                    del lines[-1]
        except Exception:
            lines = []
        # add the new record to the first line
        if self.key not in ['icon.png', './icon.png'] and (self.key
                                                           not in lines):
            lines.insert(0, self.key)
        with open(os.path.join(CURRENT_PATH, 'history.txt'), 'w') as f:
            for line in lines:
                f.write(f'{line}\n')

    def show_image(self, init=False):
        self.qscene.clear()
        self.qimg = QImage(self.key)
        self.qpixmap = QPixmap.fromImage(self.qimg)
        self.qscene.addPixmap(self.qpixmap)
        self.imgw, self.imgh = self.qpixmap.width(), self.qpixmap.height()
        # put image always in the center of a QGraphicsView
        self.qscene.setSceneRect(0, 0, self.imgw, self.imgh)
        # show image path in the statusbar
        self.parent.set_statusbar(f'{self.key}')

        try:
            with Image.open(self.key) as lazy_img:
                self.color_type = lazy_img.mode
        except FileNotFoundError:
            show_msg('Critical', 'Critical', f'Cannot open {self.key}')

        # update information panel
        self.path, self.img_name = os.path.split(self.key)
        self.file_size = sizeof_fmt(os.path.getsize(self.key))
        self.name_label.setText(f'[{self.dirpos + 1:d} / '
                                f'{len(self.img_list[self.img_list_idx]):d}] '
                                f'{self.img_name}')
        self.info_label.setText(
            'Info: \n'
            f' Height: {self.imgh:d}\n Width:  {self.imgw:d}\n'
            f' Size: {self.file_size}\n Type: {self.color_type}')

        if init:
            if self.imgw < 500:
                self.qview.set_zoom(500 // self.imgw)
            else:
                self.qview.set_zoom(1)
        self.qview.set_transform()

    def dir_browse(self, direction):
        if len(self.img_list[self.img_list_idx]) > 1:
            self.dirpos += direction
            if self.dirpos > (len(self.img_list[self.img_list_idx]) - 1):
                self.dirpos = 0
            elif self.dirpos < 0:
                self.dirpos = (len(self.img_list[self.img_list_idx]) - 1)
            self.key = self.img_list[self.img_list_idx][self.dirpos]
            self.show_image()

    def toggle_bg_color(self):
        """Toggle background color."""
        if self.qview_bg_color == 'white':
            self.qview_bg_color = 'gray'
            self.qscene.setBackgroundBrush(QtCore.Qt.gray)
        else:
            self.qview_bg_color = 'white'
            self.qscene.setBackgroundBrush(QtCore.Qt.white)


class MainWindow(QMainWindow):
    """The main window."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('HandyView')
        self.init_menubar()
        self.init_toolbar()
        self.init_statusbar()
        self.init_central_window()
        self.add_dock_window()

    def init_menubar(self):
        # create menubar
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(actions.open(self))
        file_menu.addAction(actions.refresh(self))
        file_menu.addAction(actions.include_file_name(self))
        file_menu.addAction(actions.exclude_file_name(self))
        file_menu.addAction(actions.history(self))

        # Edit
        edit_menu = menubar.addMenu('&Edit')  # noqa: F841

        # Draw
        draw_menu = menubar.addMenu('&Draw')  # noqa: F841

        # Compare
        compare_menu = menubar.addMenu('&Compare')
        compare_menu.addAction(actions.compare(self))

        # View
        self.view_menu = menubar.addMenu('&View')

        # Help
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(actions.show_instruction_msg(self))

    def init_toolbar(self):
        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(actions.open(self))
        self.toolbar.addAction(actions.refresh(self))
        self.toolbar.addAction(actions.include_file_name(self))
        self.toolbar.addAction(actions.exclude_file_name(self))
        self.toolbar.addAction(actions.compare(self))
        self.toolbar.addAction(actions.history(self))
        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(actions.show_instruction_msg(self))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def init_statusbar(self):
        self.statusBar().showMessage('Welcome to HandyView.')

    def set_statusbar(self, text):
        self.statusBar().showMessage(text)

    def init_central_window(self):
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

    def add_dock_window(self):
        # Info
        dock_info = QDockWidget('Information Panel', self)
        dock_info.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea
                                  | QtCore.Qt.RightDockWidgetArea)
        # not show close button
        dock_info.setFeatures(QDockWidget.DockWidgetMovable
                              | QDockWidget.DockWidgetFloatable)
        dockedWidget = QWidget()
        dock_info.setWidget(dockedWidget)
        layout = QGridLayout()
        layout.addWidget(self.canvas.info_label, 0, 0, 1, 3)
        layout.addWidget(self.canvas.zoom_label, 1, 0, 1, 3)
        layout.addWidget(self.canvas.mouse_pos_label, 2, 0, 1, 3)
        color_grid = QGridLayout()
        color_grid.addWidget(self.canvas.mouse_color_title, 0, 0, 1, 1)
        color_grid.addWidget(self.canvas.mouse_color_label, 0, 1, 1, 3)
        color_grid.addWidget(self.canvas.mouse_rgb_label, 1, 0, 1, 3)
        layout.addLayout(color_grid, 3, 0, 1, 3)
        layout.addWidget(HLine(), 4, 0, 1, 3)
        layout.addWidget(self.canvas.selection_pos_label, 5, 0, 1, 3)
        layout.addWidget(HLine(), 6, 0, 1, 3)
        layout.addWidget(self.canvas.include_names_label, 7, 0, 1, 3)
        layout.addWidget(self.canvas.exclude_names_label, 8, 0, 1, 3)
        layout.addWidget(self.canvas.comparison_label, 9, 0, 1, 3)

        # for compact space
        blank_qlabel = QLabel()
        layout.addWidget(blank_qlabel, 7, 0, 20, 3)
        dockedWidget.setLayout(layout)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_info)

    # --------
    # Slots
    # --------

    def open_file_dialog(self):
        try:
            with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
                history = f.readlines()[0]
                history = history.strip()
        except Exception:
            history = '.'
        key, ok = QFileDialog.getOpenFileName(self, 'Select an image', history)
        if ok:
            self.canvas.key = key
            self.canvas.get_main_img_list()
            self.canvas.show_image(init=True)

    def refresh_img_list(self):
        self.canvas.get_main_img_list()
        self.canvas.show_image(init=False)
        # TODO: update comparison image list

    def compare_folder(self):
        key, ok = QFileDialog.getOpenFileName(
            self, 'Select an image', os.path.join(self.canvas.path, '../'))
        if ok:
            self.canvas.update_cmp_img_list(key)

    def open_history(self):
        with open(os.path.join(CURRENT_PATH, 'history.txt'), 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
        key, ok = QInputDialog().getItem(self, 'Open File History', 'History:',
                                         lines, 0, True)
        if ok:
            self.canvas.key = key
            self.canvas.get_main_img_list()
            self.canvas.show_image(init=True)

    def exclude_file_name(self):
        # show current exclude names as the default values
        current_exclude_names = self.canvas.exclude_names
        if current_exclude_names is None:
            current_exclude_names = ''
        else:
            current_exclude_names = ', '.join(current_exclude_names)

        exclude_names, ok = QInputDialog.getText(self, 'Exclude file name',
                                                 'Key word (seperate by ,):',
                                                 QLineEdit.Normal,
                                                 current_exclude_names)
        if ok:
            if exclude_names != '':
                self.canvas.exclude_names = [
                    v.strip() for v in exclude_names.split(',')
                ]
                self.canvas.include_names = None
            else:
                self.canvas.exclude_names = None
            self.refresh_img_list()

        # show exclude names in the information panel
        if isinstance(self.canvas.exclude_names, list):
            show_str = 'Exclude:\n\t' + '\n\t'.join(self.canvas.exclude_names)
            self.canvas.exclude_names_label.setStyleSheet(
                'QLabel {color : red;}')
        else:
            show_str = 'Exclude: None'
            self.canvas.exclude_names_label.setStyleSheet(
                'QLabel {color : black;}')
        self.canvas.exclude_names_label.setText(show_str)

    def include_file_name(self):
        # show current include names as the default values
        current_include_names = self.canvas.include_names
        if current_include_names is None:
            current_include_names = ''
        else:
            current_include_names = ', '.join(current_include_names)

        include_names, ok = QInputDialog.getText(self, 'Include file name',
                                                 'Key word (seperate by ,):',
                                                 QLineEdit.Normal,
                                                 current_include_names)
        if ok:
            if include_names != '':
                self.canvas.include_names = [
                    v.strip() for v in include_names.split(',')
                ]
                self.canvas.exclude_names = None
            else:
                self.canvas.include_names = None
            self.refresh_img_list()

        # show include names in the information panel
        if isinstance(self.canvas.include_names, list):
            show_str = 'Include:\n\t' + '\n\t'.join(self.canvas.include_names)
            self.canvas.include_names_label.setStyleSheet(
                'QLabel {color : blue;}')
        else:
            show_str = 'Include: None'
            self.canvas.include_names_label.setStyleSheet(
                'QLabel {color : black;}')
        self.canvas.include_names_label.setText(show_str)

    def show_instruction_msg(self):
        instruct_text = r'''
        Mouse wheel : Previous/Next image
        Ctrl + Mouse wheel: Zoom in/out

        A D: Previous/Next image
        W S: Zoom in/out
        Direction key ← → : Horizontal scrolling
        Direction key ↑ ↓ : Vertical scrolling
        F9 : Change background color (white or gray)
        R : Reset zoom ration to 1
        Space : Next image
        Backspace: Previous image
        '''
        instruct_text_cn = r'''
        鼠标滚轮 : 上一张/下一张 图像
        Ctrl + 鼠标滚轮: 放大/缩小

        A D: 上一张/下一张 图像
        W S: 放大/缩小
        方向键 ← → : 水平滚动
        方向键 ↑ ↓ : 垂直滚动
        F9 : 切换背景颜色 (白色/灰色)
        R : 重置放大比率为1
        Space : 下一张 图像
        Backspace: 上一张 图像
        '''
        msg = MessageDialog(self, instruct_text, instruct_text_cn)
        msg.setStyleSheet('QLabel{min-width:500 px; font-size: 20px;}')
        msg.setWindowTitle('Instructions')
        msg.exec_()


def sizeof_fmt(size, suffix='B'):
    """Get human readable file size.
    Args:
        size (int): File size.
        suffix (str): Suffix. Default: 'B'.
    Return:
        str: Formated file siz.
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(size) < 1024.0:
            return f'{size:3.1f} {unit}{suffix}'
        size /= 1024.0
    return f'{size:3.1f} Y{suffix}'


if __name__ == '__main__':
    import platform
    if platform.system() == 'Windows':
        # set the icon in the task bar
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            'HandyView')
    print('Welcome to HandyView.')

    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    size = screen.size()
    # rect = screen.availableGeometry()

    main = MainWindow()
    main.setWindowIcon(QIcon('icon.ico'))
    main.setGeometry(0, 0, size.width(),
                     size.height())  # (left, top, width, height)
    main.showMaximized()

    # change status bar info
    main.set_statusbar(
        f'Screen: {screen.name()} with size {size.width()} x {size.height()}.')
    sys.exit(app.exec_())
