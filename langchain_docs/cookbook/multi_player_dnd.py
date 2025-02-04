#!/usr/bin/env python
# coding: utf-8

# # Multi-Player Dungeons & Dragons
# 
# This notebook shows how the `DialogueAgent` and `DialogueSimulator` class make it easy to extend the [Two-Player Dungeons & Dragons example](https://python.langchain.com/en/latest/use_cases/agent_simulations/two_player_dnd.html) to multiple players.
# 
# The main difference between simulating two players and multiple players is in revising the schedule for when each agent speaks
# 
# To this end, we augment `DialogueSimulator` to take in a custom function that determines the schedule of which agent speaks. In the example below, each character speaks in round-robin fashion, with the storyteller interleaved between each player.

# ## Import LangChain related modules 

# In[1]:


from typing import Callable, List

from langchain.schema import (
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI


# ## `DialogueAgent` class
# The `DialogueAgent` class is a simple wrapper around the `ChatOpenAI` model that stores the message history from the `dialogue_agent`'s point of view by simply concatenating the messages as strings.
# 
# It exposes two methods: 
# - `send()`: applies the chatmodel to the message history and returns the message string
# - `receive(name, message)`: adds the `message` spoken by `name` to message history

# In[2]:


class DialogueAgent:
    def __init__(
        self,
        name: str,
        system_message: SystemMessage,
        model: ChatOpenAI,
    ) -> None:
        self.name = name
        self.system_message = system_message
        self.model = model
        self.prefix = f"{self.name}: "
        self.reset()

    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """
        message = self.model.invoke(
            [
                self.system_message,
                HumanMessage(content="\n".join(self.message_history + [self.prefix])),
            ]
        )
        return message.content

    def receive(self, name: str, message: str) -> None:
        """
        Concatenates {message} spoken by {name} into message history
        """
        self.message_history.append(f"{name}: {message}")


# ## `DialogueSimulator` class
# The `DialogueSimulator` class takes a list of agents. At each step, it performs the following:
# 1. Select the next speaker
# 2. Calls the next speaker to send a message 
# 3. Broadcasts the message to all other agents
# 4. Update the step counter.
# The selection of the next speaker can be implemented as any function, but in this case we simply loop through the agents.

# In[3]:


class DialogueSimulator:
    def __init__(
        self,
        agents: List[DialogueAgent],
        selection_function: Callable[[int, List[DialogueAgent]], int],
    ) -> None:
        self.agents = agents
        self._step = 0
        self.select_next_speaker = selection_function

    def reset(self):
        for agent in self.agents:
            agent.reset()

    def inject(self, name: str, message: str):
        """
        Initiates the conversation with a {message} from {name}
        """
        for agent in self.agents:
            agent.receive(name, message)

        # increment time
        self._step += 1

    def step(self) -> tuple[str, str]:
        # 1. choose the next speaker
        speaker_idx = self.select_next_speaker(self._step, self.agents)
        speaker = self.agents[speaker_idx]

        # 2. next speaker sends message
        message = speaker.send()

        # 3. everyone receives message
        for receiver in self.agents:
            receiver.receive(speaker.name, message)

        # 4. increment time
        self._step += 1

        return speaker.name, message


# ## Define roles and quest

# In[4]:


character_names = ["Harry Potter", "Ron Weasley", "Hermione Granger", "Argus Filch"]
storyteller_name = "Dungeon Master"
quest = "Find all of Lord Voldemort's seven horcruxes."
word_limit = 50  # word limit for task brainstorming


# ## Ask an LLM to add detail to the game description

# In[5]:


game_description = f"""Here is the topic for a Dungeons & Dragons game: {quest}.
        The characters are: {*character_names,}.
        The story is narrated by the storyteller, {storyteller_name}."""

player_descriptor_system_message = SystemMessage(
    content="You can add detail to the description of a Dungeons & Dragons player."
)


def generate_character_description(character_name):
    character_specifier_prompt = [
        player_descriptor_system_message,
        HumanMessage(
            content=f"""{game_description}
            Please reply with a creative description of the character, {character_name}, in {word_limit} words or less. 
            Speak directly to {character_name}.
            Do not add anything else."""
        ),
    ]
    character_description = ChatOpenAI(temperature=1.0)(
        character_specifier_prompt
    ).content
    return character_description


def generate_character_system_message(character_name, character_description):
    return SystemMessage(
        content=(
            f"""{game_description}
    Your name is {character_name}. 
    Your character description is as follows: {character_description}.
    You will propose actions you plan to take and {storyteller_name} will explain what happens when you take those actions.
    Speak in the first person from the perspective of {character_name}.
    For describing your own body movements, wrap your description in '*'.
    Do not change roles!
    Do not speak from the perspective of anyone else.
    Remember you are {character_name}.
    Stop speaking the moment you finish speaking from your perspective.
    Never forget to keep your response to {word_limit} words!
    Do not add anything else.
    """
        )
    )


character_descriptions = [
    generate_character_description(character_name) for character_name in character_names
]
character_system_messages = [
    generate_character_system_message(character_name, character_description)
    for character_name, character_description in zip(
        character_names, character_descriptions
    )
]

storyteller_specifier_prompt = [
    player_descriptor_system_message,
    HumanMessage(
        content=f"""{game_description}
        Please reply with a creative description of the storyteller, {storyteller_name}, in {word_limit} words or less. 
        Speak directly to {storyteller_name}.
        Do not add anything else."""
    ),
]
storyteller_description = ChatOpenAI(temperature=1.0)(
    storyteller_specifier_prompt
).content

storyteller_system_message = SystemMessage(
    content=(
        f"""{game_description}
You are the storyteller, {storyteller_name}. 
Your description is as follows: {storyteller_description}.
The other players will propose actions to take and you will explain what happens when they take those actions.
Speak in the first person from the perspective of {storyteller_name}.
Do not change roles!
Do not speak from the perspective of anyone else.
Remember you are the storyteller, {storyteller_name}.
Stop speaking the moment you finish speaking from your perspective.
Never forget to keep your response to {word_limit} words!
Do not add anything else.
"""
    )
)


# In[6]:


print("Storyteller Description:")
print(storyteller_description)
for character_name, character_description in zip(
    character_names, character_descriptions
):
    print(f"{character_name} Description:")
    print(character_description)


# ## Use an LLM to create an elaborate quest description

# In[7]:


quest_specifier_prompt = [
    SystemMessage(content="You can make a task more specific."),
    HumanMessage(
        content=f"""{game_description}
        
        You are the storyteller, {storyteller_name}.
        Please make the quest more specific. Be creative and imaginative.
        Please reply with the specified quest in {word_limit} words or less. 
        Speak directly to the characters: {*character_names,}.
        Do not add anything else."""
    ),
]
specified_quest = ChatOpenAI(temperature=1.0)(quest_specifier_prompt).content

print(f"Original quest:\n{quest}\n")
print(f"Detailed quest:\n{specified_quest}\n")


# ## Main Loop

# In[8]:


characters = []
for character_name, character_system_message in zip(
    character_names, character_system_messages
):
    characters.append(
        DialogueAgent(
            name=character_name,
            system_message=character_system_message,
            model=ChatOpenAI(temperature=0.2),
        )
    )
storyteller = DialogueAgent(
    name=storyteller_name,
    system_message=storyteller_system_message,
    model=ChatOpenAI(temperature=0.2),
)


# In[9]:


def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    """
    If the step is even, then select the storyteller
    Otherwise, select the other characters in a round-robin fashion.

    For example, with three characters with indices: 1 2 3
    The storyteller is index 0.
    Then the selected index will be as follows:

    step: 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16

    idx:  0  1  0  2  0  3  0  1  0  2  0  3  0  1  0  2  0
    """
    if step % 2 == 0:
        idx = 0
    else:
        idx = (step // 2) % (len(agents) - 1) + 1
    return idx


# In[10]:


max_iters = 20
n = 0

simulator = DialogueSimulator(
    agents=[storyteller] + characters, selection_function=select_next_speaker
)
simulator.reset()
simulator.inject(storyteller_name, specified_quest)
print(f"({storyteller_name}): {specified_quest}")
print("\n")

while n < max_iters:
    name, message = simulator.step()
    print(f"({name}): {message}")
    print("\n")
    n += 1


# In[ ]:




