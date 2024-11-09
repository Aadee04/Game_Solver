import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, \
    QDesktopWidget
from PyQt5.QtCore import Qt

from PuzzleApp import PuzzleApp
from next import PuzzleApp1


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Page")
        self.setGeometry(100, 100, 600, 400)  # Adjusted to a larger size for better display
        self.center_window()

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.init_ui()

    def init_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # Center the layout

        # Title label for better UX
        title_label = QLabel("Welcome to the Puzzle Solver Suite")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)

        # Adding buttons in a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # Space between buttons

        # 8-Puzzle Solver button
        open_puzzle_button8 = QPushButton("Open 8-Puzzle Solver")
        open_puzzle_button8.setStyleSheet("font-size: 18px; padding: 10px;")
        open_puzzle_button8.clicked.connect(self.open_puzzle_solver8)

        # 15-Puzzle Solver button
        open_puzzle_button15 = QPushButton("Open 15-Puzzle Solver")
        open_puzzle_button15.setStyleSheet("font-size: 18px; padding: 10px;")
        open_puzzle_button15.clicked.connect(self.open_puzzle_solver15)

        # Add buttons to the horizontal layout
        button_layout.addWidget(open_puzzle_button8)
        button_layout.addWidget(open_puzzle_button15)

        # Add widgets to the main layout
        main_layout.addWidget(title_label)
        main_layout.addLayout(button_layout)

        # Set the layout to the central widget
        self.main_widget.setLayout(main_layout)

    def center_window(self):
        # Get the screen's geometry
        screen_geometry = QDesktopWidget().availableGeometry()
        # Calculate the center position
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        # Move the window to the center
        self.move(center_x, center_y)


    def open_puzzle_solver8(self):
        # Open the 8-puzzle solver page
        self.puzzle_solver = PuzzleApp1([1, 2, 3, 4, 5, 6, 7, 8, 0],  # Initial state for 8-puzzle
                                        [1, 2, 3, 4, 5, 6, 7, 8, 0],  # Goal state for 8-puzzle
                                        "A*")  # You can choose the algorithm
        self.puzzle_solver.show()

    def open_puzzle_solver15(self):
        # Open the 15-puzzle solver page
        self.puzzle_solver = PuzzleApp([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0],  # Initial state for 15-puzzle
                                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0],  # Goal state for 15-puzzle
                                        "A*")  # You can choose the algorithm
        self.puzzle_solver.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
