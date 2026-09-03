# Mini RAG

## Requirement


#### Install python using MiniConda





## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```
Set your environment variables in the `src/.env` file. Like `OPENAI_API_KEY` value .

## Run the FastAPI server 

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 8000
```