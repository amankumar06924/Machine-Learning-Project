from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

model = ChatAnthropic(mode='claude-3.5-sonnet-20241022',temperature=0.5,max_tokens_to_sample=50)

result = model.invoke("who is ai")

print(result.content) 