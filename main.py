import sys
import subprocess
import psutil
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.layout import Layout
from rich import print as rprint
from rich.align import Align
import config_manager

console = Console()

def is_monitor_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'monitor.py' in proc.info['cmdline'] and sys.executable in proc.info['cmdline']:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def start_monitor():
    pid = is_monitor_running()
    if pid:
        console.print(f"[yellow]Monitor is already running with PID {pid}[/yellow]")
        return
        
    try:
        if sys.platform == "win32":
            subprocess.Popen([sys.executable, "monitor.py"], 
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008) # DETACHED_PROCESS = 0x00000008
        else:
            subprocess.Popen([sys.executable, "monitor.py"], 
                             start_new_session=True, 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        console.print("[green]Monitor started in background![/green]")
    except Exception as e:
        console.print(f"[red]Failed to start monitor: {e}[/red]")

def stop_monitor():
    pid = is_monitor_running()
    if not pid:
        console.print("[yellow]Monitor is not currently running.[/yellow]")
        return
        
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        console.print("[green]Monitor stopped.[/green]")
    except psutil.NoSuchProcess:
        console.print("[yellow]Process not found.[/yellow]")

def show_status():
    config = config_manager.load_config()
    targets = config.get("targets", [])
    
    pid = is_monitor_running()
    status_text = f"[bold green]RUNNING (PID: {pid})[/bold green]" if pid else "[bold red]STOPPED[/bold red]"
    
    console.print(Panel(f"Monitor Status: {status_text}", title="System Status", style="blue"))
    
    if not targets:
        console.print("[yellow]No targets configured.[/yellow]")
        return
        
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("ID", style="dim", width=4)
    table.add_column("Hostname")
    table.add_column("Port", justify="right")
    table.add_column("Check Interval (s)", justify="right")
    table.add_column("Max Retries", justify="right")
    
    for idx, t in enumerate(targets):
        table.add_row(str(idx), t["hostname"], str(t["port"]), str(t["check_interval"]), str(t["max_retries"]))
        
    console.print(table)

def add_target_menu():
    console.print("[bold cyan]--- Add New Target ---[/bold cyan]")
    hostname = Prompt.ask("Hostname or IP")
    port = IntPrompt.ask("Port number")
    interval = IntPrompt.ask("Check interval in seconds", default=60)
    retries = IntPrompt.ask("Max retries before alert", default=3)
    
    config_manager.add_target(hostname, port, interval, retries)
    console.print(f"[green]Added target {hostname}:{port} successfully![/green]")

def remove_target_menu():
    config = config_manager.load_config()
    targets = config.get("targets", [])
    if not targets:
        console.print("[yellow]No targets to remove.[/yellow]")
        return
        
    show_status()
    idx = IntPrompt.ask("Enter ID of target to remove")
    config_manager.remove_target(idx)
    console.print("[green]Target removed successfully.[/green]")

def config_telegram_menu():
    console.print("[bold cyan]--- Configure Telegram ---[/bold cyan]")
    config = config_manager.load_config()
    current_token = config.get("telegram_token", "")
    current_chat = config.get("telegram_chat_id", "")
    
    console.print(f"Current Token: {current_token if current_token else 'Not set'}")
    console.print(f"Current Chat ID: {current_chat if current_chat else 'Not set'}")
    
    token = Prompt.ask("Enter Telegram Bot Token", default=current_token)
    chat_id = Prompt.ask("Enter Telegram Chat ID", default=current_chat)
    
    config_manager.update_telegram_settings(token, chat_id)
    console.print("[green]Telegram settings updated successfully![/green]")

def main_menu():
    while True:
        console.clear()
        title_panel = Panel(Align.center("[bold cyan]Simple VPS Health Checker[/bold cyan]\n[dim]Monitor your servers with ease[/dim]"), style="cyan")
        console.print(title_panel)
        
        show_status()
        
        console.print("\n[bold magenta]Options:[/bold magenta]")
        console.print("1. Add Target")
        console.print("2. Remove Target")
        console.print("3. Configure Telegram Bot")
        console.print("4. Start Monitor")
        console.print("5. Stop Monitor")
        console.print("6. Exit")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            add_target_menu()
        elif choice == "2":
            remove_target_menu()
        elif choice == "3":
            config_telegram_menu()
        elif choice == "4":
            start_monitor()
        elif choice == "5":
            stop_monitor()
        elif choice == "6":
            break
            
        if choice != "6":
            Prompt.ask("\nPress Enter to continue")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting...[/yellow]")
        sys.exit(0)
