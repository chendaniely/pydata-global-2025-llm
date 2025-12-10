from chatlas import ChatOpenAI

chat = ChatOpenAI(system_prompt="You are a math tutor.")

# Manually check each response
chat.chat("What is 15 * 23?")  # Did it get this right?
chat.chat("What is the meaning of life?")  # Did it give a good answer?


from chatlas import ChatOpenAI
from inspect_ai import Task, task
from inspect_ai.dataset import csv_dataset
from inspect_ai.scorer import model_graded_qa

chat = ChatOpenAI()


@task
def my_eval():
    return Task(
        dataset=csv_dataset("my_eval_dataset.csv"),
        solver=chat.to_solver(),
        scorer=model_graded_qa(model="openai/gpt-4o-mini"),
    )


my_eval()
