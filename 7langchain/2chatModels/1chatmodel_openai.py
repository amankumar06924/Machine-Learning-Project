from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model='gpt-4',temperature=0.5)
result = model.invoke("what is the cp of india")
print(result.content) # result mai bohot sare data hote hai like token output token and all isliye hum result.content use krenge take hume sirf response dikhe
 


