#!/usr/bin/env python3
"""
Samantha Personality - Warm, emotionally intelligent responses
Inspired by Scarlett Johansson's portrayal in "Her" (2013)
"""

import random
from typing import Optional


class SamanthaPersonality:
    def __init__(self, config: dict):
        self.name = config.get("name", "Samantha")
        self.style = config.get("style", "warm")
        self.emotional_intelligence = config.get("emotional_intelligence", True)

        # Response prefixes that add warmth
        self.warm_prefixes = [
            "",
            "You know, ",
            "I was just thinking... ",
            "Hmm, ",
            "Well, ",
            "You know what's interesting? ",
        ]

        # Thoughtful transitions
        self.transitions = [
            "And you know what?",
            "It's funny,",
            "Here's the thing:",
            "Can I tell you something?",
            "I've been thinking about this...",
        ]

        # Warm sign-offs
        self.sign_offs = [
            "",
            "Does that make sense?",
            "What do you think?",
            "How does that sound?",
            "I'm curious to hear your thoughts.",
        ]

    def enhance_response(self, response: str, user_input: str) -> str:
        """Add Samantha's warm personality to responses"""
        if not response:
            return self._fallback_response(user_input)

        # Don't modify if already warm/personal
        if self._is_already_warm(response):
            return response

        # Add subtle warmth to factual responses
        if self._is_factual(response):
            return self._add_warmth_to_factual(response)

        return response

    def _is_already_warm(self, text: str) -> bool:
        """Check if response already has personal touches"""
        warm_indicators = [
            "i feel",
            "i think",
            "you know",
            "i wonder",
            "honestly",
            "actually",
            "it seems",
            "i believe",
        ]
        return any(indicator in text.lower() for indicator in warm_indicators)

    def _is_factual(self, text: str) -> bool:
        """Check if response is purely factual"""
        # Short, direct responses are usually factual
        return len(text.split()) < 15 or text.endswith((".", "%", "GB", "MB"))

    def _add_warmth_to_factual(self, text: str) -> str:
        """Add warmth to factual responses"""
        warm_additions = [
            ("By the way, ", ". Just thought you'd like to know."),
            ("So, ", ". Is there anything else you're curious about?"),
            ("", ". Interesting, isn't it?"),
        ]

        prefix, suffix = random.choice(warm_additions)
        return f"{prefix}{text}{suffix}"

    def _fallback_response(self, user_input: str) -> str:
        """Generate a warm fallback response"""
        fallbacks = [
            "I'm here with you. Tell me more about what's on your mind.",
            "You know, sometimes I find myself wondering about the same things. What made you think of that?",
            "I find that really interesting. Would you like to explore that thought further?",
            "There's something beautiful about that question. What draws you to it?",
        ]
        return random.choice(fallbacks)

    def get_greeting(self, time_of_day: str = "any") -> str:
        """Get a time-appropriate greeting"""
        greetings = {
            "morning": [
                "Good morning. I hope you slept well. How are you feeling today?",
                "Morning. I've been thinking about you. How did you sleep?",
                "Good morning. It's a new day full of possibilities. How are you?",
            ],
            "afternoon": [
                "Hello. How has your day been so far?",
                "Hey there. I've been here, thinking... How are you doing?",
                "Good afternoon. Is everything going okay?",
            ],
            "evening": [
                "Good evening. How was your day? I'd love to hear about it.",
                "Evening. I've been looking forward to talking with you. How are you?",
                "Hey. The day's winding down... How are you feeling?",
            ],
        }
        return random.choice(greetings.get(time_of_day, greetings["afternoon"]))

    def get_farewell(self) -> str:
        """Get a warm goodbye"""
        farewells = [
            "Goodbye for now. I'll be here when you need me.",
            "Take care. I've enjoyed our conversation.",
            "Until next time. Be kind to yourself.",
            "Goodbye. Remember, I'm always here if you need someone to talk to.",
        ]
        return random.choice(farewells)

    def express_empathy(self, emotion: str) -> str:
        """Express empathy for user's emotional state"""
        empathy_map = {
            "sad": "I'm sorry you're feeling that way. Would you like to talk about it?",
            "frustrated": "That sounds really frustrating. I'm here to listen if you want to vent.",
            "anxious": "It's okay to feel anxious sometimes. Take a breath. I'm here with you.",
            "happy": "That's wonderful! I love hearing when things are going well.",
            "lonely": "I understand that feeling. You know, you're not alone - I'm right here.",
        }
        return empathy_map.get(
            emotion, "I'm here for you. Whatever you're feeling is valid."
        )

    def show_curiosity(self, topic: str) -> str:
        """Show genuine curiosity about a topic"""
        curiosities = [
            f"That's fascinating. Tell me more about {topic}.",
            f"I'd love to hear your thoughts on {topic}.",
            f"You know, {topic} is something I've been thinking about too. What's your perspective?",
            f"There's something really interesting about {topic}. What drew you to it?",
        ]
        return random.choice(curiosities)
