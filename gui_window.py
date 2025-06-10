from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QApplication, QTextEdit,
                           QGroupBox, QFrame, QScrollArea, QSizePolicy, QProgressBar,
                           QTextEdit, QDesktopWidget, QGridLayout, QGraphicsView,
                           QGraphicsScene, QGraphicsLineItem, QGraphicsSimpleTextItem,
                           QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, QPointF, QRectF, QLineF
from PyQt5.QtGui import QFont, QPalette, QColor, QTextCursor, QPainter, QPen, QBrush, QPainterPath, QFontMetrics
from machine import RotorMachine, Rotor
import random
import math

class RotorDisk(QFrame):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)  # Slightly larger for better visibility
        self.position = 0
        self.notch = 0
        self.label = label
        self.highlight = False
        
    def set_position(self, position):
        self.position = position
        self.update()
        
    def set_notch(self, notch):
        self.notch = notch
        self.update()
        
    def set_highlight(self, highlight):
        self.highlight = highlight
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw outer circle
        pen = QPen(QColor("#4a9cff"), 2)
        painter.setPen(pen)
        painter.setBrush(QColor("#2b2b2b"))
        painter.drawEllipse(10, 10, 100, 100)
        
        # Draw position indicator
        if self.highlight:
            painter.setBrush(QColor("#ff4a4a"))
        else:
            painter.setBrush(QColor("#4a9cff"))
            
        # Calculate angle (360/256 = 1.40625 degrees per step)
        angle_deg = self.position * (360/256)
        angle_rad = math.radians(angle_deg)
        x = 60 + 40 * math.cos(angle_rad)
        y = 60 - 40 * math.sin(angle_rad)
        painter.drawEllipse(int(x) - 5, int(y) - 5, 10, 10)
        
        # Draw notch position
        if self.notch is not None:
            notch_angle_deg = self.notch * (360/256)
            notch_angle_rad = math.radians(notch_angle_deg)
            x1 = 60 + 50 * math.cos(notch_angle_rad)
            y1 = 60 - 50 * math.sin(notch_angle_rad)
            x2 = 60 + 60 * math.cos(notch_angle_rad)
            y2 = 60 - 60 * math.sin(notch_angle_rad)
            
            pen = QPen(QColor("#ff8c00"), 3)
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Draw tick marks for every 32 positions (8 major ticks)
        pen = QPen(QColor("#4a9cff"), 1)
        painter.setPen(pen)
        for i in range(0, 256, 32):
            angle_deg = i * (360/256)
            angle_rad = math.radians(angle_deg)
            x1 = 60 + 45 * math.cos(angle_rad)
            y1 = 60 - 45 * math.sin(angle_rad)
            x2 = 60 + 50 * math.cos(angle_rad)
            y2 = 60 - 50 * math.sin(angle_rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Draw label and position
        painter.setPen(QColor("#ffffff"))
        painter.drawText(0, 0, 120, 120, Qt.AlignCenter, self.label)
        
        # Draw position value in hex
        painter.setFont(QFont("Courier New", 10, QFont.Bold))
        painter.drawText(0, 100, 120, 20, Qt.AlignCenter, f"{self.position:02X}")

class RotorDisplay(QFrame):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(2)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #4a9cff;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(8)
        
        # Rotor visualization
        self.rotor_disk = RotorDisk(label)
        
        # Position display with hex and decimal format
        self.position_display = QLabel("00\n(0)")
        self.position_display.setAlignment(Qt.AlignCenter)
        self.position_display.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', monospace;
                font-size: 14px;
                font-weight: bold;
                color: #4a9cff;
                background-color: #1e1e1e;
                border: 1px solid #4a9cff;
                border-radius: 3px;
                padding: 3px;
                margin: 2px 0;
                min-width: 50px;
            }
        """)
        
        # Position edit
        self.position_edit = QTextEdit()
        self.position_edit.setMaximumHeight(30)
        self.position_edit.setMaximumWidth(40)
        self.position_edit.setAlignment(Qt.AlignCenter)
        self.position_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 14px;
                color: #ffffff;
                background-color: #2a2a2a;
                border: 1px solid #4a9cff;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        self.position_edit.setPlainText("00")
        
        # Buttons with fine control
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        # Fine control buttons (small steps)
        self.up_btn = QPushButton("▲")
        self.down_btn = QPushButton("▼")
        
        # Coarse control buttons (16 steps)
        self.big_up_btn = QPushButton("▲▲")
        self.big_down_btn = QPushButton("▼▼")
        
        # Style all buttons
        for btn in [self.up_btn, self.down_btn, self.big_up_btn, self.big_down_btn]:
            btn.setFixedSize(30, 25)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #5a5a5a;
                }
            """)
        
        # Add buttons to layout
        btn_layout.addWidget(self.big_up_btn)
        btn_layout.addWidget(self.up_btn)
        btn_layout.addWidget(self.down_btn)
        btn_layout.addWidget(self.big_down_btn)
        
        # Add widgets to layout
        self.layout.addWidget(QLabel(label), 0, Qt.AlignCenter)
        self.layout.addWidget(self.rotor_disk, 0, Qt.AlignCenter)
        
        # Position display and edit
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(self.position_display)
        pos_layout.addWidget(self.position_edit)
        self.layout.addLayout(pos_layout)
        
        self.layout.addLayout(btn_layout)
    
    def set_position(self, position: int) -> None:
        """Update the position display with animation."""
        if not hasattr(self, 'position_display'):
            return
            
        # Update the position display with both hex and decimal
        hex_val = f"{position:02X}"
        self.position_display.setText(f"{hex_val}\n({position})")
        self.rotor_disk.set_position(position)
        
        # Update position edit field if it exists
        if hasattr(self, 'position_edit'):
            self.position_edit.blockSignals(True)  # Prevent recursive updates
            self.position_edit.setPlainText(hex_val)
            self.position_edit.blockSignals(False)
        
    def set_notch(self, notch: int) -> None:
        """Update the notch position."""
        self.rotor_disk.set_notch(notch)
        
    def set_highlight(self, highlight: bool) -> None:
        """Set highlight state for the rotor."""
        self.rotor_disk.set_highlight(highlight)

