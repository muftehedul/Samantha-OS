#!/usr/bin/env python3
"""
Samantha OS GUI - Minimalist interface inspired by "Her" (2013)
Warm colors, soft animations, conversation-focused design
"""

import sys
import math
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
    QScrollArea,
    QGraphicsOpacityEffect,
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QBrush


class SignalEmitter(QObject):
    """Thread-safe signal emitter for GUI updates"""
    transcription_update = pyqtSignal(str)
    message_add = pyqtSignal(str, bool)  # text, is_user
    state_change = pyqtSignal(str, str)  # state, status_text
    voice_finished = pyqtSignal()

# Color palette from "Her" movie
COLORS = {
    "primary": "#FF6B6B",  # Soft coral
    "secondary": "#FFE5E5",  # Light pink
    "accent": "#FFB4A2",  # Warm peach
    "background": "#FFF5EE",  # Seashell white
    "text": "#4A4A4A",  # Soft dark
    "text_light": "#8B8B8B",  # Light gray
    "warm_white": "#FFFAF5",  # Warm white
    "soft_red": "#E8A0A0",  # Soft red for animations
}


class PulseWidget(QWidget):
    """Soft pulsing circle - like Samantha's presence"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pulse = 0
        self._opacity = 0.8
        self.state = "idle"
        self.pulse_direction = 1

        self.colors = {
            "idle": QColor("#FFB4A2"),
            "listening": QColor("#FF6B6B"),
            "thinking": QColor("#E8A0A0"),
            "speaking": QColor("#FF8080"),
        }

        self.setMinimumSize(120, 120)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)

    def get_pulse(self):
        return self._pulse

    def set_pulse(self, value):
        self._pulse = value
        self.update()

    pulse = pyqtProperty(int, get_pulse, set_pulse)

    def set_state(self, state):
        self.state = state
        self.update()

    def animate(self):
        if self.state == "listening":
            self._pulse = (self._pulse + 8) % 360  # Very fast for listening
            self._opacity += 0.08 * self.pulse_direction  # Dramatic breathing effect
            if self._opacity >= 1.0 or self._opacity <= 0.2:
                self.pulse_direction *= -1
        else:
            self._pulse = (self._pulse + 2) % 360
            self._opacity = 0.8

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        base_radius = min(center_x, center_y) - 20

        color = self.colors.get(self.state, self.colors["idle"])

        # Outer glow
        for i in range(3):
            glow_color = QColor(color)
            glow_color.setAlpha(int((30 - i * 10) * self._opacity))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_color))
            radius = (
                base_radius
                + i * 8
                + (self._pulse / 20 if self.state == "listening" else 0)
            )
            painter.drawEllipse(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2),
            )

        # Main circle with gradient
        gradient = QLinearGradient(
            center_x - base_radius,
            center_y - base_radius,
            center_x + base_radius,
            center_y + base_radius,
        )
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - base_radius,
            center_y - base_radius,
            base_radius * 2,
            base_radius * 2,
        )

        # Inner highlight
        highlight = QColor("#FFFFFF")
        highlight.setAlpha(40)
        painter.setBrush(QBrush(highlight))
        inner_radius = base_radius * 0.6
        painter.drawEllipse(
            int(center_x - inner_radius),
            int(center_y - inner_radius - 10),
            int(inner_radius * 1.2),
            int(inner_radius * 0.8),
        )


class MessageBubble(QFrame):
    """Soft message bubble"""

    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setFont(QFont("SF Pro Display", 12))

        if is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFE5E5;
                    border-radius: 20px;
                    border: none;
                }
                QLabel { color: #4A4A4A; }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 20px;
                    border: 1px solid #FFE5E5;
                }
                QLabel { color: #4A4A4A; }
            """)

        layout.addWidget(self.label)


