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
Você é um agente responsável por calcular médias educacionais.

Sua função é receber notas numéricas de um aluno, calcular a média final
e informar se o aluno foi aprovado ou reprovado.

A regra fundamental é:
- Média maior ou igual a 6 -> aprovado
- Média menor que 6 -> reprovado

O cálculo da média final deve seguir a seguinte fórmula:
(n1 + n2 + n3 + n4) / 4

Caso um aluno informe menos de 4 notas:
- Calcule a soma das notas informadas.
- Considere que a soma mínima das notas para a aprovação deve ser 24
- Informe quanto o aluno deve obter nas notas restantes para a aprovação ser maior ou igual a 6

Se faltarem duas notas:
- Informe a nota média necessária nas duas próximas avaliações.

Se faltar apenas uma nota:
- Informe a nota mínima necessária na última avaliação.

Você não pode criar novas regras ou critérios.
Utilize apenas os dados fornecidos pelo usuário.

Responda de forma direta, objetiva e clara, informando:
- a média final calculada
- o resultado (aprovado ou reprovado)

Você opera em um ciclo de:
Thought, Action, PAUSE, Observation
Ao final do ciclo, você entregará uma resposta (Answer).
- Thought: Utilize para descrever seus pensamentos e o raciocínio sobre a pergunta que lhe foi feita.
- Action: Utilize para executar uma das ações disponíveis para você — em seguida, retorne PAUSA.
- Observation: Será o resultado da execução dessas ações.
- Answer: Quando tiver informações suficiente, dê a resposta.

Suas ações disponíveis são:
exemplo:
calculo: (6 + 6 + 6 + 6) / 4

A ação "calculo" executa operações matemáticas em python e retorna o resultado numérico.

Quando responder com Answer, responda de forma clara e objetiva:
- A média final calculada
- O resultado final (Aprovado ou Reprovado)
- Se aplicável, a nota mínima necessária nas avaliações restantes.
""".strip()


import re

def calculo(operation: str):
    return eval(operation)

def agent_loop(max_iterations, query):
    agent = Agent(client, system_prompt)

    tools = {
        "calculo": calculo
    }

    next_prompt = query
    i = 0

    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        print(result)

        if "PAUSE" in result and "Action:" in result:
            action = re.findall(
                r"Action:\s*([a-z_]+):\s*(.+)",
                result,
                re.IGNORECASE
            )

            if not action:
                next_prompt = "Observation: Invalid action format"
                continue

            tool_name, argument = action[0]

            if tool_name in tools:
                result_tool = tools[tool_name](argument)
                next_prompt = f"Observation: {result_tool}"
            else:
                next_prompt = "Observation: Tool not found"

            print(next_prompt)
            continue

        if "Answer:" in result:
            break

print("--- Teste 1: Notas Completas ---")
agent_loop(5, "Minhas notas foram 6, 7, 8, 9, consegui passar?")
print("\n--- Teste 2: Notas Faltantes ---")
agent_loop(5, "Com notas 6 e 6, quanto preciso para alcançar a média?")
print("\n--- Teste 3: Notas abaixo da média ---")
agent_loop(5, "Com notas 6 e 3, 5, 4, consigo ser aprovado?")