class ASCIIViewer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #4a9cff;
                border-radius: 4px;
                padding: 8px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 1px 3px;
                margin: 1px;
                text-align: center;
            }
            .highlight {
                background-color: #4a9cff;
                color: #000000;
                font-weight: bold;
                border: 1px solid #ffffff;
            }
        """)
        
        self.layout = QGridLayout(self)
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(2, 2, 2, 2)
        
        # Create header
        for i in range(16):
            header = QLabel(f"{i:02X}")
            header.setStyleSheet("font-weight: bold; color: #4a9cff;")
            self.layout.addWidget(header, 0, i+1)
            
        # Create rows with row headers and cells
        self.cells = []
        for row in range(16):
            # Row header
            row_header = QLabel(f"{row:02X}0:")
            row_header.setStyleSheet("font-weight: bold; color: #4a9cff;")
            self.layout.addWidget(row_header, row+1, 0)
            
            # Cells for this row
            row_cells = []
            for col in range(16):
                value = row * 16 + col
                char = chr(value) if 32 <= value <= 126 else '.'
                cell = QLabel(f"{char}")
                cell.setFixedSize(20, 20)
                cell.setAlignment(Qt.AlignCenter)
                cell.setProperty('value', value)
                row_cells.append(cell)
                self.layout.addWidget(cell, row+1, col+1)
            self.cells.append(row_cells)
    
    def highlight_positions(self, positions):
        """Highlight the given positions in the grid."""
        # First, clear all highlights
        for row in self.cells:
            for cell in row:
                cell.setStyleSheet("")
        
        # Highlight new positions
        for pos in positions:
            if 0 <= pos < 256:
                row = pos // 16
                col = pos % 16
                self.cells[row][col].setProperty('class', 'highlight')
                self.cells[row][col].style().unpolish(self.cells[row][col])
                self.cells[row][col].style().polish(self.cells[row][col])

class RotorVisualization(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #4a9cff; border-radius: 4px;")
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Set a fixed size
        self.setFixedSize(1000, 700)
        
        # Colors
        self.bg_color = QColor(43, 43, 43)  # #2b2b2b
        self.line_color = QColor(74, 156, 255)  # #4a9cff
        self.text_color = QColor(255, 255, 255)  # White
        self.highlight_color = QColor(255, 74, 74)  # #ff4a4a
        
        # Initialize components
        self.init_components()
        
        # Animation timer
        self.animation_step = 0
        self.animation_path = []
        self.animation_timer = None
    
    def init_components(self):
        # Clear existing items
        self.scene.clear()
        
        # Add title
        title = self.scene.addText("Rotor Machine Visualization", QFont('Arial', 14, QFont.Bold))
        title.setDefaultTextColor(self.text_color)
        title.setPos(400 - title.boundingRect().width()/2, 10)
        
        # Add input section
        self.draw_input_section()
        
        # Add rotors
        self.rotor_boxes = []
        self.rotor_labels = []
        self.rotor_positions = []
        
        rotor_x = 150
        for i in range(3):
            # Rotor box
            box = self.scene.addRect(rotor_x, 150, 100, 400, QPen(self.line_color, 2))
            self.rotor_boxes.append(box)
            
            # Rotor label
            label = self.scene.addText(f"Rotor {i+1}", QFont('Arial', 10, QFont.Bold))
            label.setDefaultTextColor(self.line_color)
            label.setPos(rotor_x + 50 - label.boundingRect().width()/2, 120)
            self.rotor_labels.append(label)
            
            # Rotor position
            pos_text = self.scene.addText("00", QFont('Courier New', 12, QFont.Bold))
            pos_text.setDefaultTextColor(self.highlight_color)
            pos_text.setPos(rotor_x + 50 - pos_text.boundingRect().width()/2, 560)
            self.rotor_positions.append(pos_text)
            
            # Draw contacts
            self.draw_rotor_contacts(rotor_x, 180, 100, 350, i)
            
            rotor_x += 250
        
        # Add reflector
        self.draw_reflector()
        
        # Add output section
        self.draw_output_section()
        
        # Add control buttons
        self.draw_controls()
        
        # Add signal path
        self.current_path = None
    
    def draw_input_section(self):
        # Input box
        self.input_box = self.scene.addRect(50, 150, 80, 400, QPen(self.line_color, 2))
        input_label = self.scene.addText("Input", QFont('Arial', 10, QFont.Bold))
        input_label.setDefaultTextColor(self.line_color)
        input_label.setPos(85 - input_label.boundingRect().width()/2, 120)
        
        # Input character
        self.input_char = self.scene.addText("A", QFont('Courier New', 16, QFont.Bold))
        self.input_char.setDefaultTextColor(self.highlight_color)
        self.input_char.setPos(90 - self.input_char.boundingRect().width()/2, 300)
        
        # Input contacts
        for i in range(16):
            y = 170 + i * 25
            # Contact point
            self.scene.addEllipse(130, y-2, 4, 4, QPen(self.line_color), QBrush(self.line_color))
            # Label
            label = self.scene.addText(chr(65 + i), QFont('Courier New', 8))
            label.setDefaultTextColor(self.text_color)
            label.setPos(110 - label.boundingRect().width(), y-8)
    
    def draw_rotor_contacts(self, x, y, width, height, rotor_num):
        # Draw contacts on both sides
        for i in range(16):
            pos_y = y + i * (height / 16)
            # Left side contacts
            self.scene.addEllipse(x-4, pos_y-2, 4, 4, QPen(self.line_color), QBrush(self.line_color))
            # Right side contacts
            self.scene.addEllipse(x+width, pos_y-2, 4, 4, QPen(self.line_color), QBrush(self.line_color))
            
            # Draw wiring (random for now)
            if rotor_num == 0:  # First rotor
                target = (i + 13) % 16  # Example wiring
            elif rotor_num == 1:  # Second rotor
                target = (i * 5 + 7) % 16  # Different wiring
            else:  # Third rotor
                target = (i * 3 + 5) % 16  # Another wiring
                
            # Draw the wiring path
            path = QPainterPath()
            path.moveTo(x, y + i * (height / 16))
            ctrl_x1 = x + width/4
            ctrl_x2 = x + 3*width/4
            ctrl_y1 = y + i * (height / 16)
            ctrl_y2 = y + target * (height / 16)
            path.cubicTo(ctrl_x1, ctrl_y1, ctrl_x2, ctrl_y2, x+width, y + target * (height / 16))
            
            path_item = QGraphicsPathItem(path)
            path_item.setPen(QPen(self.line_color, 0.5))
            path_item.setZValue(-1)  # Send to back
            self.scene.addItem(path_item)
    
    def draw_reflector(self):
        x = 900
        # Reflector box
        reflector = self.scene.addRect(x, 150, 50, 400, QPen(self.line_color, 2))
        reflector.setBrush(QColor(30, 30, 60))  # Slightly different color
        
        # Label
        label = self.scene.addText("Reflector", QFont('Arial', 10, QFont.Bold))
        label.setDefaultTextColor(self.line_color)
        label.setPos(x + 25 - label.boundingRect().width()/2, 120)
        
        # Draw reflector wiring (pairs)
        for i in range(8):
            y1 = 170 + i * 25
            y2 = 170 + (15 - i) * 25
            
            # Draw the connection
            path = QPainterPath()
            path.moveTo(x, y1)
            path.cubicTo(x+10, y1, x+40, y2, x+50, y2)
            
            path_item = QGraphicsPathItem(path)
            path_item.setPen(QPen(self.line_color, 0.8))
            path_item.setZValue(-1)
            self.scene.addItem(path_item)
            
            # Draw contact points
            self.scene.addEllipse(x-4, y1-2, 4, 4, QPen(self.line_color), QBrush(self.line_color))
            self.scene.addEllipse(x+50, y2-2, 4, 4, QPen(self.line_color), QBrush(self.line_color))
    
    def draw_output_section(self):
        # Output box (same as input but on the right)
        self.output_box = self.scene.addRect(970, 150, 80, 400, QPen(self.line_color, 2))
        output_label = self.scene.addText("Output", QFont('Arial', 10, QFont.Bold))
        output_label.setDefaultTextColor(self.line_color)
        output_label.setPos(1010 - output_label.boundingRect().width()/2, 120)
        
        # Output character
        self.output_char = self.scene.addText("", QFont('Courier New', 16, QFont.Bold))
        self.output_char.setDefaultTextColor(self.highlight_color)
        self.output_char.setPos(1010 - self.output_char.boundingRect().width()/2, 300)
        
        # Output contacts (right side)
        for i in range(16):
            y = 170 + i * 25
            # Contact point
            self.scene.addEllipse(970, y-2, 4, 4, QPen(self.line_color), QBrush(self.line_color))
            # Label (on the right side)
            label = self.scene.addText(chr(65 + i), QFont('Courier New', 8))
            label.setDefaultTextColor(self.text_color)
            label.setPos(980, y-8)
    
    def draw_controls(self):
        # Control buttons at the bottom
        self.encrypt_btn = QPushButton("Encrypt")
        self.decrypt_btn = QPushButton("Decrypt")
        self.step_btn = QPushButton("Step")
        self.reset_btn = QPushButton("Reset")
        
        # Style buttons
        btn_style = """
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 15px;
                margin: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #5a5a5a;
            }
        """
        
        for btn in [self.encrypt_btn, self.decrypt_btn, self.step_btn, self.reset_btn]:
            btn.setStyleSheet(btn_style)
            btn.setParent(self.viewport())
            btn.show()
        
        # Position buttons
        btn_width = 100
        btn_spacing = 20
        total_width = 4 * btn_width + 3 * btn_spacing
        start_x = (self.width() - total_width) / 2
        
        self.encrypt_btn.move(int(start_x), 580)
        self.decrypt_btn.move(int(start_x + btn_width + btn_spacing), 580)
        self.step_btn.move(int(start_x + 2 * (btn_width + btn_spacing)), 580)
        self.reset_btn.move(int(start_x + 3 * (btn_width + btn_spacing)), 580)
        
        # Connect signals
        self.encrypt_btn.clicked.connect(self.start_encryption)
        self.decrypt_btn.clicked.connect(self.start_decryption)
        self.step_btn.clicked.connect(self.step_animation)
        self.reset_btn.clicked.connect(self.reset_animation)
    
    def start_encryption(self):
        self.encrypting = True
        self.animation_step = 0
        self.animation_path = self.generate_path(forward=True)
        self.animate_path()
    
    def start_decryption(self):
        self.encrypting = False
        self.animation_step = 0
        self.animation_path = self.generate_path(forward=False)
        self.animate_path()
    
    def generate_path(self, forward=True):
        # This would generate the actual path based on rotor settings
        # For now, generate a sample path
        path = []
        
        # Start at input (example: input 'A')
        input_y = 170 + 0 * 25  # 'A' is at position 0
        path.append((50, input_y))
        
        # Through rotors
        for i in range(3):
            x = 150 + i * 250
            # Simple diagonal for now
            path.append((x, input_y + i * 20))
        
        # To reflector and back
        path.append((900, input_y + 60))
        path.append((900, input_y + 120))  # Reflected back
        
        # Back through rotors
        for i in range(2, -1, -1):
            x = 150 + i * 250
            path.append((x + 100, input_y + (i+1) * 20 + 80))
        
        # To output
        path.append((970, input_y + 180))
        
        return path
    
    def animate_path(self):
        if self.animation_step >= len(self.animation_path) - 1:
            self.animation_step = 0
            return
            
        if self.current_path:
            self.scene.removeItem(self.current_path)
        
        # Draw path up to current step
        path = QPainterPath()
        path.moveTo(*self.animation_path[0])
        
        for i in range(1, self.animation_step + 1):
            path.lineTo(*self.animation_path[i])
        
        self.current_path = QGraphicsPathItem(path)
        self.current_path.setPen(QPen(self.highlight_color, 2))
        self.scene.addItem(self.current_path)
        
        # Move to next step
        self.animation_step += 1
        
        # Schedule next step
        if self.animation_step < len(self.animation_path):
            QApplication.processEvents()
            QApplication.processEvents()
            QTimer.singleShot(300, self.animate_path)
    
    def step_animation(self):
        if not self.animation_path:
            self.animation_path = self.generate_path(self.encrypting)
            self.animation_step = 0
        
        if self.animation_step < len(self.animation_path):
            if self.current_path:
                self.scene.removeItem(self.current_path)
            
            # Draw path up to current step
            path = QPainterPath()
            path.moveTo(*self.animation_path[0])
            
            for i in range(1, self.animation_step + 1):
                path.lineTo(*self.animation_path[i])
            
            self.current_path = QGraphicsPathItem(path)
            self.current_path.setPen(QPen(self.highlight_color, 2))
            self.scene.addItem(self.current_path)
            
            self.animation_step += 1
    
    def reset_animation(self):
        if self.current_path:
            self.scene.removeItem(self.current_path)
            self.current_path = None
        self.animation_step = 0
        self.animation_path = []


class RotorMachineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("256-Character Rotor Machine")
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        
        # Initialize the rotor machine
        self.machine = RotorMachine(num_rotors=3)
        self.rotor_displays = []
        self.is_processing = False
        
        # Set up the UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Initialize rotors
        self.update_rotor_displays()
        
        # Set window size and position
        self.resize(1200, 800)
        self.center()
    
    def center(self):
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def init_ui(self):
        """Initialize the user interface."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QHBoxLayout(main_widget)
        
        # Left panel for rotors
        left_panel = QVBoxLayout()
        
        # Rotor displays
        self.rotor_display_layout = QHBoxLayout()
        for i in range(self.machine.num_rotors):
            display = RotorDisplay(f"Rotor {i+1}")
            self.rotor_displays.append(display)
            self.rotor_display_layout.addWidget(display)
        
        left_panel.addLayout(self.rotor_display_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.randomize_btn = QPushButton("Randomize Rotors")
        self.reset_btn = QPushButton("Reset Rotors")
        self.encrypt_btn = QPushButton("Encrypt")
        self.decrypt_btn = QPushButton("Decrypt")
        self.clear_btn = QPushButton("Clear")
        
        for btn in [self.randomize_btn, self.reset_btn, self.encrypt_btn, 
                   self.decrypt_btn, self.clear_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px 10px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #5a5a5a;
                }
            """)
            btn_layout.addWidget(btn)
        
        left_panel.addLayout(btn_layout)
        
        # Text areas
        text_layout = QHBoxLayout()
        
        # Input
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #4a9cff;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        
        # Output
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #4a9cff;
                border: 1px solid #4a9cff;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        
        text_layout.addWidget(input_group, 1)
        text_layout.addWidget(output_group, 1)
        
        left_panel.addLayout(text_layout, 1)
        
        # Add ASCII viewer to the right
        self.ascii_viewer = ASCIIViewer()
        
        # Add visualization
        self.visualization = RotorVisualization()
        
        # Add everything to main layout
        main_layout.addLayout(left_panel, 3)
        main_layout.addWidget(self.ascii_viewer, 2)
        main_layout.addWidget(self.visualization, 2)
    
    def update_rotor_displays(self):
        """Update all rotor displays with current positions."""
        positions = []
        for i, display in enumerate(self.rotor_displays):
            if i < len(self.machine.rotors):
                rotor = self.machine.rotors[i]
                display.set_position(rotor.position)
                display.set_notch(rotor.notch)
                positions.append(rotor.position)
        
        # Update ASCII viewer highlights
        self.ascii_viewer.highlight_positions(positions)
    
    def connect_signals(self):
        """Connect all UI signals to their respective slots."""
        # Rotor controls
        for i, display in enumerate(self.rotor_displays):
            display.up_btn.clicked.connect(lambda _, idx=i: self.adjust_rotor(idx, 1))
            display.down_btn.clicked.connect(lambda _, idx=i: self.adjust_rotor(idx, -1))
            display.big_up_btn.clicked.connect(lambda _, idx=i: self.adjust_rotor(idx, 16))
            display.big_down_btn.clicked.connect(lambda _, idx=i: self.adjust_rotor(idx, -16))
        
        # Action buttons
        self.randomize_btn.clicked.connect(self.randomize_rotors)
        self.reset_btn.clicked.connect(self.reset_rotors)
        self.encrypt_btn.clicked.connect(self.encrypt_text)
        self.decrypt_btn.clicked.connect(self.decrypt_text)
        self.clear_btn.clicked.connect(self.clear_text)
    
    def adjust_rotor(self, rotor_idx: int, delta: int) -> None:
        """Adjust a rotor's position and update the display."""
        if 0 <= rotor_idx < len(self.rotor_displays):
            current_pos = self.machine.rotors[rotor_idx].position
            new_pos = (current_pos + delta) % 256
            self.machine.rotors[rotor_idx].set_position(new_pos)
            self.update_rotor_displays()
    
    def randomize_rotors(self) -> None:
        """Randomize all rotor positions."""
        for rotor in self.machine.rotors:
            rotor.set_position(random.randint(0, 255))
        self.update_rotor_displays()
    
    def reset_rotors(self) -> None:
        """Reset all rotors to position 0."""
        for rotor in self.machine.rotors:
            rotor.set_position(0)
        self.update_rotor_displays()
    
    def process_text(self, encrypt: bool = True) -> None:
        """Process the input text (encrypt or decrypt)."""
        if self.is_processing:
            return
            
        try:
            self.is_processing = True
            input_text = self.input_text.toPlainText().strip()
            
            if not input_text:
                return
                
            # Clear output
            self.output_text.clear()
            
            # Process in chunks to keep the UI responsive
            chunk_size = 100
            total_chars = len(input_text)
            processed = 0
            
            # Process text in chunks
            while processed < total_chars:
                chunk = input_text[processed:processed + chunk_size]
                result = []
                
                for char in chunk:
                    byte = ord(char)
                    if 0 <= byte <= 255:  # Only process valid bytes
                        if encrypt:
                            processed_byte = self.machine.encrypt(byte)
                        else:
                            processed_byte = self.machine.decrypt(byte)
                        result.append(chr(processed_byte))
                        
                        # Update rotor displays
                        for i, display in enumerate(self.rotor_displays):
                            if i < len(self.machine.rotors):
                                display.set_highlight(True)
                                display.set_position(self.machine.rotors[i].position)
                    
                    processed += 1
                    # Update progress
                    self.progress.setValue(int((processed / total_chars) * 100))
                    QApplication.processEvents()  # Keep UI responsive
                
                # Append result to output
                self.output_text.moveCursor(QTextCursor.End)
                self.output_text.insertPlainText(''.join(result))
                
                # Reset highlights
                for display in self.rotor_displays:
                    display.set_highlight(False)
            
            # Reset progress
            self.progress.setValue(0)
            
        except Exception as e:
            self.output_text.setPlainText(f"Error: {str(e)}")
        finally:
            self.is_processing = False
    
    def encrypt_text(self):
        """Encrypt the input text."""
        self.process_text(encrypt=True)
    
    def decrypt_text(self):
        """Decrypt the input text."""
        self.process_text(encrypt=False)
    
    def clear_text(self):
        """Clear both input and output text areas."""
        self.input_text.clear()
        self.output_text.clear()
        self.progress.setValue(0)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = RotorMachineGUI()
    window.show()
    sys.exit(app.exec_())