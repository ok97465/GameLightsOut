"""Light Out Game Main."""
# Standard library imports
import sys

# Third party imports
import qdarkstyle
from qtpy.QtGui import QPixmap, QIcon, QFont
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (QApplication, QMainWindow, QToolBar, QToolButton,
                            QSpinBox, QCheckBox, QPushButton, QTableWidget,
                            QAbstractItemView, QHeaderView, QLabel, QStatusBar,
                            QMessageBox)
import qtawesome as qta

# Local imports
from lightsout import ManageLightsOutPuzzle

VER = "0.0.01"
ICON_COLOR = "#AAAAAA"
CELL_SIZE = 60
BTN_STYLE = """QPushButton {
  color: #BB2020;
  font-size: 20pt;
}

QPushButton:checked {
  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #b1b1b1, stop: 0.07 #b3b3b3,
                                    stop: 0.33 #b3b3b3, stop: 0.4 #b0b0b0,
                                    stop: 0.47 #b3b3b3, stop: 1.0 #b2b2b2);
}
"""


def create_toolbutton(parent, icon=None, tip=None, triggered=None):
    """Create a QToolButton."""
    button = QToolButton(parent)
    if icon is not None:
        button.setIcon(icon)
    if tip is not None:
        button.setToolTip(tip)
    if triggered is not None:
        button.clicked.connect(triggered)
    return button