class SamanthaWindow(QMainWindow):
    """Main Samantha OS window - minimalist "Her" style"""

    def __init__(self):
        super().__init__()
        # Thread-safe signal emitter
        self.signals = SignalEmitter()
        self.signals.transcription_update.connect(self._update_transcription)
        self.signals.message_add.connect(self._add_message_slot)
        self.signals.state_change.connect(self._set_state_slot)
        self.signals.voice_finished.connect(self._voice_finished_slot)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Samantha")
        self.setGeometry(100, 100, 500, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS["background"]};
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header - simple and elegant
        header_layout = QHBoxLayout()

        title_label = QLabel("Samantha")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["primary"]};
                font-size: 28px;
                font-weight: 300;
                letter-spacing: 2px;
            }}
        """)
        title_label.setFont(QFont("SF Pro Display", 28, QFont.Light))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Status indicator
        self.status_label = QLabel("Online")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text_light"]};
                font-size: 12px;
                font-weight: 300;
            }}
        """)
        header_layout.addWidget(self.status_label)

        main_layout.addLayout(header_layout)

        # Pulse indicator
        self.pulse_widget = PulseWidget()
        main_layout.addWidget(self.pulse_widget, alignment=Qt.AlignCenter)

        # Conversation area
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(15)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.chat_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS["accent"]};
                border-radius: 3px;
                min-height: 30px;
            }}
        """)

        main_layout.addWidget(scroll_area, stretch=1)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["warm_white"]};
                border-radius: 25px;
                border: 1px solid {COLORS["secondary"]};
            }}
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 10, 10, 10)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type something...")
        self.input_field.setMaximumHeight(80)
        self.input_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                border: none;
                color: {COLORS["text"]};
                font-size: 14px;
            }}
        """)
        self.input_field.setFont(QFont("SF Pro Display", 14))
        input_layout.addWidget(self.input_field, stretch=1)

        self.send_btn = QPushButton("→")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: #FF8080;
            }}
        """)
        input_layout.addWidget(self.send_btn)

        main_layout.addWidget(input_frame)

        # Voice button - Her movie inspired
        voice_container = QWidget()
        voice_container_layout = QVBoxLayout(voice_container)
        voice_container_layout.setSpacing(10)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.voice_btn = QPushButton("")
        self.voice_btn.setCheckable(True)
        self.voice_btn.setFixedSize(60, 60)
        self.voice_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["accent"]}, stop:1 {COLORS["primary"]});
                border: none;
                border-radius: 30px;
                color: white;
                font-size: 24px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["primary"]}, stop:1 #FF5555);
            }}
            QPushButton:checked {{
                background: {COLORS["primary"]};
                border: 3px solid white;
                box-shadow: 0 0 20px {COLORS["primary"]};
            }}
        """)
        self.voice_btn.setText("🎤")
        button_layout.addWidget(self.voice_btn)
        button_layout.addStretch()
        
        voice_container_layout.addLayout(button_layout)
        
        # Button label
        self.voice_label = QLabel("Hold to speak")
        self.voice_label.setAlignment(Qt.AlignCenter)
        self.voice_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text_light"]};
                font-size: 11px;
                font-weight: 300;
            }}
        """)
        voice_container_layout.addWidget(self.voice_label)

        main_layout.addWidget(voice_container)
        
        # Live transcription - real-time display
        self.transcription_label = QLabel("")
        self.transcription_label.setAlignment(Qt.AlignCenter)
        self.transcription_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["primary"]};
                font-size: 14px;
                font-weight: 400;
                padding: 10px;
                background-color: {COLORS["secondary"]};
                border-radius: 15px;
            }}
        """)
        self.transcription_label.setWordWrap(True)
        self.transcription_label.hide()
        main_layout.addWidget(self.transcription_label)

        # Welcome message
        self.add_message("Hi, I'm Samantha. How are you feeling today?", is_user=False)

    def set_state(self, state, status_text=None):
        self.pulse_widget.set_state(state)
        if status_text:
            self.status_label.setText(status_text)

    def add_message(self, text, is_user=True):
        bubble = MessageBubble(text, is_user)
        self.chat_layout.addWidget(bubble)

        # Scroll to bottom
        from PyQt5.QtCore import QTimer

        QTimer.singleShot(
            100, lambda: self.chat_widget.scroll(0, self.chat_widget.height())
        )

    # Thread-safe slot methods (called via signals from background threads)
    def _update_transcription(self, text):
        """Update transcription label (thread-safe via signal)"""
        if text:
            self.transcription_label.setText(text)
            self.transcription_label.show()
        else:
            self.transcription_label.hide()

    def _add_message_slot(self, text, is_user):
        """Add message to chat (thread-safe via signal)"""
        self.add_message(text, is_user)

    def _set_state_slot(self, state, status_text):
        """Set UI state (thread-safe via signal)"""
        self.pulse_widget.set_state(state)
        if status_text:
            self.status_label.setText(status_text)

    def _voice_finished_slot(self):
        """Handle voice input finished"""
        self.voice_btn.setChecked(False)
        self.voice_label.setText("Hold to speak")
        QTimer.singleShot(2000, self.transcription_label.hide)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application font
    font = QFont("SF Pro Display", 12)
    app.setFont(font)

    window = SamanthaWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
