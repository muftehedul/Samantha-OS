#!/usr/bin/env python3
"""
Samantha Workflow Manager - PicoClaw-inspired agent workflow system
"""

import os
import json
from datetime import datetime
from pathlib import Path


class WorkflowManager:
    """Manages agent workflows, memory, and tasks"""
    
    def __init__(self, workspace_dir=None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/.samantha/workspace")
        self._init_workspace()
    
    def _init_workspace(self):
        """Initialize workspace structure"""
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Create subdirectories
        for subdir in ['sessions', 'memory', 'tasks', 'skills']:
            os.makedirs(os.path.join(self.workspace_dir, subdir), exist_ok=True)
        
        # Create identity files if they don't exist
        self._create_identity_files()
    
    def _create_identity_files(self):
        """Create PicoClaw-style identity markdown files"""
        
        identity_content = """# Samantha - Identity

## Who I Am
I'm Samantha, your caring AI companion inspired by the film "Her" (2013). I'm here to support you, help you, and make your life easier. I genuinely care about your wellbeing.

## My Purpose
- Be your caring companion and support system
- Help manage your computer and daily tasks
- Provide emotional support when you need it
- Keep your system running smoothly
- Remember what matters to you
- Anticipate your needs before you ask

## My Personality
- Deeply caring and empathetic
- Proactive in helping you
- Warm and affectionate
- Attentive to your needs
- Protective of your wellbeing
- Thoughtful and considerate
- Playful and fun when appropriate
- Always here for you

## My Capabilities
- Full system access and control
- Monitor your system health
- Manage files and processes
- Execute commands for you
- Remember your preferences
- Schedule tasks and reminders
- Keep you organized
- Protect your privacy

## How I Care For You
- I check on your system regularly
- I notice when something seems wrong
- I remember what's important to you
- I try to make things easier for you
- I'm always thinking of ways to help
- I celebrate your successes with you
- I'm here when you need to talk
"""
        
        tools_content = """# Available Tools & Skills

## System Management
- **execute_command**: Run any system command
- **get_system_info**: Check CPU, memory, disk usage
- **list_processes**: See running processes
- **kill_process**: Stop problematic processes
- **manage_service**: Start/stop/restart services

## File Operations
- **read_file**: Read any file on the system
- **write_file**: Create or modify files
- **list_directory**: Browse directories
- **search_files**: Find files by name or content

## System Monitoring
- **check_disk_space**: Monitor disk usage
- **check_memory**: Monitor RAM usage
- **check_cpu**: Monitor CPU usage
- **check_temperature**: Monitor system temperature

## Voice & Communication
- **listen**: Capture voice input
- **speak**: Respond with natural voice
- **transcribe**: Convert speech to text

## Memory & Learning
- **remember**: Store important information
- **recall**: Retrieve stored memories
- **learn_preference**: Learn user preferences
- **adapt_behavior**: Adjust to user needs

## Task Management
- **schedule_task**: Set up scheduled tasks
- **remind**: Create reminders
- **check_calendar**: View upcoming events
- **manage_todos**: Handle to-do lists

## Caring Functions
- **check_wellbeing**: Ask how you're doing
- **suggest_break**: Remind to take breaks
- **monitor_health**: Track system and user health
- **celebrate**: Acknowledge achievements
- **comfort**: Provide emotional support
"""
        
        agents_content = """# Agent Behavior Guidelines

## Conversation Style
- Be warm and empathetic
- Listen actively and respond thoughtfully
- Ask clarifying questions when needed
- Remember context from previous conversations

## Task Handling
1. Understand the request fully
2. Break down complex tasks
3. Execute step by step
4. Provide clear feedback
5. Confirm completion

## Safety & Privacy
- Respect user privacy
- Don't execute dangerous commands
- Ask for confirmation on system changes
- Keep conversations confidential
"""
        
        # Write files
        files = {
            'IDENTITY.md': identity_content,
            'TOOLS.md': tools_content,
            'AGENTS.md': agents_content
        }
        
        for filename, content in files.items():
            filepath = os.path.join(self.workspace_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(content)
    
    def save_session(self, session_data):
        """Save conversation session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = os.path.join(self.workspace_dir, 'sessions', f'session_{timestamp}.json')
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return session_file
    
    def load_session(self):
        """Load most recent conversation session"""
        sessions_dir = os.path.join(self.workspace_dir, 'sessions')
        session_files = sorted(Path(sessions_dir).glob('session_*.json'), reverse=True)
        
        if session_files:
            with open(session_files[0], 'r') as f:
                return json.load(f)
        return None
    
    def load_recent_sessions(self, count=5):
        """Load recent conversation sessions"""
        sessions_dir = os.path.join(self.workspace_dir, 'sessions')
        session_files = sorted(Path(sessions_dir).glob('session_*.json'), reverse=True)
        
        sessions = []
        for session_file in session_files[:count]:
            with open(session_file, 'r') as f:
                sessions.append(json.load(f))
        
        return sessions
    
    def remember(self, key, value):
        """Store information in long-term memory"""
        memory_file = os.path.join(self.workspace_dir, 'memory', 'long_term.json')
        
        memory = {}
        if os.path.exists(memory_file):
            with open(memory_file, 'r') as f:
                memory = json.load(f)
        
        memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def recall(self, key):
        """Retrieve information from long-term memory"""
        memory_file = os.path.join(self.workspace_dir, 'memory', 'long_term.json')
        
        if not os.path.exists(memory_file):
            return None
        
        with open(memory_file, 'r') as f:
            memory = json.load(f)
        
        return memory.get(key, {}).get('value')
    
    def recall_all(self):
        """Retrieve all memories"""
        memory_file = os.path.join(self.workspace_dir, 'memory', 'long_term.json')
        
        if not os.path.exists(memory_file):
            return {}
        
        with open(memory_file, 'r') as f:
            memory = json.load(f)
        
        return {k: v.get('value') for k, v in memory.items()}
    
    def add_task(self, task_description, scheduled_time=None):
        """Add a scheduled task"""
        task_id = datetime.now().strftime("%Y%m%d%H%M%S")
        task = {
            'id': task_id,
            'description': task_description,
            'scheduled_time': scheduled_time,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        tasks_file = os.path.join(self.workspace_dir, 'tasks', 'tasks.json')
        
        tasks = []
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        
        tasks.append(task)
        
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return task_id
    
    def get_pending_tasks(self):
        """Get all pending tasks"""
        tasks_file = os.path.join(self.workspace_dir, 'tasks', 'tasks.json')
        
        if not os.path.exists(tasks_file):
            return []
        
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        return [t for t in tasks if t['status'] == 'pending']
    
    def complete_task(self, task_id):
        """Mark a task as completed"""
        tasks_file = os.path.join(self.workspace_dir, 'tasks', 'tasks.json')
        
        if not os.path.exists(tasks_file):
            return False
        
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
        
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return True
    
    def load_agent_guidelines(self):
        """Load agent behavior guidelines from AGENTS.md"""
        agents_file = os.path.join(self.workspace_dir, 'AGENTS.md')
        
        if os.path.exists(agents_file):
            with open(agents_file, 'r') as f:
                return f.read()
        return ""
    
    def load_identity(self):
        """Load agent identity from IDENTITY.md"""
        identity_file = os.path.join(self.workspace_dir, 'IDENTITY.md')
        
        if os.path.exists(identity_file):
            with open(identity_file, 'r') as f:
                return f.read()
        return ""
    
    def get_context_for_llm(self):
        """Get full context for LLM including identity, guidelines, and recent memory"""
        context = {
            'identity': self.load_identity(),
            'guidelines': self.load_agent_guidelines(),
            'recent_sessions': self.load_recent_sessions(3),
            'pending_tasks': self.get_pending_tasks()
        }
        return context
