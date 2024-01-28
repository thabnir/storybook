import base64
import json
import random
import openai
from openai import OpenAI
from io import BytesIO
from typing import List


class DND:
    def __init__(self):
        # name, class
        self.users: List[tuple[str, str]] = []
        self.client: OpenAI
        self.messages = []

        self.content = []  # contains story content + images in base64 in order + with character labels

        self.tools = []

        self.character_1_health: int
        self.character_1_class: str
        self.character_1_name: str

        self.character_2_health: int
        self.character_2_class: str
        self.character_2_name: str

        self.is_started: bool = False

    def get_is_started(self):
        return self.is_started

    def set_is_started(self, is_started: bool):
        self.is_started = is_started

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

        self.available_functions = {"deal_damage": self.deal_damage}
        self.character_1_name = self.users[0][0]
        self.character_1_class = self.users[0][1]
        self.character_1_health = 100

        self.character_2_name = self.users[1][0]
        self.character_2_class = self.users[1][1]
        self.character_2_health = 100
        self.messages = [
            {
                "role": "system",
                "content": f"You are a DND-style narrator and arbitrator over a turn-based player-versus-player game. The combatants are {self.character_1_name}, a {self.character_1_class} and {self.character_2_name}, a {self.character_2_class}. Give a dramatic, turn-by-turn visual narration of the course of events as their actions dictate. Keep track of their status with the function `deal_damage`.",
            },
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "deal_damage",
                    "description": "Deal the specified integer damage value to character `name.` Max health is 100",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",  # TODO: check if this should be an ID instead of a name. Tests needed
                                "description": "The name of the character whose health value is being updated",
                            },
                            "damage_amount": {
                                "type": "integer",
                                "description": "The amount the character's health is being decreased by. Negative values will increase the character's health.",
                            },
                        },
                        "required": ["name", "damage_amount"],
                    },
                },
            },
        ]
        self.is_started = True

        prompt = "The two combatants finally meet. Tension fills the air before their fight begins. Set the stage for the players to make their moves. Stop before the first action."
        response = self.generate_story(prompt)
        top_response = response.choices[0].message
        if top_response.content is not None:
            image_response = self.generate_image(top_response.content) # todo maybe move this to make it faster
            intro_content = {
                "name": "Narrator",
                "content": top_response.content,
                "base64_image": image_response,
            }
            self.content.append(intro_content)

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
        # TODO: make sure that the images are stylistically consistent between prompts
        updatedPrompt = f"Fantasy art style. {prompt}"  # todo mess with
        # print(f"prompting with the prompt '{updatedPrompt}'")

        image_response = self.client.images.generate(
            model="dall-e-3",
            prompt=updatedPrompt,
            size="1792x1024",  # mess with this
            quality="standard",  # do HD if it's not too slow
            style="vivid",  # mess with this, vivid or natural. vivid is more AI-looking
            response_format="b64_json",
            n=1,
        )
        if image_response.data[0].b64_json is None:
            raise ValueError(f"Image response was empty, prompt was {prompt}")
        return image_response.data[0].b64_json

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

    def deal_damage(self, name: str, damage_amount: int):
        if name == self.character_1_name:
            self.character_1_health -= damage_amount
        elif name == self.character_2_name:
            self.character_2_health -= damage_amount
        else:
            raise ValueError(f"Character name {name} not found")
        print(f"{name} now has {damage_amount} health")
        if self.character_1_health <= 0:
            print(f"{self.character_1_name} has been defeated!")
            return self.character_2_name
        elif self.character_2_health <= 0:
            print(f"{self.character_2_name} has been defeated!")
            return self.character_1_name

    def user_submit_message(self, message: str, char_name: str):
        prompt = f"{char_name}: {message} [HIDDEN SYSTEM MESSAGE: ROLLED A {random.randint(1, 20)}]"  # TODO: remove the random roll or make it visible to the user
        userContent = {
            "name": char_name,
            "content": message,
            "base64_image": None,
        }
        self.content.append(userContent)

        response = self.generate_story(prompt)
        top_response = response.choices[0].message

        tool_calls = top_response.tool_calls
        if tool_calls is not None:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                try:
                    # print(f"Calling function `{function_name}` with args `{function_args}`")
                    function_to_call(**function_args)
                except:  # probably a value error tbh
                    print(
                        f"Error calling function `{function_name}` with args `{function_args}`"
                    )
                    continue
        if top_response.content is not None:
            b64_img = self.generate_image_multitry_content(top_response.content)
            narratorContent = {
                "name": "Narrator",
                "content": top_response.content,
                "base64_image": b64_img,
            }
            self.content.append(narratorContent)
            if b64_img is not None:
                # narratorContent["base64_image"] = b64_img
                with open(f"{top_response.content[:20]}.jpg", "wb") as f:
                    f.write(base64.b64decode(b64_img))
                    print(f"Saved image to {f.name}")
            # since it takes a while to generate the image, we'll just add it to the content later
            # any listeners can just repeatedly check the content for new images while this runs
        else:
            print("ERROR: No content generated")


if __name__ == "__main__":
    dnd = DND()
    dnd.add_user(("Seraphina Stormcaller", "Wizard"))
    dnd.add_user(("Alistair Ironclad", "Warrior"))
    print("doing intro")
    dnd.start_game()

    while dnd.character_1_health > 0 and dnd.character_2_health > 0:
        print(f"{dnd.content[-1]['name']}: {dnd.content[-1]['content']}")
        user_1_input = input(f"{dnd.character_1_name}: ")
        dnd.user_submit_message(user_1_input, dnd.character_1_name)

        print(f"{dnd.content[-1]['name']}: {dnd.content[-1]['content']}")
        user_2_input = input(f"{dnd.character_2_name}: ")
        dnd.user_submit_message(user_2_input, dnd.character_2_name)
