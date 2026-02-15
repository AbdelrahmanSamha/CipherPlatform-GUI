from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from ui.sidebar import Sidebar
from ui.pages.block_lab_page import BlockLabPage
from ui.pages.placeholder_page import PlaceholderPage
from ui.pages.configuration_page import ConfigPage
from ui.pages.stream_page import StreamPage
from ui.pages.rng_page import RNGPage
from ui.pages.test_page import UartTestPage
from ui.pages.image_page import ImagePage
from ui.pages.sha256_page import Sha256Page
from ui.pages.metrics_page import MetricsPage 

class MainWindow(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.setWindowTitle("XLR8 Control Panel")
        self.resize(1000, 600)

        # Left sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_selected.connect(self.change_page)

        # Right content area (stacked pages)
        self.pages = QStackedWidget()

        # Pages
        self.config_page = ConfigPage(controller)
        self.block_lab = BlockLabPage(controller)
        self.streaming_page = StreamPage(controller)
        self.rng_page = RNGPage(controller)
        self.metrics_page = MetricsPage(controller)
        self.test_page = UartTestPage(controller)
        self.image_page = ImagePage(controller)
        self.sha256_page = Sha256Page(controller)
        

        self.pages.addWidget(self.config_page)     # index 0
        self.pages.addWidget(self.block_lab)       # index 1
        self.pages.addWidget(self.streaming_page)  # index 2
        self.pages.addWidget(self.image_page)      # index 3
        self.pages.addWidget(self.sha256_page)     # index 4
        self.pages.addWidget(self.rng_page)        # index 5
        self.pages.addWidget(self.metrics_page)    # index 6
        self.pages.addWidget(self.test_page)       #index 7

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages, stretch=1)

        self.setLayout(layout)

    def change_page(self, page_name):
        if page_name == "config":
            self.pages.setCurrentIndex(0)
        elif page_name == "block":
            self.pages.setCurrentIndex(1)
        elif page_name == "stream":
            self.pages.setCurrentIndex(2)
        elif page_name == "image": 
            self.pages.setCurrentIndex(3)
        elif page_name =="sha":
            self.pages.setCurrentIndex(4)
        elif page_name == "rng":
            self.pages.setCurrentIndex(5)
        elif page_name =="metrics": 
            self.pages.setCurrentIndex(6)
        elif page_name =="test": 
            self.pages.setCurrentIndex(7)
