from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from pyray.color import Color
from pyray.point_3d import Point3D
from pyray.renderer import Renderer
from pyray.scene import Scene
from pyray.sphere import Sphere
from functools import partial
import time


class WorkerThread(QThread):
    # Define a signal to emit a message when the thread finishes
    finished_signal = Signal(str)
    progress_signal = Signal(int)

    def __init__(self, renderer):
        super().__init__()
        self.renderer = renderer
        self.stop_flag = False

    def run(self):
        samples = 0
        while not self.stop_flag:
            self.renderer.calculate()
            self.progress_signal.emit(samples)
            samples += 1
            self.msleep(5)
        message = "Thread finished"
        self.finished_signal.emit(message)

    def quit(self) -> None:
        self.stop_flag = True
        return super().quit()


class Window(QWidget):
    def __init__(self, window_dimensions, render_resolution, parent=None) -> None:
        super().__init__(parent)
        self.width, self.height = window_dimensions
        self.render_width, self.render_height = render_resolution
        self.viewport_width, self.viewport_height = 700, 700
        self.img = QImage(self.render_width, self.render_height, QImage.Format.Format_ARGB32)
        self.settings = None
        self.viewport = None

        self.renderer = None
        self.scene = None

        self.init_ui()
        self.init_renderer()

    def init_ui(self):
        self.setWindowTitle("PyRay")
        self.setGeometry(100, 100, self.width, self.height)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.viewport = QLabel()
        self.viewport.setFixedSize(self.viewport_width, self.viewport_height)

        settings_widget = QWidget()
        settings_widget.setFixedSize(self.width - self.viewport_width, self.viewport_height)
        settings_layout = QVBoxLayout()

        load_scene_1_btn = QPushButton("Load Scene 1")
        load_scene_1_btn.clicked.connect(partial(self.load_scene, 1))
        settings_layout.addWidget(load_scene_1_btn)

        load_scene_2_btn = QPushButton("Load Scene 2")
        load_scene_2_btn.clicked.connect(partial(self.load_scene, 2))
        settings_layout.addWidget(load_scene_2_btn)

        load_scene_3_btn = QPushButton("Load Scene 3")
        load_scene_3_btn.clicked.connect(partial(self.load_scene, 3))
        settings_layout.addWidget(load_scene_3_btn)

        start_render = QPushButton(text="Render")
        start_render.clicked.connect(self.start_render_thread)
        settings_layout.addWidget(start_render)

        restart_render = QPushButton("Restart Render")
        restart_render.clicked.connect(self.init_renderer)
        settings_layout.addWidget(restart_render)

        stop_render = QPushButton("Stop Render")
        stop_render.clicked.connect(self.stop_worker_thread)
        settings_layout.addWidget(stop_render)

        self.progress_label = QLabel("Progress:")
        settings_layout.addWidget(self.progress_label)

        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        settings_widget.setLayout(settings_layout)

        main_layout.addWidget(self.viewport)
        main_layout.addWidget(settings_widget)

        self.setLayout(main_layout)

        self.show()

    def load_scene(self, number):
        match number:
            case 1:
                sphere1 = Sphere(Point3D(0.0, -3.5, 3.0), 2, Color(255, 255, 255), True)
                sphere2 = Sphere(Point3D(8.0, 0.0, 3.0), 6, Color(255, 0, 0), False)
                sphere3 = Sphere(Point3D(-8.0, 0.0, 3.0), 6, Color(0, 255, 0), False)
                sphere4 = Sphere(Point3D(0.0, 8.0, 3.0), 6, Color(0, 0, 255), False)
                sphere5 = Sphere(Point3D(0.0, -8.0, 3.0), 6, Color(255, 255, 255), False)
                sphere6 = Sphere(Point3D(0.0, 1.5, 3.0), 0.75, Color(0, 255, 0), False)
                sphere7 = Sphere(Point3D(0.0, 0.48, 3.0), 0.33, Color(255, 255, 255), True)
                sphere8 = Sphere(Point3D(0.0, 0.0, -7.5), 6, Color(255, 255, 255), False)
                self.scene = Scene(sphere1, sphere2, sphere3, sphere4, sphere5, sphere6, sphere7, sphere8)
            case 2:
                sphere1 = Sphere(Point3D(0.0, -3.5, 3.0), 2, Color(255, 255, 255), True)
                sphere2 = Sphere(Point3D(8.0, 0.0, 3.0), 6, Color(255, 255, 255), False)
                self.scene = Scene(sphere1, sphere2)
            case 3:
                sphere1 = Sphere(Point3D(0.0, -3.5, 3.0), 2, Color(255, 255, 255), True)
                self.scene = Scene(sphere1)

        self.init_renderer()

    def init_renderer(self):
        self.renderer = Renderer(self, self.scene, Point3D(0, 0, 10))

    def start_render_thread(self):
        self.worker_thread = WorkerThread(self.renderer)
        self.worker_thread.progress_signal.connect(self.update_progress_label)
        self.worker_thread.start()

    def stop_worker_thread(self):
        self.worker_thread.quit()

    def update_progress_label(self, progress):
        self.progress_label.setText(f"Progress: {progress} Samples")

    def update_screen(self):
        self.viewport.setPixmap(QPixmap.fromImage(self.img.scaled(self.viewport_width, self.viewport_height)))
        self.viewport.update()
        self.update()