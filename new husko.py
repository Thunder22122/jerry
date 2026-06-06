import discord
from discord.ext import commands
import requests
import asyncio
import logging
import random
import os

# -------------------------------------------------------------------
# Global registry for all bot instances (including the master)
hosted_bots = []          # list of HuskoBot instances
hosted_tokens = set()     # set of tokens already in use
# -------------------------------------------------------------------

class HuskoBot(commands.Bot):
    def __init__(self, token, command_prefix=",", self_bot=True, **options):
        super().__init__(command_prefix=command_prefix, self_bot=self_bot, **options)
        self.token = token

        # Per‑bot state variables
        self.react_emoji = None
        self.stam_loop = False
        self.gc_loop = False
        self.antigc_on = False
        self.antigc_counter = 0
        self.auto_reply_users = {}
        self.auto_reply1_users = {}

        # AutoBeef variables
        self.autobeef_task = None
        self.autobeef_channel_id = None
        self.autobeef_delay = 3.5
        self.autobeef_index = 0

        # AutoCount variables
        self.autocount_task = None
        self.autocount_channel_id = None
        self.autocount_target = None
        self.autocount_current = 1
        self.autocount_delay = 1.0

        # Stam variables
        self.stam_delay = 4.0
        self.stam_channel_id = None

        # Anti‑gc data (same as original)
        self.antigc_data = {
            "antigc_messages": [
                "# this doesn't phase me at all",
                "ur a nobody and i dont acknowledge u",
                "garbage attempt",
                "this was awkward as fuck",
            ],
            "antigc_names": [
                "sit the fuck down u cant hang with me ",
                "this doesnt scare me at all ur a little bitch",
                "you have anxiety + i mess with ur thoughts",
                "you need backup because you're not good enough"
            ],
        }

        # The full beef message list (unchanged, copied from original)
        self.beef_messages = [
            "SLOW ASS LITTLE BITCH",
            "CORNY FUCKING FAGGOT",
            "GAY ASS BITCH",
            "UR ASS AS FUCK NIGGA",
            "SHITTY LITTLE BITCH",
            "UR MY SON",
            "FAT ASS NIGGA",
            "OBESE ASS RETARD",
            "SISSY ASS FAGGOT",
            "FAT ASS BITCH",
            "RETARDED LITTLE FUCKING DORK",
            "STUPID ASS RETARD",
            "SLOW LITTLE FUCKING DORK",
            "INSECURE ASS PEDO",
            "DUMBASS BITCH UR ASS",
            "CORNY LITTLE DORK",
            "PEDO ASS BITCH",
            "SLOW ASS THOT",
            "THOTTY ASS NIGGA",
            "UR MY SON",
            "UR FAT AS FUCK",
            "UR ASS AS FUCK NIGGA",
            "SHITTY ASS BITCH",
            "THOTTY ASS NIGGA",
            "SLOW LITTLE BITCH",
            "YOURE A FUCKING RETARD",
            "FAT ASS CUCK",
            "UR MY FUCKING SON",
            "SPED ASS BITCH",
            "SLOW LITTLE DOGSHIT ASS NIGGA",
            "FAGGOT ASS NIGGA",
            "QUEER ASS PUSSY",
            "NIGGA YOURE A PEDO",
            "TRASH ASS LITTLE SHITCAN",
            "LAME ASS LITTLE WHORE",
            "YOUR A BUM",
            "YOUR SLOW AS FUCK",
            "UR MY BITCH NIGGA",
            "UR SORRY AS FUCK",
            "FAT ASS LITTLE BITCH",
            "TRASH ASS LITTLE CORNY BITCH",
            "UR LAME AS FUCK NIGGA",
            "NIGGA YOURE RETARDED",
            "UR GAY AS FUCK",
            "TRASH ASS LITTLE BITCH",
            "UR MY SON",
            "THOT ASS NIGGA",
            "UR A FUCKING RETARD",
            "UR GAY AS FUCK",
            "UR NOT GOOD",
            "BUM ASS BITCH",
            "UR CORNY",
            "UR MY FUCKING BITCH",
            "NIGGA UR MY SON",
            "THOT ASS LITTLE BITCH",
            "UR RETARDED AS FUCK",
            "UR SHITTY AS FUCK NIGGA",
            "UR ASS AS FUCK",
            "UR MY JR",
            "THOTTY ASS NIGGA",
            "FRAIL ASS LOSER",
            "WEAK ASS LITTLE BITCH",
            "UR SUBMISSIVE AS FUCK",
            "TRASH ASS PUSSY",
            "UR MY FUCKING SON",
            "THOT ASS BITCH UR A NERD",
            "UR BITCHMADE NIGGA",
            "BITCH ASS NIGGA",
            "UR FAT AS FUCK NIGGA",
            "UR SO SHITTY",
            "NERDY LITTLE BITCH",
            "FAGGOT ASS BITCH",
            "NIGGA UR NOT GOOD",
            "UR GAY NIGGA",
            "UR ASS NIGGA UR SLOW",
            "SLOW ASS RETARD",
            "TROGLODYTE ASS BITCH",
            "GAY ASS NIGGA",
            "QUEER ASS NIGGA",
            "TRASH ASS NIGGA",
            "UR NOT GOOD NIGGA",
            "GAY ASS LITTLE BITCH",
            "UR CORNY AS FUCK",
            "DUMBASS LITTLE BITCH",
            "UR A GAY ASS NIGGA",
            "THOT ASS LITTLE PEDO",
            "UR ASS AS FUCK LMFAO",
            "UR SO NASTY",
            "DISGUSTING ASS RETARD",
            "YOURE NASTY NIGGA",
            "UR TRASH AS FUCK",
            "GARBAGE ASS RETARD",
            "CORNY ASS LITTLE BITCH",
            "UR MY FUCKING BITCH",
            "UR NASTY",
            "UGLY ASS LITTLE SLUT",
            "TRASH ASS LITTLE FUCKING DORK",
            "SLUTTY ASS JUNIOR",
            "FRAIL ASS NIGGA",
            "UR A FUCKING LOSER",
            "UR A RETARDED FUCKING DORK",
            "UR A FUCKING LOSER",
            "BORING ASS RETARDED BITCH",
            "UGLY ASS NIGGA",
            "RETARDED ASS LITTLE BITCH",
            "CORNY ASS NIGGA",
            "BROKE LITTLE CUCK",
            "SHUT THE FUCK UP",
            "SASSY ASS LOSER",
            "GEEK LITTLE BITCH",
            "UR FUCKING TRASH",
            "UR A BITCH",
            "UR FUCKING WEAK",
            "SHUT THE FUCK UP BITCH",
            "SASSY ASS BITCH",
            "POOR ASS NIGGA",
            "PUSSY ASS NIGGA",
            "UR SO FUCKING DOGSHIT",
            "UR MY FUCKING BITCH",
            "UR FAT AS FUCK",
            "UR A SLUT",
            "YOUR A PEDO",
            "UGLY ASS NIGGA",
            "CORNY ASS NIGGA",
            "SHUT THE FUCK UP",
            "NIGGA UR SLOW AS SHIT",
            "UR MY BITCH",
            "UR A LITTLE SON",
            "UR A GEEK",
            "UR A FAGGOT",
            "UR SO FUCKING SLOW",
            "THOT ASS DORK",
            "UR RETARDED",
            "UR UGLY AS FUCK",
            "UR A LOSER",
            "UR SO FUCKING UGLY",
            "UR A FAGGOT",
            "UR SLOW AS FUCK",
            "UR SO FUCKING SLOW",
            "UR SHITTY",
            "DORK ASS NIGGA",
            "UR A DORK",
            "SHITTY ASS LITTLE BITCH",
            "RETARDED QUEER ASS NIGGA",
            "UR SLOW",
            "CORNY ASS NIGGA",
            "UR ASS",
            "UR LAME AS FUCK",
            "UR A FAGGOT",
            "UR MY FUCKING BITCH",
            "BITCH ASS LITTLE RETARD",
            "RETARDED ASS LITTLE NIGGA",
            "RETARDED ASS PEDO",
            "UR WEAK AS FUCK",
            "UR BROKE AS FUCK",
            "UR UGLY AS FUCK",
            "UR A FUCKING LOSER",
            "UR SHITTY",
            "UR SO FUCKING RETARDED",
            "NIGGA UR WEAK AS FUCK",
            "UR MY JR NIGGA",
            "UR MY FUCKING SON",
            "UR A POOR LITTLE BITCH",
            "UR SO ASS",
            "UR BORING AS FUCK",
            "UR A FUCKING THOT",
            "UGLY FUCKING DORK",
            "UR MAD AS FUCK",
            "UR SO FUCKING RETARDED",
            "UR FUCKING SOFT",
            "UR WEAK",
            "UR TRASH AS FUCK",
            "SLUTTY ASS NIGGA",
            "UR HORRIBLE AS FUCK",
            "RETARDED ASS SLUT",
            "UGLY ASS NIGGA",
            "UR SLOW AS FUCK WHORE",
            "THOT ASS NIGGA",
            "UR WEAK AND UR SOFT",
            "DOGSHIT ASS NIGGA",
            "SLOW FUCKING RETARD",
            "UR FAT AS FUCK",
            "UR CORNY AS FUCK",
            "SHUT THE FUCK UP",
            "YOUR GAY AS FUCK",
            "UGLY ASS LOSER",
            "UR SLOW AS FUCK",
            "UR WEAK AS FUCK",
            "LAME LITTLE FUCKING THOT",
            "UR TRASH",
            "UR BORING AS FUCK",
            "UR MY FUCKING SON",
            "LAME ASS NIGGA",
            "UR A LITTLE BITCH",
            "THOT ASS BITCH",
            "UR SOFT AS FUCK",
            "UR MY FUCKING WHORE",
            "UR A DORK",
            "UR ASS AS FUCK",
            "LOSER ASS NIGGA",
            "YOUR SASSY AS FUCK",
            "YOUR A LITTLE GEEK",
            "SHUT THE FUCK UP",
            "UR A LITTLE BITCH",
            "GAY ASS NIGGA",
            "SASSY ASS NIGGA",
            "SHUT THE FUCK UP",
            "RETARDED ASS FAGGOT",
            "UR UGLY AS FUCK",
            "LAME ASS NIGGA",
            "GEEK ASS NIGGA",
            "UR OBESE AS FUCK",
            "SASSY ASS NIGGA",
            "SHUT THE FUCK UP",
            "LITTLE POOR LOSER",
            "UR FUCKING DOGSHIT",
            "UR A LITTLE BITCH",
            "UGLY LITTLE BITCH",
            "SASSY ASS NIGGA",
            "UR SLOW AS FUCK",
            "UR A GEEK",
            "GEEK ASS NIGGA",
            "UR SASSY AS FUCK",
            "UR MY FUCKING SON LMAO",
            "UR GEEKY AS FUCK",
            "UR A BITCH",
            "UR MY BITCH",
            "UR A FUCKING WHORE",
            "SHUT THE FUCK UP",
            "UR A LITTLE LOSER",
            "GEEK ASS NIGGA",
            "UR A LITTLE BITCH",
            "UR A WHORE",
            "UR A LITTLE POOR LOSER",
            "SASSY ASS NIGGA",
            "SHITTY ASS LOSER",
            "UR A FUCKING THOT",
            "THOT ASS DORK",
            "SHUT THE FUCK UP",
            "UR A BITCH",
            "QUEER ASS NIGGA",
            "NIGGA UR SLOW AS FUCK",
            "UR A BITCH",
            "UR A LITTLE GEEK",
            "UR A FUCKING BITCH",
            "UR MY BITCH",
            "UR A LOSER",
            "UR A QUEER",
            "UR SLOW AS FUCK",
            "UR UGLY",
            "UR SOFT AND WEAK",
            "UGLY ASS RETARD",
            "GEEKY LITTLE FAGGOT",
            "UR FUCKING SLOW",
            "UR UGLY AS FUCK",
            "SLOW ASS BITCH",
            "YOUR MY JUNIOR",
            "THOT ASS NIGGA",
            "RETARDED ASS NIGGA",
            "YOUR A GEEK",
            "UR BROKE",
            "SHITTY ASS PUSSY",
            "FAT ASS NIGGA",
            "UR BROKE",
            "UR FUCKING SHITTY",
            "UR FUCKING RETARDED",
            "UR FUCKING FAT",
            "WEAK ASS BITCH",
            "YOUR MY JR",
            "YOUR SHITTY AS FUCK",
            "WEAK ASS BITCH",
            "UR LAME AS FUCK",
            "RETARDED ASS NIGGA",
            "UR A FUCKING LOSER",
            "UR A SLUT",
            "UGLY FUCKING FAGGOT",
            "UGLY ASS RETARD",
            "UR A FUCKING SLUT",
            "UR A FUCKING DORK",
            "SHITTY LITTLE RETARD",
            "UR FUCKING RETARDED",
            "GAY ASS FUCKING FAGGOT",
            "GAY ASS WHORE",
            "UR FUCKING SHITTY",
            "YOUR MY JUNIOR",
            "RETARDED SHITTY FUCK",
            "RETARDED ASS NIGGA",
            "UR A FUCKING SLUT",
            "YOUR MY JUNIOR",
            "THOT ASS NIGGA",
            "UR SOFT",
            "UR SLOW",
            "UR A FAGGOT",
            "UR FUCKING SLOW",
            "RETARDED ASS NIGGA",
            "UR BROKE",
            "UR FUCKING BROKE",
            "BROKE ASS FAGGOT",
            "RETARDED ASS NIGGA",
            "UR LAME AS FUCK",
            "UGLY ASS DORK",
            "UR A SLUT",
            "UR FUCKING WEAK",
            "SHITTY ASS LITTLE BITCH",
            "UR WEAK",
            "UR A WHORE",
            "FAT ASS NIGGA",
            "UR A FUCKING SLUT",
            "RETARDED SHITTY FUCK",
            "GEEKY LITTLE FAGGOT",
            "UR FUCKING TRASH",
            "UR FUCKING FAT",
            "RETARDED SHITTY FUCK",
            "GAY ASS WHORE",
            "UR SHITTY",
            "YOUR MY JUNIOR",
            "BITCH ASS LOSER",
            "UR A FUCKING WHORE",
            "RETARDED ASS NIGGA",
            "UR A SLUT",
            "THOT ASS NIGGA",
            "SHUT THE FUCK UP",
            "UR A WHORE",
            "FAT ASS NIGGA",
            "UR A WHORE",
            "UGLY FUCKING FAGGOT",
            "UGLY LITTLE BITCH",
            "YOUR SHITTY AS FUCK",
            "SHUT THE FUCK UP",
            "GAY ASS WHORE",
            "RETARDED FUCKING SLUT",
            "UR A WHORE",
            "UR A FUCKING DORK",
            "YOUR SHITTY AS FUCK",
            "GAY ASS FUCKING FAGGOT",
            "UR BROKE",
            "UR A FUCKING SLUT",
            "GAY ASS WHORE",
            "UR A FUCKING LOSER",
            "UR RETARDED",
            "UGLY DORK",
            "SLOW ASS NIGGA",
            "LITTLE BITCH",
            "UGLY FUCKING RETARD",
            "UR UGLY AS FUCK",
            "UR WEAK LITTLE NIGGA",
            "YOUR SLOW AS FUCK",
            "UR LAME AS FUCK",
            "UR RETARDED AS FUCK",
            "UR GAY AS FUCK",
            "UR A FUCKING LSOER",
            "POOR ASS NIGGA",
            "AWKARD ASS NIGGA",
            "UR SLOW AS FUCK",
            "UR A BITCH",
            "UR LAME AS FUCK",
            "UR POOR",
            "UR RETARDED AS FUCK",
            "UR SHIT AS FUCK",
            "UR A WHORE",
            "SHUT THE FUCK UP DORK",
            "YOUR A PEDO",
            "CRINGE ASS NIGGA",
            "UR A LITTLE MORON",
            "UR FUCKING DOGSHIT",
            "STUPID FUCKING DORK",
            "UR SHIT AS FUCK",
            "UR A STUPID FUCKING LOSER",
            "UR SLOW AS FUCK",
            "UR MY BITCH",
            "SASSY ASS GEEK",
            "CORNY ASS LOSER",
            "UGLY LITTLE NIGGA",
            "SHUT THE FUCK UP",
            "UR A RETARD",
            "UR A BITCH",
            "SHUT THE FUCK UP",
            "UR A FAGGOT",
            "UR SHIT AS FUCK",
            "UR A BITCH",
            "STUPID LOSER",
            "UR SLOW AS FUCK",
            "FAGGOT ASS NIGGA",
            "UR FAT",
            "UR SLOW AS FUCK",
            "UR A FUCKING LOSER",
            "UR ASS NIGGA",
            "SHUT THE FUCK UP",
            "LMFAO UR MY BITCH",
            "UGLY ASS NIGGA",
            "UR MY BITCH",
            "UR A FUCKING QUEER",
            "UR A RETARD",
            "UR SLOW",
            "FAGGOT ASS BITCH",
            "SHUT THE FUCK UP",
            "SASSY ASS NIGGA",
            "UR ASS UR A DORK",
            "SHIT ASS NIGGA",
            "RETARDED ASS NIGGA",
            "TRANNY ASS BITCH",
            "BITCH ASS NIGGA",
            "UR A BITCH",
            "SHUT THE FUCK UP LMAO",
            "UR A BITCH",
            "UR FAT AS FUCK",
            "UR A FUCKING LOSER",
            "QUEER ASS NIGGA",
            "FRAIL ASS NIGGA",
            "FAT LITTLE FUCKING NERD",
            "UR GARBAGE",
            "GAY ASS NIGGA",
            "YOUR SO FUCKING ASS",
            "YOUR A BITCH",
            "YOUR FRAIL AS FUCK",
            "YOUR A FUCKING GEEK",
            "YOUR A VICTIM",
            "UR SLUTTY AS FUCK",
            "UR A LITTLE FAGGOT",
            "YOUR TERRIBLE AS FUCK",
            "RETARDED ASS TRANNY",
            "UR UGLY AS FUCK",
            "YOUR MY BITCH",
            "YOUR A FUCKING PEDO",
            "SHUT UP DORK",
            "SLUTTY LITTLE NIGGA",
            "YOUR DISGUSTING",
            "WHORE ASS NIGGA",
            "CORNY ASS NIGGA",
            "YOUR A FUCKING GEEK",
            "LAME ASS NIGGA",
            "SHUT THE FUCK UP WHORE",
            "YOUR MY FUCKING SON",
            "UR SO SHITTY",
            "UR A LITTLE FAGGOT",
            "SHUT THE FUCK UP",
            "UR SO FUCKING ASS",
            "UR A BITCH",
            "NERD ASS NIGGA",
            "UR TRASH AS FUCK",
            "UR SLUTTY AS FUCK",
            "SHUT THE FUCK UP RETARD",
            "UR MY FUCKING SON",
            "UGLY ASS CUCK",
            "UR UGLY AS FUCK NIGGA",
            "SHUT THE FUCK UP",
            "UR SO FUCKING UGLY",
            "RETARDED LITTLE FUCKING CUCK",
            "CUCK ASS NIGGA",
            "UR A FUCKING DORK",
            "CRINGE ASS NIGGA",
            "UR LAME AS FUCK",
            "UR SLOW AS FUCK",
            "SHITTY ASS BITCH",
            "RETARDED ASS CRINGELORD",
            "UR MY FUCKING BITCH",
            "UR LONELY AS FUCK",
            "INEPT ASS FAGGOT",
            "CUCK ASS MORON",
            "SLOW ASS FUCKING FAGGOT",
            "DIRTY ASS NIGGA",
            "GROSS ASS MORON"
        ]

        # Register all events and commands
        self._register_events()
        self._register_commands()

    # -----------------------------------------------------------------
    # Event handlers
    # -----------------------------------------------------------------
    def _register_events(self):
        @self.event
        async def on_ready():
            print(f'logged in as {self.user}')

        @self.event
        async def on_message(message):
            if message.author == self.user:
                if self.react_emoji:
                    try:
                        await message.add_reaction(self.react_emoji)
                    except discord.errors.HTTPException as e:
                        if e.status != 400:
                            print(f"Error adding reaction: {e}")
                            raise

            if self.antigc_on:
                if isinstance(message.channel, discord.GroupChannel):
                    if message.type == discord.MessageType.recipient_add:
                        for user in message.mentions:
                            if user.id == self.user.id:
                                try:
                                    self.antigc_counter += 1
                                    headers = {"Authorization": self.token, "content-type": "application/json"}
                                    url = f"https://discord.com/api/v9/channels/{message.channel.id}"
                                    data = {"name": random.choice(self.antigc_data["antigc_names"]) + f" #{self.antigc_counter}"}
                                    response = requests.patch(url=url, headers=headers, json=data)
                                    response.raise_for_status()
                                    await message.channel.send(random.choice(self.antigc_data["antigc_messages"]) + f" (Attempt #{self.antigc_counter})")
                                    await message.channel.leave()
                                except Exception as e:
                                    print(f"Failed to leave GC: {e}")

            await self._handle_auto_replies(message)
            await self.process_commands(message)

    async def _handle_auto_replies(self, message):
        if message.author.id in self.auto_reply_users:
            try:
                await message.reply(self.auto_reply_users[message.author.id])
            except (discord.HTTPException, discord.Forbidden) as e:
                print(f'failed to auto reply {e}')

        if message.author.id in self.auto_reply1_users:
            try:
                await message.reply(f'A\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nA\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nA\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nA\n\n\n\n\n\n\n\n\n\n\n\nA\n\n\n\n\n\n\n\n\n\n\n\n{self.auto_reply1_users[message.author.id]}')
            except (discord.HTTPException, discord.Forbidden) as e:
                print(f'failed to auto reply {e}')

    # -----------------------------------------------------------------
    # Background loops
    # -----------------------------------------------------------------
    async def _autobeef_loop(self):
        current_delay = self.autobeef_delay
        while self.autobeef_channel_id is not None:
            try:
                message = self.beef_messages[self.autobeef_index]
                url = f"https://discord.com/api/v9/channels/{self.autobeef_channel_id}/messages"
                headers = {"authorization": self.token, "content-type": "application/json"}
                data = {"content": message}
                response = requests.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    print(f"[AutoBeef] Sent ({self.autobeef_index + 1}/{len(self.beef_messages)}): {message}")
                    self.autobeef_index = (self.autobeef_index + 1) % len(self.beef_messages)
                    current_delay = self.autobeef_delay
                elif response.status_code == 429:
                    retry_after = response.json().get("retry_after", 5)
                    print(f"[AutoBeef] Rate limited! Waiting {retry_after + 2}s")
                    await asyncio.sleep(retry_after + 2)
                    current_delay = retry_after + 2
                else:
                    print(f"[AutoBeef] Failed ({response.status_code}): {response.text}")
                    current_delay = min(current_delay * 1.5, 30)

                await asyncio.sleep(current_delay)
            except Exception as e:
                print(f"[AutoBeef] Error: {e}")
                await asyncio.sleep(10)
        print("[AutoBeef] Stopped.")

    async def _autocount_loop(self):
        current_delay = self.autocount_delay
        while self.autocount_channel_id is not None and self.autocount_current <= self.autocount_target:
            try:
                message = str(self.autocount_current)
                url = f"https://discord.com/api/v9/channels/{self.autocount_channel_id}/messages"
                headers = {"authorization": self.token, "content-type": "application/json"}
                data = {"content": message}
                response = requests.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    print(f"[AutoCount] Sent {self.autocount_current}/{self.autocount_target}")
                    self.autocount_current += 1
                    current_delay = self.autocount_delay
                elif response.status_code == 429:
                    retry_after = response.json().get("retry_after", 5)
                    print(f"[AutoCount] Rate limited! Waiting {retry_after + 2}s")
                    await asyncio.sleep(retry_after + 2)
                    current_delay = retry_after + 2
                else:
                    print(f"[AutoCount] Failed ({response.status_code}): {response.text}")
                    current_delay = min(current_delay * 1.5, 30)

                await asyncio.sleep(current_delay)
            except Exception as e:
                print(f"[AutoCount] Error: {e}")
                await asyncio.sleep(10)

        self.autocount_channel_id = None
        print("[AutoCount] Completed or stopped.")

    # -----------------------------------------------------------------
    # Command definitions (exactly as original, but with self. instead of globals)
    # -----------------------------------------------------------------
    def _register_commands(self):
        @self.command()
        async def ab(ctx, channel_id: str, delay: float = 3.5):
            await ctx.message.delete()
            if delay > 20:
                await ctx.send("Delay cannot exceed 20 seconds.", delete_after=5)
                return
            try:
                self.autobeef_channel_id = int(channel_id)
                self.autobeef_delay = delay
                self.autobeef_index = 0
                if self.autobeef_task is None or self.autobeef_task.done():
                    self.autobeef_task = asyncio.create_task(self._autobeef_loop())
                    await ctx.send(f"AutoBeef started in channel {channel_id} | Delay: {delay}s", delete_after=5)
                else:
                    await ctx.send("AutoBeef is already running! Use ,stopab first.", delete_after=5)
            except ValueError:
                await ctx.send("Invalid channel ID.", delete_after=5)

        @self.command()
        async def stopab(ctx):
            await ctx.message.delete()
            if self.autobeef_task and not self.autobeef_task.done():
                self.autobeef_channel_id = None
                self.autobeef_task.cancel()
                self.autobeef_task = None
                await ctx.send("AutoBeef stopped.", delete_after=5)
            else:
                await ctx.send("AutoBeef is not running.", delete_after=5)

        @self.command()
        async def autocount(ctx, *args):
            await ctx.message.delete()
            try:
                args_list = list(args)
                delay = 1.0
                if args_list and args_list[-1].replace('.', '', 1).isdigit():
                    delay = float(args_list.pop())
                    if delay > 20:
                        await ctx.send("Delay cannot exceed 20 seconds.", delete_after=5)
                        return
                channel_id = ctx.channel.id
                if args_list and args_list[-1].isdigit() and len(args_list[-1]) >= 17:
                    channel_id = int(args_list.pop())
                if len(args_list) != 1:
                    await ctx.send("Usage: ,autocount [target] [channel_id] [delay]", delete_after=5)
                    return
                target = int(args_list[0])
                if target <= 0:
                    await ctx.send("Target must be positive.", delete_after=5)
                    return
                self.autocount_target = target
                self.autocount_current = 1
                self.autocount_channel_id = channel_id
                self.autocount_delay = delay
                if self.autocount_task is None or self.autocount_task.done():
                    self.autocount_task = asyncio.create_task(self._autocount_loop())
                    await ctx.send(f"AutoCount started in channel {channel_id} to {target} | Delay: {delay}s", delete_after=5)
                else:
                    await ctx.send("AutoCount is already running! Use ,stopautocount first.", delete_after=5)
            except ValueError:
                await ctx.send("Invalid arguments.", delete_after=5)

        @self.command()
        async def stopautocount(ctx):
            await ctx.message.delete()
            if self.autocount_task and not self.autocount_task.done():
                self.autocount_channel_id = None
                self.autocount_task.cancel()
                self.autocount_task = None
                await ctx.send("AutoCount stopped.", delete_after=5)
            else:
                await ctx.send("AutoCount is not running.", delete_after=5)

        @self.command()
        async def react(ctx, emoji):
            await ctx.message.delete()
            self.react_emoji = emoji

        @self.command()
        async def stopreact(ctx):
            await ctx.message.delete()
            self.react_emoji = None

        @self.command()
        async def stam(ctx, *content):
            await ctx.message.delete()
            args = list(content)
            delay = 4.0
            if args and args[-1].replace('.', '', 1).isdigit():
                try:
                    delay = float(args.pop())
                    if delay > 20:
                        await ctx.send("Delay cannot exceed 20 seconds.", delete_after=5)
                        return
                except ValueError:
                    pass
            channel_id = ctx.channel.id
            if args and args[-1].isdigit() and len(args[-1]) >= 17:
                try:
                    channel_id = int(args.pop())
                except ValueError:
                    pass
            message = ' '.join(args)
            if not message:
                await ctx.send("Please provide a message.", delete_after=5)
                return
            self.stam_loop = True
            counter = 1
            while self.stam_loop:
                try:
                    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
                    headers = {"authorization": self.token, "content-type": "application/json"}
                    data = {'content': f"{message} {counter}"}
                    response = requests.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    counter += 1
                    await asyncio.sleep(delay)
                except requests.exceptions.RequestException as e:
                    logging.error(f'error making api request {e}')
                    await asyncio.sleep(10)

        @self.command()
        async def stamstop(ctx):
            await ctx.message.delete()
            self.stam_loop = False

        @self.command(name='gc')
        async def change_group_name(ctx, *, new_name: str):
            await ctx.message.delete()
            self.gc_loop = True
            counter = 1
            while self.gc_loop:
                try:
                    url = f'https://discord.com/api/v9/channels/{ctx.channel.id}'
                    headers = {"authorization": self.token, "content-type": "application/json"}
                    data = {'name': f'{new_name} {counter}'}
                    response = requests.patch(url, headers=headers, json=data)
                    response.raise_for_status()
                    counter += 1
                    await asyncio.sleep(0.01)
                except requests.RequestException as e:
                    print(f"Error making API request: {e}")
                    await asyncio.sleep(5)

        @self.command(name='sgc')
        async def stop_group_name(ctx):
            await ctx.message.delete()
            self.gc_loop = False

        @self.command(name='stream')
        async def start_stream(ctx, *, stream_status):
            try:
                await self.change_presence(activity=discord.Streaming(name=stream_status, url="https://twitch.tv/ata"))
            except Exception as e:
                print(f'failed to stream {e}')
            finally:
                await ctx.message.delete()

        @self.command(name='ss')
        async def stop_stream(ctx):
            try:
                await self.change_presence(activity=None)
            except Exception as e:
                print(f'failed to stop stream {e}')
            finally:
                await ctx.message.delete()

        @self.command('ar')
        async def auto_reply(ctx, user: discord.User, *, message):
            await ctx.message.delete()
            self.auto_reply_users[user.id] = message

        @self.command('sar')
        async def stop_autoreply(ctx, user: discord.User = None):
            await ctx.message.delete()
            if user is None:
                self.auto_reply_users.clear()
            else:
                if user.id in self.auto_reply_users:
                    del self.auto_reply_users[user.id]

        @self.command('ar1')
        async def auto_reply1(ctx, user: discord.User, *, message):
            await ctx.message.delete()
            self.auto_reply1_users[user.id] = message

        @self.command('sar1')
        async def stop_autoreply1(ctx, user: discord.User = None):
            await ctx.message.delete()
            if user is None:
                self.auto_reply1_users.clear()
            else:
                if user.id in self.auto_reply1_users:
                    del self.auto_reply1_users[user.id]

        @self.command(name='pfp')
        async def avatarUrl(ctx, user_info):
            if ctx.message.mentions:
                user = ctx.message.mentions[0]
            else:
                try:
                    user_id = int(user_info)
                    user = await self.fetch_user(user_id)
                except ValueError:
                    await ctx.send("Please mention a user or provide a valid user ID.")
                    return
                except discord.NotFound:
                    await ctx.send("User not found. Please provide a valid user ID.")
                    return
            if user:
                url = user.avatar_url_as(format='png', size=1024)
                await ctx.send(url)
            else:
                await ctx.send("User not found. Please provide a valid user or user ID.")

        @self.command(name='antigc')
        async def anti_gc(ctx, option):
            await ctx.message.delete()
            if option == "on":
                self.antigc_on = True
            else:
                self.antigc_on = False

        @self.command(name='purge')
        async def purge(ctx, limit: int = 20):
            def is_user(message):
                return message.author == ctx.author

            total_deleted = 0
            delay = 3
            try:
                if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.GroupChannel):
                    while total_deleted < limit:
                        try:
                            messages = await ctx.channel.history(limit=100).flatten()
                            deletions_in_batch = 0
                            for message in messages:
                                if message.type == discord.MessageType.default and is_user(message):
                                    try:
                                        await message.delete()
                                        total_deleted += 1
                                        deletions_in_batch += 1
                                        if total_deleted >= limit:
                                            break
                                    except discord.errors.HTTPException as e:
                                        if e.status == 429:
                                            await asyncio.sleep(delay)
                                            delay = 5
                                        elif e.status == 403 and e.code == 50021:
                                            continue
                                        else:
                                            print(f"HTTPException in purge command: {e}")
                                            raise
                            if deletions_in_batch == 0:
                                break
                        except Exception as e:
                            print(f"Unexpected error during message retrieval: {e}")
                            await ctx.send(f"An unexpected error occurred: {e}", delete_after=5)
                            break
                else:
                    deleted = await ctx.channel.purge(limit=limit, check=is_user)
                    total_deleted += len(deleted)
            except Exception as e:
                print(f"Unexpected error in purge command: {e}")
                await ctx.send(f"An unexpected error occurred: {e}", delete_after=5)

        # ---------- NEW COMMANDS: host and list ----------
        @self.command(name='host')
        async def host_token(ctx, token: str):
            """Host an additional token (multi‑token)."""
            await ctx.message.delete()
            if token in hosted_tokens:
                await ctx.send("That token is already being hosted.", delete_after=5)
                return
            try:
                new_bot = HuskoBot(token=token)
                hosted_tokens.add(token)
                hosted_bots.append(new_bot)
                # Start the bot in the background
                asyncio.create_task(new_bot.start(token))
                await ctx.send(f"Successfully hosted new token. Total hosted: {len(hosted_bots)}", delete_after=5)
            except Exception as e:
                await ctx.send(f"Failed to host token: {e}", delete_after=5)

        @self.command(name='list')
        async def list_tokens(ctx):
            """Show how many tokens are currently hosted."""
            await ctx.message.delete()
            await ctx.send(f"Currently hosting {len(hosted_bots)} token(s).", delete_after=5)

# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------
async def main():
    # The master token from the original TOKEN variable
    master_token = os.getenv("TOKEN")  # <-- replace with actual token or keep empty
    # For compatibility with the original code, we read the global TOKEN variable
    # However, the original code had `TOKEN = ""` at the top.
    # We'll use that variable if it exists, otherwise fallback.
    try:
        master_token = TOKEN
    except NameError:
        pass

    if not master_token:
        print("No token provided. Please set the TOKEN variable or pass a token when creating the master bot.")
        return

    master_bot = HuskoBot(token=master_token)
    hosted_tokens.add(master_token)
    hosted_bots.append(master_bot)

    try:
        await master_bot.start(master_token)
    except discord.LoginFailure:
        print("Invalid master token. Exiting.")
    except Exception as e:
        print(f"Master bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
