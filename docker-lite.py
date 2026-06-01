#!/usr/bin/env python3
"""
Docker-Lite: Lightweight Container-like System for Mobile
Mimics Docker behavior without Docker overhead
"""

import os
import sys
import json
import subprocess
import time
import signal
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import threading
# import psutil - optional

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

class DockerLite:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()
        self.state_file = self.project_dir / ".docker-lite"
        self.logs_dir = self.project_dir / "logs"
        self.services_dir = self.project_dir / ".services"
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.services_dir.mkdir(exist_ok=True)
        
        # Load state
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load service state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_state(self):
        """Save service state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _log(self, level: str, msg: str, color: str = Colors.NC):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{timestamp}] [{level}]{Colors.NC} {msg}")
    
    def _success(self, msg: str):
        self._log("✓", msg, Colors.GREEN)
    
    def _error(self, msg: str):
        self._log("✗", msg, Colors.RED)
    
    def _info(self, msg: str):
        self._log("ℹ", msg, Colors.BLUE)
    
    def _warn(self, msg: str):
        self._log("⚠", msg, Colors.YELLOW)
    
    def up(self, services: Optional[List[str]] = None, detach: bool = False):
        """Start services (docker up)"""
        if services is None:
            services = ['webui', 'bot']
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Docker-Lite UP{Colors.NC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")
        
        self._info(f"Starting {len(services)} service(s)...")
        
        pids = []
        for service in services:
            pid = self._start_service(service)
            if pid:
                pids.append(pid)
        
        if pids:
            self.state['services'] = {svc: {'pid': pid, 'started': datetime.now().isoformat()} 
                                     for svc, pid in zip(services, pids)}
            self._save_state()
            self._success(f"Started {len(pids)} service(s)")
            self._print_access_info(services)
        
        if not detach:
            try:
                self._follow_logs(services)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Interrupt received. Stopping services...{Colors.NC}")
                self.down(services)
    
    def _start_service(self, service: str) -> Optional[int]:
        """Start individual service"""
        services_config = {
            'webui': {
                'cmd': [sys.executable, '-m', 'uvicorn', 'webui.app:app', 
                        '--host', '0.0.0.0', '--port', '8000'],
                'env': {'PORT': '8000'},
                'name': 'FastAPI WebUI',
            },
            'bot': {
                'cmd': [sys.executable, '-m', 'bot_service'],
                'env': {},
                'name': 'Telegram Bot',
            },
        }
        
        if service not in services_config:
            self._error(f"Unknown service: {service}")
            return None
        
        config = services_config[service]
        log_file = self.logs_dir / f"{service}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        try:
            self._info(f"Starting {config['name']}...")
            
            # Set environment
            env = os.environ.copy()
            env.update(config['env'])
            
            # Start process
            with open(log_file, 'w') as lf:
                process = subprocess.Popen(
                    config['cmd'],
                    cwd=self.project_dir,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    env=env,
                    preexec_fn=os.setsid  # Create process group
                )
            
            pid = process.pid
            
            # Wait a bit to ensure it started
            time.sleep(2)
            
            if process.poll() is not None:
                # Process died
                self._error(f"{service} failed to start")
                print("\nLog output:")
                with open(log_file) as f:
                    print(f.read()[-500:])  # Last 500 chars
                return None
            
            self._success(f"{config['name']} running (PID: {pid})")
            
            # Save service info
            if 'services' not in self.state:
                self.state['services'] = {}
            self.state['services'][service] = {
                'pid': pid,
                'log': str(log_file),
                'started': datetime.now().isoformat(),
            }
            self._save_state()
            
            return pid
        
        except Exception as e:
            self._error(f"Failed to start {service}: {e}")
            return None
    
    def down(self, services: Optional[List[str]] = None, force: bool = False):
        """Stop services (docker down)"""
        if services is None:
            services = list(self.state.get('services', {}).keys())
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Docker-Lite DOWN{Colors.NC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")
        
        stopped = 0
        for service in services:
            if service in self.state.get('services', {}):
                pid = self.state['services'][service].get('pid')
                if pid:
                    try:
                        # Kill process group
                        if force:
                            os.killpg(os.getpgid(pid), signal.SIGKILL)
                            self._warn(f"Killed {service} (PID: {pid})")
                        else:
                            os.killpg(os.getpgid(pid), signal.SIGTERM)
                            self._info(f"Terminating {service} (PID: {pid})...")
                            time.sleep(1)
                        
                        stopped += 1
                        del self.state['services'][service]
                    except ProcessLookupError:
                        self._warn(f"{service} already stopped")
                        if service in self.state.get('services', {}):
                            del self.state['services'][service]
        
        self._save_state()
        self._success(f"Stopped {stopped} service(s)")
    
    def ps(self):
        """List running services (docker ps)"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Docker-Lite PS{Colors.NC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")
        
        services = self.state.get('services', {})
        
        if not services:
            print("No services running")
            return
        
        print(f"{'SERVICE':<15} {'PID':<10} {'STATUS':<15} {'UPTIME':<20}")
        print("-" * 60)
        
        for name, info in services.items():
            pid = info.get('pid')
            started = datetime.fromisoformat(info.get('started', datetime.now().isoformat()))
            uptime = datetime.now() - started
            
            # Check if still running
            try:
                os.kill(pid, 0)
                status = f"{Colors.GREEN}running{Colors.NC}"
            except:
                status = f"{Colors.RED}stopped{Colors.NC}"
            
            uptime_str = str(uptime).split('.')[0]
            print(f"{name:<15} {pid:<10} {status:<15} {uptime_str:<20}")
    
    def logs(self, service: str, follow: bool = False, tail: int = 50):
        """View service logs (docker logs)"""
        if service not in self.state.get('services', {}):
            self._error(f"Service not found: {service}")
            return
        
        log_file = Path(self.state['services'][service].get('log'))
        
        if not log_file.exists():
            self._error(f"Log file not found: {log_file}")
            return
        
        print(f"\n{Colors.CYAN}Logs for {service}{Colors.NC}\n")
        
        if follow:
            # Follow logs like 'tail -f'
            try:
                with open(log_file) as f:
                    f.seek(0, 2)  # Go to end
                    while True:
                        line = f.readline()
                        if line:
                            print(line, end='')
                        else:
                            time.sleep(0.1)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Stopped following logs{Colors.NC}")
        else:
            # Show last N lines
            with open(log_file) as f:
                lines = f.readlines()
                for line in lines[-tail:]:
                    print(line, end='')
    
    def _follow_logs(self, services: List[str], tail: int = 20):
        """Follow all service logs in real-time"""
        print(f"\n{Colors.CYAN}Following logs (Ctrl+C to stop)...{Colors.NC}\n")
        
        # Get log files
        log_files = {}
        for service in services:
            if service in self.state.get('services', {}):
                log_file = self.state['services'][service].get('log')
                if log_file:
                    log_files[service] = Path(log_file)
        
        # Start following
        processes = []
        for service, log_file in log_files.items():
            cmd = ['tail', '-f', str(log_file)]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            processes.append((service, proc))
        
        try:
            while True:
                time.sleep(0.1)
                for service, proc in processes:
                    if proc.poll() is not None:
                        # Process died, try to restart
                        pass
        except KeyboardInterrupt:
            for service, proc in processes:
                proc.terminate()
    
    def _print_access_info(self, services: List[str]):
        """Print access information"""
        print(f"\n{Colors.GREEN}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Access Information{Colors.NC}")
        print(f"{Colors.GREEN}{'='*60}{Colors.NC}\n")
        
        if 'webui' in services:
            print(f"{Colors.CYAN}WebUI:{Colors.NC}")
            print(f"  Dashboard:   http://localhost:8000")
            print(f"  API Docs:    http://localhost:8000/docs")
            print(f"  Health:      http://localhost:8000/health")
            print()
        
        if 'bot' in services:
            print(f"{Colors.CYAN}Telegram Bot:{Colors.NC}")
            print(f"  Status:      Polling for messages")
            print(f"  Test:        Send /start to your bot")
            print()
        
        print(f"{Colors.CYAN}Logs:{Colors.NC}")
        print(f"  Directory:   {self.logs_dir}")
        print(f"  Command:     docker-lite logs <service> -f")
        print()
    
    def exec(self, cmd: List[str]):
        """Execute command in project context"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=False,
            )
            return result.returncode
        except Exception as e:
            self._error(f"Exec failed: {e}")
            return 1
    
    def stats(self):
        """Show resource usage (docker stats)"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Docker-Lite STATS{Colors.NC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")
        
        services = self.state.get('services', {})
        
        if not services:
            print("No services running")
            return
        
        print(f"{'SERVICE':<15} {'PID':<10} {'CPU%':<10} {'MEM (MB)':<15}")
        print("-" * 50)
        
        for name, info in services.items():
            pid = info.get('pid')
            try:
                proc = psutil.Process(pid)
                cpu_percent = proc.cpu_percent(interval=0.1)
                mem_mb = proc.memory_info().rss / 1024 / 1024
                print(f"{name:<15} {pid:<10} {cpu_percent:<10.1f} {mem_mb:<15.1f}")
            except:
                print(f"{name:<15} {pid:<10} {'N/A':<10} {'N/A':<15}")

