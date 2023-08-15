# 📖 Text Analysis Tutorials

This directory contains tutorials related to Text Analysis. It focuses on understanding and analyzing text data through different methodologies and techniques. There are two main tutorials to follow:

1. **basics-of-text-analysis.ipynb** - This tutorial introduces the foundational concepts and techniques in text analysis. It covers topics like tokenization, stemming, lemmatization, and more. You will learn how to prepare and process text data for various analyses, and experiment with a paper implementation.

2. **topic-modelling.ipynb** - This tutorial explores the fascinating world of topic modeling. Learn how to extract underlying topics from large collections of documents using different algorithms like Latent Dirichlet Allocation (LDA) and BERTopic.

## 🚀 Setup and Requirements

To successfully run the notebooks, you will need to have specific packages and models installed:

### SpaCy Language Model

The tutorials make use of SpaCy for various Natural Language Processing tasks, and the English language model `en_core_web_sm` is required. You can download it by executing the following in your terminal:

```bash
python -m spacy download en_core_web_sm
```

## Note on Multi-Processing
Some steps in the tutorials use multi-processing and batching for efficiency. If multi-processing does not work in your environment or causes any issues, you can modify the code by removing the batching and the number of processes arguments. The tutorials are designed to work without multi-processing as well, albeit at a slower pace.

## 🎓 Get Started
To install the text analysis specific requirements, run the following command:

```pip install -r text_analysis_requirements.txt```

Navigate to the desired notebook and follow the instructions and code blocks. Enjoy your journey through the engaging world of text analysis!