class MainWindowLightsOut(QMainWindow):
    """Main Window."""

    def __init__(self):
        """Init Main Window."""
        super().__init__()

        # Title and set icon
        self.setWindowTitle(f"LightsOut by ok97465 - {VER}")

        icon = QIcon()
        icon.addPixmap(QPixmap(r'ok_64x64.ico'), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        # Setup toolbar
        self.toolbar = QToolBar()
        self.new_btn = None
        self.clear_btn = None
        self.n_lights_1axis_spinbox = None
        self.show_solution_chkbox = None
        self.setup_toolbar()

        # Setup Button
        self.btn_grid_table = QTableWidget(self)

        # Setup Status Bar
        self.n_clicked = 0
        self.clicked_label = QLabel("0", self)
        self.n_solution_1_label = QLabel("0", self)
        self.setup_status_bar()

        # Setup info  of lights out
        self.manage_puzzle = ManageLightsOutPuzzle()
        self.new_game()

        # Setup Main Layout
        self.setCentralWidget(self.btn_grid_table)
        self.resize_main_window()

        QTimer.singleShot(100, self.resize_main_window)

    def resize_main_window(self):
        """Resize mainwindow to fit table."""
        self.toolbar.adjustSize()
        self.statusBar().adjustSize()
        w = CELL_SIZE * self.manage_puzzle.n_lights_1axis
        w += self.btn_grid_table.frameWidth() * 2

        w = max([w, self.toolbar.width(), self.statusBar().width()])

        h = CELL_SIZE * self.manage_puzzle.n_lights_1axis
        h += self.btn_grid_table.frameWidth() * 2
        h += self.toolbar.frameSize().height()
        h += self.statusBar().height()

        self.resize(w, h)

    def new_game(self):
        """Create New Game."""
        self.manage_puzzle.new_puzzle(self.n_lights_1axis_spinbox.value())
        self.setup_btn_grid(self.manage_puzzle.n_lights_1axis)
        self.show_puzzle()
        self.n_solution_1_label.setText(
            f"{self.manage_puzzle.count_1_of_solution()}")
        self.resize_main_window()

    def setup_toolbar(self):
        """Set up toolbar."""
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        self.toolbar.setStyleSheet(
            "QToolButton {{height:{30}px;width:{30}px;}}")

        self.new_btn = create_toolbutton(
            self, qta.icon("mdi.new-box", color=ICON_COLOR),
            "Start new game.", triggered=self.new_game)
        self.toolbar.addWidget(self.new_btn)
        self.toolbar.addSeparator()

        self.clear_btn = create_toolbutton(
            self, qta.icon("fa5s.eraser", color=ICON_COLOR),
            "Click을 초기화 한다.", triggered=self.show_puzzle)
        self.toolbar.addWidget(self.clear_btn)
        self.toolbar.addSeparator()

        self.n_lights_1axis_spinbox = QSpinBox(self)
        self.n_lights_1axis_spinbox.setValue(4)
        self.n_lights_1axis_spinbox.setRange(2, 10)
        self.n_lights_1axis_spinbox.setAlignment(Qt.AlignRight)
        self.n_lights_1axis_spinbox.setToolTip(
            "Set Number of light in 1 axis.")
        self.toolbar.addWidget(self.n_lights_1axis_spinbox)
        self.toolbar.addSeparator()

        self.show_solution_chkbox = QCheckBox("Solution", self)
        self.show_solution_chkbox.setStyleSheet(""" background : "#32414B" """)
        self.show_solution_chkbox.setToolTip("Show the solution.")
        self.show_solution_chkbox.stateChanged.connect(self.show_solution)
        self.toolbar.addWidget(self.show_solution_chkbox)
        self.toolbar.addSeparator()

        self.toolbar.adjustSize()

    def setup_status_bar(self):
        """Set up status bar."""
        status_bar = QStatusBar(self)
        status_bar.addPermanentWidget(QLabel("Clicked", self))
        status_bar.addPermanentWidget(self.clicked_label)
        status_bar.addPermanentWidget(QLabel("Solution", self))
        status_bar.addPermanentWidget(self.n_solution_1_label)

        self.setStatusBar(status_bar)

    def setup_btn_grid(self, n_lights_1axis):
        """Set up grid of buttons."""
        table = self.btn_grid_table
        if n_lights_1axis != table.rowCount():
            table.clear()
            table.setSelectionMode(QAbstractItemView.NoSelection)
            table.setColumnCount(n_lights_1axis)
            table.setRowCount(n_lights_1axis)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

            table.horizontalHeader().setDefaultSectionSize(CELL_SIZE)
            table.verticalHeader().setDefaultSectionSize(CELL_SIZE)

            table.horizontalHeader().hide()
            table.verticalHeader().hide()

            for idx_row in range(n_lights_1axis):
                for idx_col in range(n_lights_1axis):
                    btn = QPushButton(self)
                    btn.setStyleSheet(BTN_STYLE)
                    btn.setCheckable(True)
                    btn.setChecked(True)
                    btn.clicked.connect(
                        self.clicked_btn_of_grid_factory(idx_row, idx_col))
                    table.setCellWidget(idx_row, idx_col, btn)
        self.show_solution()

    def clicked_btn_of_grid_factory(self, idx_row, idx_col):
        """Generate lambda function of clicked_btn_of_grid."""
        return lambda: self.clicked_btn_of_grid(idx_row, idx_col)

    def clicked_btn_of_grid(self, idx_row, idx_col):
        """Change state of button around clicked button."""
        self.change_state_btn(idx_row - 1, idx_col + 0)
        self.change_state_btn(idx_row + 1, idx_col + 0)
        self.change_state_btn(idx_row + 0, idx_col - 1)
        self.change_state_btn(idx_row + 0, idx_col + 1)

        self.n_clicked += 1
        self.refresh_n_clicked()

        self.check_solve()

    def change_state_btn(self, idx_row, idx_col):
        """Change state of button."""
        btn = self.btn_grid_table.cellWidget(idx_row, idx_col)
        if btn is not None:
            btn.setChecked(not btn.isChecked())

    def show_solution(self):
        """Show the solution on the button."""
        n_lights = self.manage_puzzle.n_lights_1axis
        solution = self.manage_puzzle.mat_solution
        for idx_row in range(n_lights):
            for idx_col in range(n_lights):
                btn = self.btn_grid_table.cellWidget(idx_row, idx_col)
                if btn is not None:
                    if self.show_solution_chkbox.isChecked():
                        if solution[idx_row, idx_col] == 1:
                            btn.setText("◉")
                        else:
                            btn.setText("")
                    else:
                        btn.setText("")

    def refresh_n_clicked(self):
        """Refresh number of clicked."""
        self.clicked_label.setText(f"{self.n_clicked}")

    def show_puzzle(self):
        """Show puzzle."""
        n_lights = self.manage_puzzle.n_lights_1axis
        puzzle = self.manage_puzzle.mat_puzzle
        for idx_row in range(n_lights):
            for idx_col in range(n_lights):
                btn = self.btn_grid_table.cellWidget(idx_row, idx_col)
                if btn is not None:
                    if puzzle[idx_row, idx_col] == 1:
                        btn.setChecked(True)
                    else:
                        btn.setChecked(False)

        self.n_clicked = 0
        self.refresh_n_clicked()

    def check_solve(self):
        """Check if the problem is solved."""
        n_lights = self.manage_puzzle.n_lights_1axis
        for idx_row in range(n_lights):
            for idx_col in range(n_lights):
                btn = self.btn_grid_table.cellWidget(idx_row, idx_col)
                if btn is not None:
                    if btn.isChecked():
                        return

        n_solution = self.manage_puzzle.count_1_of_solution()
        QMessageBox.information(self, "Succeess",
                                ("Congratulation\n"
                                 f"clicked  : {self.n_clicked}\n"
                                 f"solution : {n_solution}"))


if __name__ == '__main__':
    APP = QApplication(sys.argv)

    style_sheet = qdarkstyle.load_stylesheet_pyqt5()
    APP.setStyleSheet(style_sheet)

    FONT = QFont("D2Coding Ligature", 12)
    FONT.setStyleHint(QFont.Monospace)
    APP.setFont(FONT)

    MAIN_WINDOW = MainWindowLightsOut()
    MAIN_WINDOW.show()

    sys.exit(APP.exec_())
