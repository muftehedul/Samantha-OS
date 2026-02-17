#!/usr/bin/env python3
"""
Samantha Skills - System operation capabilities
"""

import os
import subprocess
import psutil
from datetime import datetime
import pytz


class SystemSkills:
    """System operation and monitoring skills"""
    
    def __init__(self, restricted=False):
        self.restricted = restricted
    
    def get_datetime(self):
        """Get current date and time"""
        now = datetime.now()
        return {
            'datetime': now.strftime("%Y-%m-%d %H:%M:%S"),
            'date': now.strftime("%A, %B %d, %Y"),
            'time': now.strftime("%I:%M %p"),
            'day': now.strftime("%A"),
            'timestamp': now.timestamp()
        }
    
    def execute_command(self, command):
        """Execute system command and return detailed results"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, 
                text=True, timeout=30
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'return_code': result.returncode,
                'command': command
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_system_info(self):
        """Get system information"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
    
    def list_processes(self):
        """List running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
    
    def manage_service(self, service_name, action):
        """Manage systemd service"""
        if action not in ['start', 'stop', 'restart', 'status']:
            return {'success': False, 'error': 'Invalid action'}
        
        result = self.execute_command(f'systemctl {action} {service_name}')
        return result
    
    def read_file(self, filepath):
        """Read file contents"""
        try:
            with open(os.path.expanduser(filepath), 'r') as f:
                return {'success': True, 'content': f.read()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def write_file(self, filepath, content):
        """Write to file"""
        try:
            with open(os.path.expanduser(filepath), 'w') as f:
                f.write(content)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_directory(self, path='.'):
        """List directory contents"""
        try:
            path = os.path.expanduser(path)
            items = os.listdir(path)
            return {'success': True, 'items': items}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_disk_space(self):
        """Check disk space"""
        usage = psutil.disk_usage('/')
        return {
            'total': usage.total / (1024**3),  # GB
            'used': usage.used / (1024**3),
            'free': usage.free / (1024**3),
            'percent': usage.percent
        }
    
    def check_memory(self):
        """Check memory usage"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total / (1024**3),  # GB
            'available': mem.available / (1024**3),
            'used': mem.used / (1024**3),
            'percent': mem.percent
        }
    
    def kill_process(self, pid):
        """Kill process by PID"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return {'success': True, 'message': f'Process {pid} terminated'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
