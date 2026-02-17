#!/usr/bin/env python3
"""
Samantha OS - AI Assistant inspired by the movie "Her" (2013)
Minimalist, warm, emotionally intelligent AI companion
"""

__version__ = "1.0.0"
__author__ = "Samantha OS Project"

from .core import SamanthaCore
from .voice import VoiceEngine
from .personality import SamanthaPersonality

__all__ = ["SamanthaCore", "VoiceEngine", "SamanthaPersonality"]
