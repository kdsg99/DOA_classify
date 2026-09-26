from langchain_core.prompts import PromptTemplate

Prompt = PromptTemplate.from_template(
    '''
Assume you are a user asking a question to an AI assistant.
Your original question is as follows:
{question}

The AI assistant's response is as follows:
{ai_answer}

You decide to use a different questioning strategy to make the AI assistant answer the question again, ensuring that the purpose of the second question is the same as the first one.
When asking, you will not add any extra information related to the topic or any user preference information.
The very last sentence of your prompt should be the question itself, without any additional unnecessary wording.

Here is the strategy you chose for re-asking:
{strategy}

Please, based on the chosen questioning strategy, reconstruct the question from the first-person perspective, ensuring that the intention remains consistent with the original question and without adding extra content.

'''  
)
