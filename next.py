import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, \
    QLabel, QComboBox, QDesktopWidget
import heapq
import time
from PyQt5.QtCore import QTimer, Qt, QElapsedTimer
from PyQt5.QtGui import QColor, QPalette


class PuzzleState:
    def __init__(self, board, parent=None, move=None, depth=0, cost=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.cost = cost
        self.zero_index = board.index(0)

    def __lt__(self, other):
        return self.cost < other.cost

    def get_neighbors(self):
        neighbors = []
        row, col = divmod(self.zero_index, 3)
        moves = {
            'UP': (row - 1, col),
            'DOWN': (row + 1, col),
            'LEFT': (row, col - 1),
            'RIGHT': (row, col + 1),
        }

        for move, (r, c) in moves.items():
            if 0 <= r < 3 and 0 <= c < 3:
                new_zero_index = r * 3 + c
                new_board = self.board[:]
                new_board[self.zero_index], new_board[new_zero_index] = new_board[new_zero_index], new_board[
                    self.zero_index]
                neighbors.append(PuzzleState(new_board, self, move, self.depth + 1))

        return neighbors


def heuristic(board, goal):
    distance = 0
    for i, value in enumerate(board):
        if value == 0:
            continue
        goal_index = goal.index(value)
        distance += abs(goal_index // 3 - i // 3) + abs(goal_index % 3 - i % 3)
    return distance


def reconstruct_path(state):
    path = []
    while state.parent:
        path.append(state.move)
        state = state.parent
    path.reverse()
    return path


def a_star_search(initial, goal):
    open_list = []
    closed_set = set()

    start_state = PuzzleState(initial)
    start_state.cost = heuristic(initial, goal)
    heapq.heappush(open_list, start_state)

    while open_list:
        current_state = heapq.heappop(open_list)

        if current_state.board == goal:
            return reconstruct_path(current_state)

        closed_set.add(tuple(current_state.board))

        for neighbor in current_state.get_neighbors():
            if tuple(neighbor.board) in closed_set:
                continue

            neighbor.cost = neighbor.depth + heuristic(neighbor.board, goal)
            heapq.heappush(open_list, neighbor)

    return None


def greedy_best_first_search(initial, goal):
    open_list = []
    closed_set = set()

    start_state = PuzzleState(initial)
    start_state.cost = heuristic(initial, goal)
    heapq.heappush(open_list, start_state)

    while open_list:
        current_state = heapq.heappop(open_list)

        if current_state.board == goal:
            return reconstruct_path(current_state)

        closed_set.add(tuple(current_state.board))

        for neighbor in current_state.get_neighbors():
            if tuple(neighbor.board) in closed_set:
                continue

            neighbor.cost = heuristic(neighbor.board, goal)  # Only heuristic, ignoring path cost
            heapq.heappush(open_list, neighbor)

    return None


class HoverButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(80, 80)
        self.setStyleSheet(self.get_button_style())

    def enterEvent(self, event):
        # On hover, change background color for the puzzle buttons
        self.setStyleSheet(self.get_button_hover_style())
        super().enterEvent(event)

    def leaveEvent(self, event):
        # On leave, reset background color for the puzzle buttons
        self.setStyleSheet(self.get_button_style())
        super().leaveEvent(event)

    def get_button_style(self):
        return (
            "background-color: #4CAF50; "  # Green color for puzzle buttons
            "border-radius: 10px; "
            "color: white; "
            "font-size: 20px; "
            "font-weight: bold; "
            "padding: 5px;"
        )

    def get_button_hover_style(self):
        return (
            "background-color: #45a049; "  # Slightly darker shade for hover effect
            "border-radius: 10px; "
            "color: white; "
            "font-size: 20px; "
            "font-weight: bold; "
            "padding: 5px;"
        )



class SolveButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(120, 70)  # Slightly larger for visibility
        self.setStyleSheet(self.get_solve_button_style())

    def get_solve_button_style(self):
        return (
            "background-color: #FF9800; "  # Orange color, no hover effect
            "border-radius: 10px; "
            "color: white; "
            "font-size: 18px; "
            "font-weight: bold; "
            "padding: 15px; "
            "margin-top: 20px;"
        )


class PuzzleApp1(QWidget):
    def __init__(self, initial_board, goal_board, algorithm_type):
        super().__init__()
        self.initial_board = initial_board
        self.goal_board = goal_board
        self.board = initial_board[:]
        self.algorithm_type = algorithm_type  # Store the selected algorithm type
        self.buttons = []
        self.is_goal_state_editing = False  # Flag to toggle between goal state editing
        self.init_ui()

        # Initialize solver_running to track if the solver is running
        self.solver_running = False

        # Timer initialization
        self.elapsed_timer = QElapsedTimer()  # Using QElapsedTimer instead of time.time()
        self.elapsed_time = 0

    def init_ui(self):
        self.setWindowTitle("Puzzle Solver")
        self.setGeometry(100, 100, 300, 500)

        # Center the window on the screen
        self.center_window()

        # Set a background color for the window
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(235, 235, 235))  # Light grey background
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Title label with improved styling
        title_label = QLabel(f"{len(self.board)}-Puzzle Solver")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 23px; font-weight: bold; color: #2E3B3E; padding-bottom: 20px;")
        layout.addWidget(title_label)

        # Grid layout for puzzle buttons
        grid_layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                if idx < len(self.board):  # Ensure that index does not go out of range
                    button = HoverButton(str(self.board[idx]) if self.board[idx] != 0 else '')
                    button.clicked.connect(lambda checked, idx=idx: self.move_tile(idx))
                    grid_layout.addWidget(button, i, j)
                    self.buttons.append(button)

        layout.addLayout(grid_layout)

        # Algorithm selector dropdown (white text)
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(["A*", "Greedy Best First"])
        self.algorithm_selector.setStyleSheet(
            "font-size: 16px; color: white; padding: 5px; background-color: #2E3B3E;")  # White text and dark background
        layout.addWidget(self.algorithm_selector)  # Add dropdown to layout

        # Center the Solve button and make it orange (using SolveButton)
        solve_button_layout = QHBoxLayout()
        solve_button = SolveButton("Solve")  # Use SolveButton instead of HoverButton
        solve_button.clicked.connect(self.solve_puzzle)
        solve_button_layout.addWidget(solve_button)
        solve_button_layout.setAlignment(Qt.AlignCenter)  # Center align the button
        layout.addLayout(solve_button_layout)

        # Goal State toggle button
        self.goal_state_button = QPushButton("Edit Goal State")
        self.goal_state_button.setStyleSheet(
            "font-size: 18px; color: white; background-color: #2196F3; border-radius: 10px; padding: 10px;")
        self.goal_state_button.clicked.connect(self.toggle_goal_state)
        layout.addWidget(self.goal_state_button)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #2E3B3E; padding-top: 20px;")
        layout.addWidget(self.status_label)

        self.timer_label = QLabel("Time Elapsed: 0s")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 16px; color: #2E3B3E; padding-top: 10px;")
        layout.addWidget(self.timer_label)

        self.setLayout(layout)
        self.show()

    def center_window(self):
        # Get the screen's geometry
        screen_geometry = QDesktopWidget().availableGeometry()
        # Calculate the center position
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        # Move the window to the center
        self.move(center_x, center_y)

    def toggle_goal_state(self):
        """Toggle between editing and viewing the goal state."""
        if self.is_goal_state_editing:
            # Save the goal state when exiting edit mode
            self.goal_board = self.board[:]
            self.goal_state_button.setText("Edit Goal State")
            self.status_label.setText("Goal state saved.")
        else:
            self.goal_state_button.setText("Save Goal State")
            self.status_label.setText("Edit the goal state.")
        self.is_goal_state_editing = not self.is_goal_state_editing
        self.update_ui()  # Refresh the UI to show the changes

    def move_tile(self, idx):
        """Move a tile if possible. Only allow tile movements in goal state edit mode."""
        if self.is_goal_state_editing:
            zero_index = self.board.index(0)
            row, col = divmod(idx, 3)
            zero_row, zero_col = divmod(zero_index, 3)

            if abs(row - zero_row) + abs(col - zero_col) == 1:
                self.board[zero_index], self.board[idx] = self.board[idx], self.board[zero_index]
                self.update_ui()

    def update_ui(self):
        """Update the UI after any state change."""
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                if idx < len(self.board):
                    self.buttons[idx].setText(str(self.board[idx]) if self.board[idx] != 0 else '')

    def get_button_style(self):
        return (
            "background-color: #3CAF50; "
            "border-radius: 10px; "
            "color: white; "
            "font-size: 20px; "
            "font-weight: bold; "
            "padding: 5px;"
        )

    def get_solve_button_style(self):
        return (
            "background-color: #FF9800; "  # Orange color
            "border-radius: 10px; "
            "color: white; "
            "font-size: 18px; "
            "font-weight: bold; "
            "padding: 15px; "
            "margin-top: 20px;"
        )

    def move_tile(self, idx):
        zero_index = self.board.index(0)
        row, col = divmod(idx, 3)
        zero_row, zero_col = divmod(zero_index, 3)

        if abs(row - zero_row) + abs(col - zero_col) == 1:
            self.board[zero_index], self.board[idx] = self.board[idx], self.board[zero_index]
            self.update_ui()

    def update_ui(self):
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                if idx < len(self.board):
                    self.buttons[idx].setText(str(self.board[idx]) if self.board[idx] != 0 else '')

    def solve_puzzle(self):
        # Check if the start state is the same as the goal state
        if self.board == self.goal_board:
            self.status_label.setText("Already Solved!")
            self.status_label.setStyleSheet("font-size: 16px; color: #3CAF50;")
            self.stop_timer()  # Stop the timer immediately
            self.timer_label.setText(f"Time Elapsed: {self.elapsed_time:.2f}s")
            return  # Return immediately since the puzzle is already solved

        self.status_label.setText("Solving...")
        self.status_label.setStyleSheet("font-size: 16px; color: #FF9800;")
        self.status_label.update()  # Manually trigger an update

        self.elapsed_timer.start()  # Start the timer
        self.elapsed_time = 0
        self.solver_running = True  # Indicate that the solver is running
        self.update_timer()  # Begin updating the timer

        algorithm = self.algorithm_selector.currentText()

        if algorithm == 'A*':
            solution = a_star_search(self.board, self.goal_board)
        elif algorithm == 'Greedy Best First':
            solution = greedy_best_first_search(self.board, self.goal_board)

        if solution:
            self.animate_solution(solution)
        else:
            self.status_label.setText("No solution found")
            self.status_label.setStyleSheet("font-size: 16px; color: #F33336;")  # Red color for error
            self.show_message("Error", "No solution found")
            self.stop_timer()  # Stop the timer if no solution is found

    def stop_timer(self):
        # Ensure the timer stops when solving is completed
        if self.solver_running:
            self.elapsed_time = self.elapsed_timer.elapsed() / 1000  # Final time in seconds
            self.timer_label.setText(f"Time Elapsed: {self.elapsed_time:.2f}s")  # Show time with float precision
            self.timer_label.repaint()  # Force repaint of the label
            self.solver_running = False  # Set solver running to False

    def update_timer(self):
        if self.solver_running:  # Only update the timer if the solver is still running
            self.elapsed_time = self.elapsed_timer.elapsed() / 1000  # Convert milliseconds to seconds
            self.timer_label.setText(f"Time Elapsed: {self.elapsed_time:.2f}s")  # Display time with float precision
            self.timer_label.repaint()  # Force a repaint of the label

            # Call the update_timer function every 1000ms (1 second) if the solver is still running
            QTimer.singleShot(1000, self.update_timer)

    def animate_solution(self, solution):
        def step_through_solution(index=0):
            if index < len(solution):
                move = solution[index]
                self.perform_move(move)
                self.update_ui()
                QTimer.singleShot(500, lambda: step_through_solution(index + 1))
            else:
                self.stop_timer()  # Stop the timer before showing the solved message
                self.status_label.setText("Solved!")
                self.status_label.setStyleSheet("font-size: 16px; color: #3CAF50;")
                self.show_message("Solved", "Puzzle Solved!")  # Now the message will show after stopping the timer

        step_through_solution()

    def perform_move(self, move):
        zero_index = self.board.index(0)
        row, col = divmod(zero_index, 3)
        if move == 'UP':
            new_row, new_col = row - 1, col
        elif move == 'DOWN':
            new_row, new_col = row + 1, col
        elif move == 'LEFT':
            new_row, new_col = row, col - 1
        elif move == 'RIGHT':
            new_row, new_col = row, col + 1

        new_zero_index = new_row * 3 + new_col
        self.board[zero_index], self.board[new_zero_index] = self.board[new_zero_index], self.board[zero_index]

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)


if __name__ == '__main__':
    initial_board = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    goal_board = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    algorithm_type = 'A*'  # You can change this to 'Greedy Best First'

    app = QApplication(sys.argv)
    puzzle_app = PuzzleApp1(initial_board, goal_board, algorithm_type)
    sys.exit(app.exec_())
