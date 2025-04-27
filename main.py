## File: main.py
import asyncio
import os
import pyfiglet
from config import constants, Settings 
from core.session.creator import SessionCreator
from core.health import SessionHealth
from modules import OTPFetcher, BroadcastManager, GroupManager
from typing import List
from core.utils.logger import log


def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner_text = pyfiglet.figlet_format("XackerBot")
    print(f"{constants.CYAN}{banner_text}{constants.RESET}")
    print(f"{constants.YELLOW}---------------------------------{constants.RESET}")
    print(f"{constants.GREEN}      Created by Xacker Team     {constants.RESET}")
    print(f"{constants.YELLOW}---------------------------------{constants.RESET}")
    print(f"{constants.RED} Use this bot responsibly!{constants.RESET}")

def show_menu():
    print(f"\n {constants.GREEN}Menu:{constants.RESET}")
    print(f" {constants.CYAN}1.{constants.RESET} Create Session")
    print(f" {constants.CYAN}2.{constants.RESET} View Session")
    print(f" {constants.CYAN}3.{constants.RESET} Get OTP Code")
    print(f" {constants.CYAN}4.{constants.RESET} Multi-Broadcast  {constants.YELLOW}← NEW{constants.RESET}")
    print(f" {constants.CYAN}5.{constants.RESET} Group/Channel Tools    {constants.YELLOW}← NEW{constants.RESET}")
    print(f" {constants.CYAN}0.{constants.RESET} Exit")


async def main():
    while True:
        banner()
        show_menu()
        choice = input(f"\n {constants.YELLOW}Enter your choice: {constants.RESET}")
        
        if choice == "1":
            print(f" {constants.GREEN}Creating a new session...{constants.RESET}")
            await SessionCreator.create_session()
            log("Created new session", session_name="system")
            await asyncio.sleep(2)
        
        elif choice == "2":
            print(f" {constants.CYAN}Viewing existing sessions...{constants.RESET}")
            await SessionCreator.view_sessions()
            input(" Press Enter to go back...")
            await asyncio.sleep(2)
        
        elif choice == "3":  # Get OTP Code
            sessions = [f.replace(".session", "") for f in os.listdir(Settings.SESSION_DIR) if f.endswith(".session")]
    
            print(f"\n{constants.CYAN}Available Sessions ({len(sessions)})):{constants.RESET}")
            for i, session in enumerate(sessions, 1):
                print(f" {constants.YELLOW}{i}.{constants.RESET} {session}")
    
            try:
                selection = int(input("\nSelect session: ")) - 1
                if 0 <= selection < len(sessions):
                    print(f"{constants.GREEN}Waiting for OTP code... (Check your Telegram){constants.RESET}")
                    otp = await OTPFetcher.wait_for_otp(sessions[selection])
                    if otp:
                        print(f"\n{constants.GREEN}OTP Code: {constants.YELLOW}{otp}{constants.RESET}")
                    else:
                        print(f"{constants.RED}No OTP code found within 2 minutes{constants.RESET}")
            except ValueError:
                print(f"{constants.RED}Invalid selection!{constants.RESET}")
            
            input(" Press Enter to go back...")
            await asyncio.sleep(1)
        
        elif choice == "4":  # Multi-account broadcast
            sessions = [f.replace(".session", "") for f in os.listdir(Settings.SESSION_DIR) if f.endswith(".session")]
        
            if not sessions:
                print(f" {constants.RED}No sessions found!{constants.RESET}")
                await asyncio.sleep(1)
                continue
        
            print(f"\n {constants.CYAN}Available Sessions:{constants.RESET}")
            for i, session in enumerate(sessions, 1):
                status = "✅" if await SessionHealth.check_session(session) else "❌"
                print(f" {constants.YELLOW}{i}.{constants.RESET} {status} {session}")
        
            target = input("\nEnter target (username/ID): ")
            if not target:
                continue
        
            print("\nEnter your multi-line message (type '__END__' on a new line to finish):")
            lines = []
            while True:
                line = input()
                if line.strip() == "__END__":
                    break
                lines.append(line)
            message = "\n".join(lines)
        
            selected = input("Send from ALL sessions? (y/n): ").lower()
            if selected == "y":
                selected_sessions = sessions
            else:
                choices = input("Select sessions (comma-separated numbers): ")
                selected_sessions = [sessions[int(i)-1] for i in choices.split(",")]
        
            result = await BroadcastManager.mass_broadcast(selected_sessions, target, message)
            
            print(f"\n{constants.CYAN}Broadcast Completed!{constants.RESET}")
            print(f" Success: {result['success']}")
            print(f" Failed: {result['failed']}")
            print("\n Details:")
            for session, status in result['details'].items():
                print(f"  {session}: {status}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "5":  # New: Group Operations
            sessions = [f.replace(".session", "") for f in os.listdir(Settings.SESSION_DIR) if f.endswith(".session")]
            if not sessions:
                print(f" {constants.RED}No sessions found!{constants.RESET}")
                await asyncio.sleep(1)
                continue

            print(f"\n {constants.CYAN}Available Sessions:{constants.RESET}")
            for i, session in enumerate(sessions, 1):
                print(f" {constants.YELLOW}{i}.{constants.RESET} {session}")

            try:
                selection = int(input(f"\n {constants.YELLOW}Choose session (0 to cancel): {constants.RESET}"))
                if 1 <= selection <= len(sessions):
                    await GroupManager.group_operations_menu(sessions[selection - 1])
            except ValueError:
                print(f" {constants.RED}Invalid selection!{constants.RESET}")
                
                
        elif choice == "0":
            break 




if __name__ == "__main__":
    asyncio.run(main())