def main():
    parser = argparse.ArgumentParser(
        description='Docker-Lite: Lightweight container-like system for mobile'
    )
    parser.add_argument('command', nargs='?', default='up',
                       choices=['up', 'down', 'ps', 'logs', 'stats', 'exec', 'help'])
    parser.add_argument('services', nargs='*', help='Services to operate on')
    parser.add_argument('-d', '--detach', action='store_true', help='Detach from logs')
    parser.add_argument('-f', '--follow', action='store_true', help='Follow logs')
    parser.add_argument('--tail', type=int, default=50, help='Number of lines to show')
    parser.add_argument('--force', action='store_true', help='Force kill services')
    
    args = parser.parse_args()
    
    docker_lite = DockerLite()
    
    if args.command == 'up':
        services = args.services if args.services else ['webui', 'bot']
        docker_lite.up(services, detach=args.detach)
    
    elif args.command == 'down':
        services = args.services if args.services else None
        docker_lite.down(services, force=args.force)
    
    elif args.command == 'ps':
        docker_lite.ps()
    
    elif args.command == 'logs':
        if not args.services:
            print("Usage: docker-lite logs <service> [-f] [--tail N]")
            return
        docker_lite.logs(args.services[0], follow=args.follow, tail=args.tail)
    
    elif args.command == 'stats':
        docker_lite.stats()
    
    elif args.command == 'exec':
        if not args.services:
            print("Usage: docker-lite exec <command>")
            return
        docker_lite.exec(args.services)
    
    elif args.command == 'help':
        print(f"""
{Colors.CYAN}Docker-Lite: Lightweight Container System for Mobile{Colors.NC}

{Colors.BLUE}Commands:{Colors.NC}
  up [services] [-d]     Start services (default: webui, bot)
                         -d: detach (run in background)
  
  down [services] [--force]  Stop services
                             --force: kill immediately
  
  ps                     List running services
  
  logs <service> [-f] [--tail N]  View service logs
                                  -f: follow logs
                                  --tail: number of lines (default: 50)
  
  stats                  Show resource usage
  
  exec <cmd>            Execute command in project context
  
  help                  Show this help

{Colors.BLUE}Examples:{Colors.NC}
  docker-lite up                    # Start all services
  docker-lite up webui              # Start WebUI only
  docker-lite up -d                 # Start detached
  docker-lite down                  # Stop all services
  docker-lite ps                    # List services
  docker-lite logs bot -f           # Follow bot logs
  docker-lite stats                 # Show resource usage
  docker-lite exec pytest tests/    # Run tests

{Colors.YELLOW}Note:{Colors.NC}
  This is a lightweight container-like system optimized for mobile.
  It provides Docker-like behavior without Docker overhead.
""")

if __name__ == '__main__':
    main()

