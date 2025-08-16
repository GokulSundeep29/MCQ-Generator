import os
import sys
import json
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcqgen import model_name
from mcqgen.logger import logging

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Get the API keys from environment variables
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")


def generate_mcq(topics_list):    
    """
    Function to generate multiple choice questions based on topics and difficulty levels.
    It uses the OpenAI API to generate questions and Tavily for web search results.
    """
    
    try:
        # Read question prompt
        logging.info("Starting MCQ generation process")
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
        search = TavilySearchResults(tavily_api_key=TAVILY_KEY, max_results=3)


        # Build topics string
        topics_str = "\n".join([f"{t['topic']} - {t['difficulty']} - generate {t['count']} questions" for t in topics_list])

        logging.info(f"Topics String: {topics_str}")
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
        logging.info("Successfully generated questions")
        return result_dict  
          
    except Exception as e:
        logging.error(f"Error in generating MCQs: {e}")
        return None
    