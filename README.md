# DocInsightAI
This project is an interactive Document Analyzer that uses Retrieval-Augmented Generation (RAG) to answer questions about any document you provide. It reads a serialized text version of your document and provides answers with reasoning, page numbers, and data sources. Each answer is also evaluated for correctness and quality.

## Features
- Extracts and uses document content from a text file
- Answers user questions using Gemini LLM
- Provides answer, page number, reasoning, and data source
- Evaluates each answer for correctness and quality
- Interactive loop: ask multiple questions until you type `exit` or `bye`

## Requirements
- Python 3.8+
- Google Gemini API access and API key
- Required Python packages:
  - `google-generativeai`
  - `python-dotenv`
  - `pandas`

## Setup
1. **Clone this repository** and navigate to the project folder.
2. **Install dependencies:**
   ```sh
   pip install google-generativeai python-dotenv pandas
   ```
3. **Prepare your document:**
   - Convert your PDF or other document to a text file (e.g., `serialized_pdf.txt`).
   - Place it in the project directory.
4. **Set up your `.env` file:**
   - Create a `.env` file in the project root with:
     ```env
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## Usage
Run the analyzer:
```sh
python main.py
```
- Enter your document question at the prompt.
- Type `exit` or `bye` to quit.

## Example
```
Enter your question (or type 'exit' or 'bye' to quit): What is the leave policy?
===== Output =====
Answer: ...
Page Number: ...
Reasoning: ...
Data Source: ...
===== Evaluation Output =====
Is Correct: ...
Score: ...
Reasoning: ...
```

## Customization
- To use a different document, update the `path` variable in `main.py`.
- You can add more evaluation logic or test cases as needed.

## License
This project is for internal use and demonstration purposes only.
