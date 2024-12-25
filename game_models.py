import random
import discord

from ui_get_answer import GetAnswerView


class Game:

    def __init__(self):
        self.started = False
        self.number_of_teams = 2
        self.teams = []
        self.players = {}
        self.info_message = None

    async def update_info_message(self):
        message_text = ""

        if self.info_message:

            for team in self.teams:
                message_text += f"```Team {self.teams.index(team) + 1}\n"
                team = sorted(list(team.values()), key=lambda player: player.score)

                for player_number in range(len(team)):
                    player = team[player_number]
                    message_text += f"\n{player_number + 1}\t{player.score}\t {player.user.name}"

                message_text += "```"

            message_text += "\nSelect your team:"
            await self.info_message.edit(content=message_text)


class Player:

    def __init__(self, user: discord.User,  team_number, game: Game, info_message: discord.Message):
        self.score = 0
        self.user = user
        self.game = game
        self.info_message = info_message
        self.hidden_parts = ["wiz tripped a ard on".split(), "cast and robe a and spell".split(), "soup turned into self him to".split()]
        self.opened_parts = []
        self.hidden_words = ["a wizard tripped on", "robe cast a spell and", "turned him self into soup"]
        self.opened_words = []
        self.team_number = team_number

        with open("questions.txt", "r", encoding="utf-8") as f:
            blocks = f.read().split("\n\n---\n\n")
            self.questions = [[question.split("\n") for question in block.split("\n\n")] for block in blocks]
            [random.shuffle(question_block) for question_block in self.questions]

        [team.pop(user.id) for team in game.teams if user.id in team]
        game.teams[team_number][user.id] = self
        game.players[user.id] = self

    async def handle_answer(self, answer):
        delete_delay = 20

        if self.questions:
            if self.questions[0]:

                if self.questions[0][0][1].lower() == answer.lower():
                    await self.user.send("Correct", delete_after=delete_delay)
                    self.score += 10 * (4 - len(self.questions))
                    self.questions[0].pop(0)
                    self.opened_parts.append(self.hidden_parts[0].pop(0))
                    if not self.hidden_parts[0]:
                        self.hidden_parts.pop(0)

                else:
                    await self.user.send("Incorrect", delete_after=delete_delay)

                if not self.questions[0]:
                    await self.update_info_message("Reassemble phrases from accumulated fragments")

            else:
                if self.hidden_words[0].lower() == answer.lower():
                    self.opened_words.append(self.hidden_words.pop(0))
                    self.questions.pop(0)
                    self.opened_parts.clear()
                    await self.user.send("Correct", delete_after=delete_delay)
                    self.score += 50 * len(self.opened_words)
                else:
                    await self.user.send("Incorrect", delete_after=delete_delay)

            if self.questions[0]:
                await self.update_info_message(self.questions[0][0][0])

        else:
            await self.update_info_message("You've completed the game!", buttons=False)

    async def update_info_message(self, text="", buttons=True):
        view = GetAnswerView(self) if buttons else None
        info = (f"Your score: {self.score}\n"
                f"Fragments found: {' '.join(self.opened_parts)}\n"
                f"Words discovered: {' '.join(self.opened_words)}\n")

        await self.info_message.edit(content=info + text, view=view)
        await self.game.update_info_message()
