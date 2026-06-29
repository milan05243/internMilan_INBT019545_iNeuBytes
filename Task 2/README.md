# Sentiment Analysis using Machine Learning & Deep Learning

A comprehensive Sentiment Analysis project developed as **Task 2** for the **iNeuBytes Artificial Intelligence Internship**. This project performs binary sentiment classification on IMDb movie reviews using both **Machine Learning** and **Deep Learning** techniques and compares their performance.

---

# Project Overview

This project classifies IMDb movie reviews into **Positive** and **Negative** sentiments using three different models:

- Logistic Regression
- Support Vector Machine (Linear SVM)
- Bidirectional Long Short-Term Memory (Bi-LSTM)

The project demonstrates the complete Natural Language Processing (NLP) pipeline including data preprocessing, feature extraction, model training, evaluation, and comparison.

---

# Objectives

- Perform sentiment classification on IMDb movie reviews.
- Apply text preprocessing techniques.
- Implement traditional Machine Learning algorithms.
- Build a Deep Learning model using Bidirectional LSTM.
- Compare model performance using standard evaluation metrics.

---

# Features

- Text Cleaning & Preprocessing
- Stopword Removal
- Tokenization
- TF-IDF Vectorization
- Logistic Regression Classifier
- Linear Support Vector Machine (SVM)
- Bidirectional LSTM Network
- Model Performance Comparison
- Confusion Matrix Visualization
- Accuracy, Precision, Recall and F1-Score Evaluation

---

# Dataset

**Dataset:** IMDb Movie Reviews Dataset

- 50,000 Movie Reviews
- Binary Sentiment Classification
- Positive Reviews
- Negative Reviews

Source:
https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews

---

# Tech Stack

## Programming Language

- Python

## Machine Learning

- Scikit-learn
- Logistic Regression
- Linear SVM

## Deep Learning

- TensorFlow
- Keras
- Bidirectional LSTM

## NLP

- NLTK
- TF-IDF Vectorizer
- Tokenizer
- Padding

## Visualization

- Matplotlib
- Seaborn

---

# Project Structure

```text
Task 2/
│
├── Task_2_Sentiment_Analysis_ML_DL.ipynb
├── requirements.txt
├── README.md
├── ML_Pipeline_Diagram.png
├── Bidirectional_LSTM_Architecture.png
└── screenshots/
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/milan05243/internsMilan_INBT019545_iNeuBytes.git
```

Go to Task 2

```bash
cd "Task 2"
```

Install dependencies

```bash
pip install -r requirements.txt
```

Launch Jupyter Notebook

```bash
jupyter notebook
```

Open

```
Task_2_Sentiment_Analysis_ML_DL.ipynb
```

Run all cells.

---

# Machine Learning Pipeline

The workflow followed in this project:

IMDb Dataset

↓

Data Cleaning

↓

Text Preprocessing

↓

Train-Test Split

↓

TF-IDF Vectorization

↓

Logistic Regression

↓

Linear SVM

↓

Tokenizer & Padding

↓

Bidirectional LSTM

↓

Performance Evaluation

↓

Sentiment Prediction

---

# Evaluation Metrics

The following metrics are used for evaluating all models:

- Accuracy
- Precision
- Recall
- F1-Score
- Classification Report
- Confusion Matrix

---

# Architecture Diagrams

Included in this repository:

- ML Pipeline Diagram
- Bidirectional LSTM Architecture Diagram

---

# Results

The project compares the performance of:

- Logistic Regression
- Linear SVM
- Bidirectional LSTM

using the same IMDb dataset and evaluation metrics.

---

# Author

**Milan Choudhary**

Registration No.: **INBT019545**

Course ID: **AIINB10626**

Internship: **iNeuBytes Artificial Intelligence Internship**
