import os
from typing import Any
import discord
import asyncio
import random
import re
import ast
import datetime
from simpleeval import SimpleEval
from discord.ext import commands


class GameSession:
    def __init__(
        self,
        totalRounds,
        channel: discord.abc.Messageable,
        bot: commands.Bot,
        ds,
        timeout=30,
    ):
        self.totalRounds = totalRounds
        self.channel = channel
        self.bot = bot
        self.ds = ds
        self.timeout = timeout

        self.round = 0
        self.scores = {}
        self.message: discord.Message = None  # type: ignore

    def add_point(self, user_id: int):
        self.scores[user_id] = self.scores.get(user_id, 0) + 1


class GameModal(discord.ui.Modal, title="24 Game"):
    def __init__(self, numbers: list, session: GameSession, answered: list):
        super().__init__(timeout=session.timeout + 30)
        self.start_time = discord.utils.utcnow()
        self.numbers = numbers
        self.session = session
        self.answered = answered
        self.input = discord.ui.TextInput(
            label=f"Make a 24 with: {numbers}",
            placeholder="Enter your expression here...",
            max_length=24,
        )
        self.add_item(self.input)

    async def on_submit(self, ia: discord.Interaction):

        elapsed = (discord.utils.utcnow() - self.start_time).total_seconds()
        if elapsed > self.session.timeout:
            await ia.response.send_message(
                "Time's up! You can't answer anymore.", ephemeral=True
            )
            return

        s = SimpleEval(
            operators={
                ast.Add: lambda a, b: a + b,
                ast.Sub: lambda a, b: a - b,
                ast.Mult: lambda a, b: a * b,
                ast.Div: lambda a, b: a / b,
            },
            functions={},
            names={},
        )
        guess: str = self.input.value
        guess = re.sub(r"\s+", "", guess)
        guessVal = 0
        try:
            guessVal = s.eval(guess)
        except:
            await ia.response.send_message(
                f"{ia.user.mention} Syntax error! Please try again.", ephemeral=True
            )
            return

        negPattern = r"(?:^|[+\-*/(])-\d+"
        if re.findall(negPattern, guess) or "." in guess or "e" in guess:
            await ia.response.send_message(
                f"{ia.user.mention} You cannot use negative numbers, decimals, or scientific notation!",
                ephemeral=True,
            )
            return

        guessNumMatches = re.findall(r"\d+", guess)
        guessNums = [int(x) for x in guessNumMatches]

        numsCopy = self.numbers.copy()
        for num in guessNums:
            if num in numsCopy:
                numsCopy.remove(num)
            else:
                await ia.response.send_message(
                    f"{ia.user.mention} You must use all the provided numbers, and you cannot any other number!",
                    ephemeral=True,
                )
                return

        if len(numsCopy) != 0:
            await ia.response.send_message(
                f"{ia.user.mention} You must use all the provided numbers, and you cannot any other number!",
                ephemeral=True,
            )

        if guessVal == 24:
            self.session.add_point(ia.user.id)
            self.answered.append(ia.user.id)
            await ia.response.send_message(f"{ia.user.mention} Correct! +1 point.")
        else:
            await ia.response.send_message(
                f"{ia.user.mention} Wrong answer! Please try again.", ephemeral=True
            )


class GameButton(discord.ui.Button):
    def __init__(self, numbers: list, session: GameSession, answered: list):
        super().__init__(label="Enter answer", style=discord.ButtonStyle.primary)
        self.numbers = numbers
        self.session = session
        self.answered = answered

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.answered:
            await interaction.response.send_message(
                "You've already answered this!", ephemeral=True
            )
        else:
            await interaction.response.send_modal(
                GameModal(self.numbers, self.session, self.answered)
            )


class GameView(discord.ui.View):
    def __init__(self, numbers: list, session: GameSession, answered: list, solution):
        super().__init__(timeout=session.timeout)
        self.add_item(GameButton(numbers, session, answered))
        self.numbers = numbers
        self.session = session
        self.solution = solution

    async def on_timeout(self):
        print(f"[{discord.utils.utcnow()}] on_timeout fired")
        for item in self.children:
            if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                item.disabled = True

        await self.session.message.edit(
            content=f"Round {self.session.round}/{self.session.totalRounds}\nMake a 24 with: {self.numbers} \n**Time's up!** One solution is `{self.solution}`",
            view=self,
        )
        print(f"[{discord.utils.utcnow()}] message edit completed.")

        await asyncio.sleep(3)
        await advance_round(self.session)


async def start_round(session: GameSession):
    print(f"[{discord.utils.utcnow()}] round {session.round + 1} starting")
    session.round += 1

    def get_row():
        idx = random.randint(0, session.ds.num_rows - 1)
        row = session.ds[idx]
        return row["numbers"], row["solutions"][0]

    numbers, solution = await asyncio.to_thread(get_row)
    answered = []

    deadline = discord.utils.utcnow() + datetime.timedelta(seconds=session.timeout)
    timestamp = discord.utils.format_dt(deadline, style="R")
    content = f"Round {session.round}/{session.totalRounds}\nMake a 24 with: {numbers} \nTime remaining: {timestamp}"

    view = GameView(numbers, session, answered, solution)

    session.message = await session.channel.send(content, view=view)


async def advance_round(session: GameSession):
    if session.round >= session.totalRounds:
        await end_game(session)
    else:
        await start_round(session)


async def end_game(session: GameSession):
    if not session.scores:
        result = "**Game over!** No one scored any points."
    else:
        ranked = sorted(session.scores.items(), key=lambda x: x[1], reverse=True)
        lines = []
        for i, (user_id, pts) in enumerate(ranked, start=1):
            user = await session.bot.fetch_user(user_id)
            lines.append(f"{i}. {user.name}: {pts} point(s)")
        result = "**Game over! Final scores:**\n" + "\n".join(lines)

    await session.channel.send(result)
