# Natural Language to SQL Tutorial

This project demonstrates how to build an AI-powered SQL agent that can convert natural language questions into SQL queries using LangChain and OpenAI.

## Features

- Natural language to SQL conversion
- Interactive database exploration
- Data visualization with pandas and matplotlib
- Sample employee database for learning

## Prerequisites

- Python 3.8+
- OpenAI API key
- Basic understanding of SQL and Python

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/oba2311/text2sql
   cd text2sql
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Project Structure

- `tutorial.ipynb`: Jupyter notebook with step-by-step tutorial
- `main.py`: Standalone Python script version
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (create this file)

## Usage

### Using the Jupyter Notebook (Recommended for Learning)

1. Start Jupyter:

   ```
   jupyter notebook
   ```

2. Open `tutorial.ipynb`
3. Run cells sequentially to:
   - Create a sample database
   - Explore data with visualizations
   - Query the database using natural language
