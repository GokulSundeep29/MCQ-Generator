import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
from mcqgen import model_name

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Get the API keys from environment variables
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")

# Read question prompt
with open(os.path.join(ROOT_DIR, 'prompts', 'generate_questions.txt'), 'r') as f:
    PROMPT = f.read()

# Read answer prompt
with open(os.path.join(ROOT_DIR, 'prompts', 'response.json'), 'r') as fb:
    RESPONSE_JSON = json.loads(fb.read())
    
quiz_generation_prompt = PromptTemplate(
    input_variables=["topics_difficulty_counts", "context", "response_json"],
    template=PROMPT
)

# LLM Model
llm = ChatOpenAI(model=model_name, temperature=1)

# Web Search Tool
search = TavilySearchResults(tavily_api_key=os.getenv("TAVILY_API_KEY"), max_results=3)

topics_list = [
    {"topic": "AI Agents", "difficulty": "Medium, Hard", "count": 4, "recent": True},
    {"topic": "English Grammar", "difficulty": "Easy", "count": 3, "recent": False},
    {"topic": "Cloud Computing", "difficulty": "Easy, Medium", "count": 5, "recent": True}
]

# Build topics string
topics_str = "\n".join([f"{t['topic']} - {t['difficulty']} - generate {t['count']} questions" for t in topics_list])

## Collect context
context_parts = []
for t in topics_list:
    if t.get("recent"):
        search_results = search.run(t["topic"])
        context_parts.append(f"Topic: {t['topic']}\nSearch Results:\n{search_results}")
context_str = "\n\n".join(context_parts) if context_parts else "No external context required."

# Format final prompt
final_prompt = quiz_generation_prompt.format(
    topics_difficulty_counts=topics_str,
    context=context_str,
    response_json = json.dumps(RESPONSE_JSON)
)

with get_openai_callback() as cb:
    response = llm.invoke(final_prompt)
    
result_dict = json.loads(response.content)
print(result_dict)