import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)


class Agent:
    def __init__(self, client, system):
        self.client = client
        self.system = system
        self.messages = []
        if self.system is not None:
            self.messages.append({"role": "system", "content": self.system})
    
    def __call__(self, message=''):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def execute(self):
        completion = client.chat.completions.create(
            messages=self.messages,
            model="llama-3.3-70b-versatile",
        )
        return completion.choices[0].message.content

system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

get_planet_mass:
e.g. get_planet_mass: Earth
returns weight of the planet in kg

Example session:

Question: What is the mass of Earth times 2?
Thought: I need to find the mass of Earth
Action: get_planet_mass: Earth
PAUSE

You will be called again with this:

Observation: 5.972e24

Thought: I need to multiply this by 2
Action: calculate: 5.972e24 * 2
PAUSE

You will be called again with this:

Observation: 1,1944x10e25

If you have the answer, output it as the Answer.

Answer: The mass of Earth times 2 is 1,1944x10e25.

Now it's your turn:
""".strip()

def calculate(operation):
    return eval(operation)

def get_planet_mass(planet) -> float:
    match planet.lower():
        case "Mercury": 
            return 3.301e23
        case "Venus": 
            return 4.867e24
        case "Earth": 
            return 5.972e24
        case "Mars": 
            return 6.417e23
        case"Jupiter": 
            return 1.899e27
        case "Saturn":
            return 5.685e26
        case "Uranus": 
            return 8.682e25
        case "Neptune": 
            return 1.024e26
        case _:
            return 0.0
        
neil_tyson = Agent(client, system_prompt)
neil_tyson.messages
result = neil_tyson("What is the mass of planet earth times 5?")
print(result)
observation = get_planet_mass("Earth")
print(observation)
next_prompt = f"Observation: {observation}"
result =  neil_tyson("What is the mass of planet earth times 5?")
print(result)
neil_tyson.messages
observation = calculate("3.285e23 * 5")
print(observation)

import re

def agent_loop(max_iterations, query):
    agent = Agent(client, system_prompt)
    tools = ['calculate', 'get_planet_mass']
    next_prompt = query
    i = 0
    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        print(result)

        if "PAUSE" in result and "Action" in result:
            action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)
            chosen_tool = action [0][0]
            arg = action [0][1]
        
            if chosen_tool in tools:
                result_tool = eval(f"{chosen_tool}('{arg}')")
                next_prompt = f"Observation: {result_tool}"
            
            else:
                next_prompt = "Observation: Tool not found"
                
            print(next_prompt)
            continue
        
        if "Answer" in result:
            break

