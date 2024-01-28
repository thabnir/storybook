import json
import openai
from openai import OpenAI
from typing import List


class DND:
    def __init__(self):
        # name, class
        self.users: List[tuple[str, str]] = []
        self.client: OpenAI
        self.messages = []
        self.tools = []

        self.character_1_health: int
        self.character_1_class: str
        self.character_1_name: str

        self.character_2_health: int
        self.character_2_class: str
        self.character_2_name: str

        self.is_started: bool = False

    def add_user(self, user: tuple[str, str]):
        self.users.append(user)

    def remove_user(self, user: tuple[str, str]):
        self.users.remove(user)

    def get_user(self, user_id: tuple[str, str]):
        for user in self.users:
            if user == user_id:
                return user
        return None

    def get_messages(self):
        return self.messages

    def get_last_message(self):
        return self.messages[-1]

    def start_game(self):
        if len(self.users) < 2:
            raise ValueError("Not enough users to start game")
        elif len(self.users) > 2:
            raise ValueError("Too many users to start game")
            # alternatively, we could just ignore the extra users
        self.client = OpenAI()

        self.available_functions = {"set_character_health": self.set_character_health}
        self.character_1_name = self.users[0][0]
        self.character_1_class = self.users[0][1]
        self.character_1_health = 20

        self.character_2_name = self.users[1][0]
        self.character_2_class = self.users[1][1]
        self.character_2_health = 20
        self.messages = [
            {
                "role": "system",
                "content": f"You are a DND-style narrator and arbitrator over a turn-based player-versus-player game. The combatants are {self.character_1_name}, a {self.character_1_class} and {self.character_2_name}, a {self.character_2_class}. Give a dramatic, turn-by-turn visual narration of the course of events as their actions dictate.", 
            },
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "set_character_health",
                    "description": "Set the health of character `name` to the specified integer value",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",  # TODO: check if this should be an ID instead of a name. Tests needed
                                "description": "The name of the character whose health value is being updated",
                            },
                            "new_health": {
                                "type": "integer",
                                "description": "The updated health value of the character",
                            },
                        },
                        "required": ["name", "new_health"],
                    },
                },
            },
        ]
        self.is_started = True

    def generate_story(
        self,
        prompt: str,
        role="user",
    ):
        self.messages.append({"role": role, "content": prompt})
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",
        )
        return response

    def generate_image(self, prompt: str):
        # TODO: make sure that the images are stylistically consistent
        updatedPrompt = f"Fantasy art style. {prompt}" # todo mess with
        print(f"prompting with the prompt '{updatedPrompt}'")
        image_response = self.client.images.generate(
            model="dall-e-3",
            prompt=updatedPrompt,
            size="1792x1024",  # mess with this
            quality="hd",  # do HD if it's not too slow
            style="vivid",  # mess with this, vivid or natural. vivid is more AI-looking
            n=1,
        )
        return image_response

    def generate_image_multitry_content(self, prompt: str, num_tries=2):
        try:
            image_response = self.generate_image(prompt)
            return image_response
        except openai.BadRequestError as e:
            print(
                f"Error: `{e}` trying again with a more PG prompt. {num_tries} tries left"
            )
            new_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Rewrite the following message to create a more PG visual that wouldn't violate a content guideline when made into an image: `{prompt}`",
                    }
                ],
            )
            new_prompt = new_response.choices[0].message.content
            if new_prompt is not None:
                return self.generate_image_multitry_content(new_prompt, num_tries - 1)
            else:
                print("Failed to generate a more PG prompt, giving up")

    def set_character_health(self, name: str, new_health: int):
        if name == self.character_1_name:
            self.character_1_health = new_health
        elif name == self.character_2_name:
            self.character_2_health = new_health
        else:
            raise ValueError(f"Character name {name} not found")
            # TODO: test this to see if it actually works
        print(f"{name} now has {new_health} health")
        if self.character_1_health <= 0:
            print(f"{self.character_1_name} has been defeated!")
        elif self.character_2_health <= 0:
            print(f"{self.character_2_name} has been defeated!")


if __name__ == "__main__":
    dnd = DND()
    dnd.add_user(("Seraphina Stormcaller", "Wizard"))
    dnd.add_user(("Alistair Ironclad", "Warrior"))
    dnd.start_game()
    prompt = "The two combatants finally meet. Tension fills the air before their fight begins. Set the stage for the players to make their moves. Stop before the first action."
    response = dnd.generate_story(prompt)
    print(response)
    top_response = response.choices[0].message

    print("Generating image with prompt:")
    print(top_response.content)

    if top_response.content is not None:
        image_response = dnd.generate_image(top_response.content)

        print(image_response)

    tool_calls = top_response.tool_calls
    if tool_calls is not None:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = dnd.available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            try:
                print(f"Calling function `{function_name}` with args `{function_args}`")
                function_response = function_to_call(**function_args)
            except:  # probably a value error tbh
                print(
                    f"Error calling function `{function_name}` with args `{function_args}`"
                )
                continue
