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

    
