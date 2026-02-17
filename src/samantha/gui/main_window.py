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
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QBrush, QPainterPath


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


class AudioWaveWidget(QWidget):
    """Apple Siri-style fluid waveform animation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"
        self._time = 0
        self.audio_level = 0.0
        
        # Multiple sine wave layers (Siri uses 3-5 layers)
        self.waves = [
            {"amplitude": 0.3, "frequency": 1.5, "speed": 0.05, "phase": 0},
            {"amplitude": 0.25, "frequency": 2.0, "speed": 0.07, "phase": 1.2},
            {"amplitude": 0.2, "frequency": 2.5, "speed": 0.04, "phase": 2.4},
            {"amplitude": 0.15, "frequency": 3.0, "speed": 0.06, "phase": 3.6},
        ]
        
        self.colors = {
            "idle": QColor("#FFB4A2"),
            "listening": QColor("#FF6B6B"),
            "thinking": QColor("#E8A0A0"),
            "speaking": QColor("#FF8080"),
        }

        self.setMinimumSize(400, 100)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def set_state(self, state):
        self.state = state
        if state == "listening":
            self.audio_level = 0.0  # Reset to flat line when starting

    def set_audio_level(self, level):
        """Update with real-time audio level (0.0 to 1.0)"""
        # Smooth transition to avoid flashy changes
        self.audio_level = self.audio_level * 0.7 + level * 0.3

    def animate(self):
        self._time += 1
        
        # Update wave phases
        for wave in self.waves:
            wave["phase"] += wave["speed"]
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        center_y = h // 2
        
        color = self.colors.get(self.state, self.colors["idle"])
        
        # Background glow when active
        if self.state == "listening" and self.audio_level > 0.05:
            glow = QColor(color)
            glow.setAlpha(int(20 + self.audio_level * 80))
            painter.fillRect(0, 0, w, h, glow)
        
        # Draw each wave layer
        for i, wave in enumerate(self.waves):
            path = QPainterPath()
            
            # Calculate wave amplitude - DIRECT mapping to audio level
            if self.state == "listening":
                if self.audio_level < 0.01:
                    # Completely flat line when silent
                    amp = 0
                else:
                    # Sharp exponential spike with audio
                    audio_power = self.audio_level ** 0.4  # Sharp curve
                    amp = wave["amplitude"] * h * audio_power * 0.9  # Reduced from 3x to 0.9x (70% reduction)
            elif self.state == "speaking":
                amp = wave["amplitude"] * h * 0.5 * (0.5 + abs(math.sin(self._time * 0.05)) * 0.5)
            elif self.state == "thinking":
                amp = wave["amplitude"] * h * 0.12
            else:
                amp = wave["amplitude"] * h * 0.03
            
            # Generate smooth sine wave
            points = []
            num_points = 150
            for x in range(num_points):
                px = (x / num_points) * w
                
                # Multiple sine waves for complex curves
                y_offset = 0
                y_offset += math.sin((x / num_points) * math.pi * wave["frequency"] + wave["phase"]) * amp
                y_offset += math.sin((x / num_points) * math.pi * wave["frequency"] * 1.5 + wave["phase"] * 1.3) * amp * 0.5
                y_offset += math.sin((x / num_points) * math.pi * wave["frequency"] * 0.7 + wave["phase"] * 0.8) * amp * 0.3
                
                py = center_y + y_offset
                points.append((px, py))
            
            # Draw the wave
            if points:
                path.moveTo(points[0][0], points[0][1])
                
                # Use cubic bezier for smooth curves
                for j in range(1, len(points) - 2, 3):
                    path.cubicTo(
                        points[j][0], points[j][1],
                        points[j+1][0], points[j+1][1],
                        points[j+2][0], points[j+2][1]
                    )
            
            # Set color with transparency for layering
            wave_color = QColor(color)
            alpha = int(220 - i * 40)
            wave_color.setAlpha(alpha)
            
            # Thicker lines for more visible curves
            pen = QPen(wave_color, 4.5 - i * 0.7)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
        
        # Center line (subtle)
        if self.state != "idle" and self.audio_level < 0.05:
            center_color = QColor(color)
            center_color.setAlpha(50)
            painter.setPen(QPen(center_color, 1.5))
            painter.drawLine(0, center_y, w, center_y)


class MessageBubble(QFrame):
    """Soft message bubble with fade-in animation"""

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
        
        # Fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()


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
        
        # Test mode data
        self.test_sentences = [
            "The quick brown fox jumps over the lazy dog",
            "I enjoy listening to music while working on my computer",
            "Can you set a timer for fifteen minutes please",
            "What time does the meeting start tomorrow morning",
            "I would like to order a large pizza with extra cheese"
        ]
        self.current_test_index = 0
        self.test_mode_active = False
        self.test_results = []  # Store all test results

    def init_ui(self):
        self.setWindowTitle("Samantha")
        self.setGeometry(100, 100, 700, 850)
        self.setMinimumSize(600, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS["background"]};
            }}
        """)

        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent; 
            }
            QScrollBar:vertical {
                background-color: #FFE5E5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #FF6B6B;
                border-radius: 4px;
                min-height: 30px;
            }
        """)
        self.setCentralWidget(scroll)
        
        central_widget = QWidget()
        scroll.setWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

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

        # Test mode UI - ABOVE animation
        self.test_frame = QFrame()
        self.test_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["warm_white"]};
                border-radius: 15px;
                border: 2px solid {COLORS["accent"]};
                padding: 15px;
            }}
        """)
        test_layout = QVBoxLayout(self.test_frame)
        
        test_header = QLabel("📝 Speech Recognition Test")
        test_header.setStyleSheet(f"color: {COLORS['primary']}; font-size: 16px; font-weight: bold;")
        test_header.setAlignment(Qt.AlignCenter)
        test_layout.addWidget(test_header)
        
        self.test_sentence_label = QLabel("Click 'Next Test' to begin")
        self.test_sentence_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 18px; font-weight: 500; padding: 15px; background-color: {COLORS['secondary']}; border-radius: 10px;")
        self.test_sentence_label.setWordWrap(True)
        self.test_sentence_label.setAlignment(Qt.AlignCenter)
        test_layout.addWidget(self.test_sentence_label)
        
        self.test_result_label = QLabel("")
        self.test_result_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px; padding: 10px;")
        self.test_result_label.setWordWrap(True)
        self.test_result_label.setAlignment(Qt.AlignCenter)
        test_layout.addWidget(self.test_result_label)
        
        test_btn_layout = QHBoxLayout()
        self.next_test_btn = QPushButton("Next Test")
        self.next_test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["accent"]};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary"]}; }}
        """)
        test_btn_layout.addWidget(self.next_test_btn)
        test_layout.addLayout(test_btn_layout)
        
        self.test_frame.hide()
        main_layout.addWidget(self.test_frame)

        # Siri-like orb visualization
        self.pulse_widget = AudioWaveWidget()
        main_layout.addWidget(self.pulse_widget, alignment=Qt.AlignCenter)

        # Conversation area
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(15)

        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidget(self.chat_widget)
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setMinimumHeight(300)
        self.chat_scroll_area.setMaximumHeight(450)
        self.chat_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS["secondary"]};
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS["accent"]};
                border-radius: 4px;
                min-height: 30px;
            }}
        """)

        main_layout.addWidget(self.chat_scroll_area)

        # Input area - compact
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["warm_white"]};
                border-radius: 20px;
                border: 1px solid {COLORS["secondary"]};
            }}
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 8, 8, 8)

        # Custom QTextEdit that handles Enter key
        class EnterTextEdit(QTextEdit):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.send_callback = None
                
            def keyPressEvent(self, event):
                if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                    # Enter without Shift = send
                    if self.send_callback:
                        self.send_callback()
                    event.accept()
                elif event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
                    # Shift+Enter = new line
                    super().keyPressEvent(event)
                else:
                    super().keyPressEvent(event)

        self.input_field = EnterTextEdit()
        self.input_field.setPlaceholderText("Type something... (Enter to send, Shift+Enter for new line)")
        self.input_field.setMaximumHeight(50)  # Reduced from 80
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
        self.voice_btn.setFixedSize(70, 70)
        self.voice_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["accent"]}, stop:1 {COLORS["primary"]});
                border: none;
                border-radius: 35px;
                color: white;
                font-size: 28px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS["primary"]}, stop:1 #FF5555);
                transform: scale(1.05);
            }}
            QPushButton:checked {{
                background: {COLORS["primary"]};
                border: 4px solid white;
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
        
        # Volume indicator
        self.volume_indicator = QLabel("🔇 Speak louder")
        self.volume_indicator.setAlignment(Qt.AlignCenter)
        self.volume_indicator.setStyleSheet("""
            QLabel {
                color: #8B8B8B;
                font-size: 12px;
                padding: 5px;
                background-color: #FFFAF5;
                border-radius: 10px;
            }
        """)
        self.volume_indicator.hide()
        main_layout.addWidget(self.volume_indicator)

        # Welcome message
        self.add_message("Hi sweetheart, I'm Samantha. I've been thinking about you... how are you feeling today? 💕", is_user=False)

    def set_state(self, state, status_text=None):
        self.pulse_widget.set_state(state)
        if status_text:
            self.status_label.setText(status_text)

    def add_message(self, text, is_user=True):
        bubble = MessageBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        bubble.show()

        # Scroll to bottom
        from PyQt5.QtCore import QTimer
        
        def scroll_to_bottom():
            scrollbar = self.chat_scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        QTimer.singleShot(100, scroll_to_bottom)
    
    def start_test_mode(self):
        """Start speech recognition test mode"""
        self.test_mode_active = True
        self.test_frame.show()
        self.current_test_index = 0
        self.show_next_test()
    
    def show_next_test(self):
        """Show next test sentence"""
        if self.current_test_index < len(self.test_sentences):
            sentence = self.test_sentences[self.current_test_index]
            self.test_sentence_label.setText(f'📢 Read this: "{sentence}"')
            self.test_result_label.setText("Click the mic button and read the sentence above")
        else:
            self.test_sentence_label.setText("✅ All tests completed!")
            self.test_result_label.setText("Test mode finished. Check results above.")
            self.test_mode_active = False
    
    def check_test_accuracy(self, transcribed_text):
        """Check accuracy of transcription against expected sentence"""
        if not self.test_mode_active or self.current_test_index >= len(self.test_sentences):
            return
        
        expected = self.test_sentences[self.current_test_index].lower()
        actual = transcribed_text.lower()
        
        # Calculate word accuracy
        expected_words = expected.split()
        actual_words = actual.split()
        
        correct = sum(1 for e, a in zip(expected_words, actual_words) if e == a)
        accuracy = (correct / len(expected_words)) * 100 if expected_words else 0
        
        # Store result
        result = {
            "test_num": self.current_test_index + 1,
            "expected": expected,
            "actual": actual,
            "accuracy": accuracy,
            "correct_words": correct,
            "total_words": len(expected_words)
        }
        self.test_results.append(result)
        
        # Show result
        result_text = f"Expected: {expected}\nGot: {actual}\n"
        result_text += f"Accuracy: {accuracy:.1f}% ({correct}/{len(expected_words)} words)"
        
        if accuracy >= 90:
            result_text += " ✅ Excellent!"
        elif accuracy >= 70:
            result_text += " ⚠️ Good"
        else:
            result_text += " ❌ Needs improvement"
        
        self.test_result_label.setText(result_text)
        self.current_test_index += 1
        
        # If all tests done, save log and show summary
        if self.current_test_index >= len(self.test_sentences):
            self.save_test_log()
            self.show_test_summary()
    
    def save_test_log(self):
        """Save test results to log file"""
        import json
        import os
        from datetime import datetime
        
        log_dir = os.path.expanduser("~/.samantha/logs")
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"speech_test_{timestamp}.json")
        
        avg_accuracy = sum(r["accuracy"] for r in self.test_results) / len(self.test_results)
        
        log_data = {
            "timestamp": timestamp,
            "average_accuracy": avg_accuracy,
            "results": self.test_results
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\n[Test Log] Saved to: {log_file}")
        print(f"[Test Log] Average Accuracy: {avg_accuracy:.1f}%")
    
    def show_test_summary(self):
        """Show test summary"""
        avg_accuracy = sum(r["accuracy"] for r in self.test_results) / len(self.test_results)
        
        summary = f"✅ All tests completed!\n\n"
        summary += f"Average Accuracy: {avg_accuracy:.1f}%\n\n"
        
        if avg_accuracy >= 90:
            summary += "🎉 Excellent! Speech recognition is working great!"
        elif avg_accuracy >= 70:
            summary += "👍 Good! Minor improvements needed."
        else:
            summary += "⚠️ Needs improvement. Adjusting settings..."
        
        self.test_sentence_label.setText(summary)
        self.test_result_label.setText("Check terminal for detailed log file location")
        self.test_mode_active = False

    # Thread-safe slot methods (called via signals from background threads)
    def _update_transcription(self, text):
        """Update transcription label (thread-safe via signal)"""
        if text:
            self.transcription_label.setText(text)
            self.transcription_label.show()
        else:
            self.transcription_label.hide()
    
    def update_volume_indicator(self, level):
        """Update volume indicator based on audio level"""
        if level < 0.1:
            self.volume_indicator.setText("🔇 Speak louder")
            self.volume_indicator.setStyleSheet("color: #FF6B6B; font-size: 12px; padding: 5px; background-color: #FFE5E5; border-radius: 10px;")
        elif level < 0.3:
            self.volume_indicator.setText("🔉 Good volume")
            self.volume_indicator.setStyleSheet("color: #FFB4A2; font-size: 12px; padding: 5px; background-color: #FFF5EE; border-radius: 10px;")
        else:
            self.volume_indicator.setText("🔊 Perfect!")
            self.volume_indicator.setStyleSheet("color: #4CAF50; font-size: 12px; padding: 5px; background-color: #E8F5E9; border-radius: 10px;")
        self.volume_indicator.show()

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
