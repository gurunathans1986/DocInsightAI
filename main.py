import pandas as pd
import os
import re
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Load your GEMINI_API_KEY from .env

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

path = "./serialized_pdf.txt"

def read_text_file(file_path):
    """Read entire text file and return as string"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def callGemini(file_text,user_q):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
    model = genai.GenerativeModel("gemini-2.5-pro")  # type: ignore

    system_prompt = f"""
    You are a expert Document analyzer. You will be given with a text content of document which has HR policy content.
    Your task is to analyze the user's question and find the answer from the document and provide with a crisp answer
    You will be given with a document text and user question.    
    
    ##Output
    answer: <Your answer here>
    page_number: <Page number where the answer is found>
    reasoning: <Your reasoning for the answer>
    data_source: <Source of the data used to answer the question>

    ##Input
    document_text: {file_text}
    user_question: {user_q}  
    """
    response = model.generate_content(system_prompt)

    return response

def gemini_evaluate_answer(file_text,user_q,answer):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
    model = genai.GenerativeModel("gemini-2.5-pro")  # type: ignore

    system_prompt = f"""
    You are a expert Evaluator. You will be give with a text document , question, metadata and answer.
    Your task is evaluate the answer based on the document and question.

    ##Output
    is_correct: <true/false>
    score: <0-10>
    reasoning: <Your reasoning for the score>

    ##Input
    document_text: {file_text}
    question: {user_q}
    answer: {answer}  
    """
    response = model.generate_content(system_prompt)

    return response

def parse_evaloutput(output):
    try:
        result = {}
        # Patterns for each field
        is_correct_pattern = r'is_correct:\s*(.*?)(?=\n\s*score:|\Z)'
        score_pattern = r'score:\s*(.*?)(?=\n\s*reasoning:|\Z)'
        reasoning_pattern = r'reasoning:\s*(.*?)(?=\n|\Z)'

        is_correct = re.search(is_correct_pattern, output, re.IGNORECASE | re.DOTALL)
        score = re.search(score_pattern, output, re.IGNORECASE | re.DOTALL)
        reasoning = re.search(reasoning_pattern, output, re.IGNORECASE | re.DOTALL)

        result['is_correct'] = is_correct.group(1).strip() if is_correct else None
        result['score'] = score.group(1).strip() if score else None
        result['reasoning'] = reasoning.group(1).strip() if reasoning else None

        return result
    except Exception:
        return False


def parse_output(output):
    try:
        result = {}
        # Patterns for each field
        answer_pattern = r'answer:\s*(.*?)(?=\n\s*page_number:|\Z)'
        page_pattern = r'page_number:\s*(.*?)(?=\n\s*reasoning:|\Z)'
        reasoning_pattern = r'reasoning:\s*(.*?)(?=\n\s*data_source:|\Z)'
        data_source_pattern = r'data_source:\s*(.*?)(?=\n|\Z)'

        answer = re.search(answer_pattern, output, re.IGNORECASE | re.DOTALL)
        page = re.search(page_pattern, output, re.IGNORECASE | re.DOTALL)
        reasoning = re.search(reasoning_pattern, output, re.IGNORECASE | re.DOTALL)
        data_source = re.search(data_source_pattern, output, re.IGNORECASE | re.DOTALL)

        result['answer'] = answer.group(1).strip() if answer else None
        result['page_number'] = page.group(1).strip() if page else None
        result['reasoning'] = reasoning.group(1).strip() if reasoning else None
        result['data_source'] = data_source.group(1).strip() if data_source else None

        # Return result if at least answer is found
        if result['answer']:
            return result
        else:
            return False
    except Exception:
        return False


file_text = read_text_file(path)
while True:
    user_question = input("Enter your question (or type 'exit' or 'bye' to quit): ")
    if user_question.strip().lower() in ["exit", "bye"]:
        print("Exiting HR Policy Assistant.")
        break
    response = callGemini(file_text, user_question)
    output = parse_output(response.text)
    print("===== Output =====")
    print(f"Answer: {output['answer']}")
    print(f"Page Number: {output['page_number']}")
    print(f"Reasoning: {output['reasoning']}")
    print(f"Data Source: {output['data_source']}")

    file_output = f"""
        Answer: {output['answer']}
        Page Number: {output['page_number']}
        Reasoning: {output['reasoning']}
        Data Source: {output['data_source']}
        """

    eval_output = gemini_evaluate_answer(file_text, user_question, file_output) 
    eval_result = parse_evaloutput(eval_output.text)
    print("===== Evaluation Output =====")
    print(f"Is Correct: {eval_result['is_correct']}")
    print(f"Score: {eval_result['score']}")
    print(f"Reasoning: {eval_result['reasoning']}")