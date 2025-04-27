# File: core/modules/group_tools.py
import asyncio
from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    ChannelInvalid,
    ChannelPrivate,
    UsernameNotOccupied,
    UserAlreadyParticipant
)
from config import Settings, constants
from core.utils.logger import log
from core.anti_ban import AntiBan

class GroupManager:
    
    
    @staticmethod
    async def join_group(client: Client, group_link: str):
        """
        Join a Telegram group/channel
        Args:
            client: Pyrogram client
            group_link: Username or invite link
        Returns:
            bool: True if successful
        """
        try:
            # Extract username from link if provided
            if "t.me/" in group_link:
                group_link = group_link.split("t.me/")[-1].split("/")[-1]
            
            await AntiBan.action_delay()
            await client.join_chat(group_link)
            log(f"Successfully joined: {group_link}")
            return True
            
        except UserAlreadyParticipant:
            log(f"Already in group: {group_link}")
            return True
        except (ChannelInvalid, ChannelPrivate, UsernameNotOccupied):
            log(f"Invalid group: {group_link}", level="error")
        except FloodWait as e:
            log(f"Flood wait: {e.value}s for {group_link}", level="warning")
            await asyncio.sleep(e.value)
            return await GroupManager.join_group(client, group_link)
        except Exception as e:
            log(f"Join error ({group_link}): {str(e)}", level="error")
        return False

    @staticmethod
    async def leave_group(client: Client, group_link: str):
        """
        Leave a Telegram group/channel
        Args:
            client: Pyrogram client
            group_link: Username or invite link
        Returns:
            bool: True if successful
        """
        try:
            if "t.me/" in group_link:
                group_link = group_link.split("t.me/")[-1].split("/")[-1]
            
            await AntiBan.action_delay()
            await client.leave_chat(group_link)
            log(f"Successfully left: {group_link}")
            return True
            
        except (ChannelInvalid, ChannelPrivate):
            log(f"Not in group: {group_link}")
            return True
        except FloodWait as e:
            log(f"Flood wait: {e.value}s for {group_link}", level="warning")
            await asyncio.sleep(e.value)
            return await GroupManager.leave_group(client, group_link)
        except Exception as e:
            log(f"Leave error ({group_link}): {str(e)}", level="error")
        return False
    
    @staticmethod
    async def group_operations_menu(session_name: str):
        client = Client(f"{Settings.SESSION_DIR}/{session_name}")
    
        async with client:
            while True:
                print(f"\n{constants.CYAN}Group Operations:{constants.RESET}")
                print("1. Join Group/Channel")
                print("2. Leave Group/Channel")
                print("3. Batch Join (from file)")
                print("4. Batch Leave (from file)")
                print("0. Back to Main Menu")
            
                choice = input(f"{constants.YELLOW}Select option: {constants.RESET}")
                
                if choice == "1":
                    link = input("Enter group link (@username or t.me link): ")
                    success = await GroupManager.join_group(client, link)
                    print(f"{constants.GREEN if success else constants.RED}{'Joined' if success else 'Failed'} {link}{constants.RESET}")
                    
                elif choice == "2":
                    link = input("Enter group link (@username or t.me link): ")
                    success = await GroupManager.leave_group(client, link)
                    print(f"{constants.GREEN if success else constants.RED}{'Left' if success else 'Failed'} {link}{constants.RESET}")
                    
                elif choice == "3":
                    file_path = input("Enter file path with links (one per line): ")
                    await batch_join(client, file_path)
                    
                elif choice == "4":
                    file_path = input("Enter file path with links (one per line): ")
                    await batch_leave(client, file_path)
                    
                elif choice == "0":
                    break
    @staticmethod
    async def batch_join(client: Client, file_path: str):
        try:
            with open(file_path) as f:
                links = [line.strip() for line in f if line.strip()]
                
            for link in links:
                success = await GroupManager.join_group(client, link)
                print(f"{link}: {'✓' if success else '✗'}")
                await asyncio.sleep(2)  # Rate limiting
                
        except Exception as e:
            print(f"{constants.RED}Error: {str(e)}{constants.RESET}")