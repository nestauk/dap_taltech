## 💅 LLM tutorials

This directory contains tutorials related to LLMs. It primarily focuses on the practicalities of building LLM applications. There are two tutorials to follow along with:

1. `basics_of_langchains.ipynb` - This tutorial introduces the basics of LangChain and how to use the library to build LLM applications. It covers prompts, chains, agents and Retrieval Augmented Generation (RAG). There are **🛸 TASK** to complete along the way.

2. `llm_innovation_mapping.ipynb` - This tutorial applies what we learn in `basics_of_langchains.ipynb` to a fictional innovation mapping scenario. It serves as example project inspiration and provides codeblocks to use for your project work later in the hack week. 

### LLM set up

As we make extensive use of OpenAI LLMs and chat models, you will need to add the OpenAI API key as an environment variable. We will provide you with a key at the beginning of the hack week. 

You can do this by executing the following in your terminal:

```
export OPENAI_API_KEY="sk-.."
```
Alternatively, you can create a `.env` file in the root of this repository and add the following line to it:

```
OPENAI_API_KEY="sk-.."
```