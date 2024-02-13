#!/usr/bin/env python
# coding: utf-8

# We start by loading a list of URLs from an Excel file named `Input.xlsx`. Each URL corresponds to an article we aim to analyze.

# In[70]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

input_file_path = "Input.xlsx"
df= pd.read_excel(input_file_path)

articles_list = []

def extract_and_save_article_content(url, url_id):
    try:
        response= requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content,'html.parser')
            title = soup.find('h1').get_text(strip=True)
            article_body = soup.find('article')
            article_text=article_body.get_text(separator=' ',strip=True) if article_body else "Article Not Found"
            
            
            articles_list.append({
                "id": url_id,
                "url": url,
                "title": title,
                "text": article_text
            })
          
        else:
            print(f'Failed to fetch data from the {url} with response code{response.status_code}')
    except Exception as e:
        print(f'An error occured while processing {url}:{e}')
        
for index, row in df.iterrows():
    extract_and_save_article_content(row['URL'],index)
with open('article.json','w', encoding='utf-8')as f:
    json.dump(articles_list,f,ensure_ascii=False, indent =4)


# Analysis from the extracted Data

# In[13]:


with open('article.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)


# In[7]:


import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import pandas as pd
import string
import os

nltk.download('punkt')


def load_stop_words(stop_words_dir):
    all_stop_words = []
    for filename in os.listdir(stop_words_dir):
        file_path = os.path.join(stop_words_dir, filename)
        with open(file_path, 'r') as file:
            all_stop_words.extend(file.read().splitlines())
    
    return list(set(all_stop_words))
stop_words_dir = "StopWords"
all_stop_words = load_stop_words(stop_words_dir)


# We preprocess the text data by removing punctuation, converting to lowercase, 
# and excluding stop words. The cleaned text is then tokenized for further 
# analysis.

# In[8]:


def clean_and_tokenize(text):
    text= text.translate(str.maketrans('','',string.punctuation))
    tokens =[word.lower() for word in word_tokenize(text) if word.lower() not in all_stop_words]
    return tokens


# In[18]:


def load_words_from_file(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as file:
        words = file.read().splitlines()
    return words


positive_words = load_words_from_file('positive-words.txt', encoding='utf-8')
negative_words = load_words_from_file('negative-words.txt', encoding='ISO-8859-1') 


# We calculate positive and negative sentiment scores for each article using
# predefined lists of positive and negative words.
# 

# In[58]:


def calculate_sentiment_scores(tokens, positive_words, negative_words):
    
    positive_score = sum(token in positive_words for token in tokens)
    negative_score = sum(token in negative_words for token in tokens)
    return positive_score, negative_score


# We assess the readability of the articles using metrics such as the Fog Index, 
# average sentence length, and the percentage of complex words.

# In[66]:


def calculate_metrics(text, positive_words, negative_words):
    blob = TextBlob(text)
    tokens = clean_and_tokenize(text)
    sentences = blob.sentences
    positive_score, negative_score = calculate_sentiment_scores(tokens, positive_words, negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(tokens) + 0.000001)
    word_count = len(tokens)
    sentence_count = len(sentences)
    avg_sentence_length = sum(len(sentence.words) for sentence in sentences) / sentence_count if sentence_count else 0
    complex_word_count = sum(1 for word in tokens if count_syllables(word) > 2)
    percentage_complex_words = (complex_word_count / word_count) * 100 if word_count else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    avg_number_of_words_per_sentence = avg_sentence_length
    syllable_per_word = sum(count_syllables(word) for word in tokens) / word_count if word_count else 0
    personal_pronouns = sum(text.lower().count(pronoun) for pronoun in ['i', 'we', 'my', 'ours', 'us'])
    avg_word_length = np.mean([len(word) for word in tokens]) if tokens else 0
    
    return {
        "POSITIVE SCORE": positive_score,
        "NEGATIVE SCORE": negative_score,
        "POLARITY SCORE": polarity_score,
        "SUBJECTIVE SCORE": subjectivity_score,
        "AVG SENTENCE LENGTH": avg_sentence_length,
        "PERCENTAGE OF COMPLEX WORD": percentage_complex_words,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_number_of_words_per_sentence,  # Added
        "COMPLEX WORD COUNT": complex_word_count,
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": syllable_per_word,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": avg_word_length,
    }
def count_syllables(word):
    import re
    word = word.lower()
    return len(re.findall('[aeiouy]+', word)) - sum(word.endswith(x) for x in ["e"])


# All calculated metrics for each article are compiled into a structured format, 
# using a pandas DataFrame for easy analysis and visualization.
# 

# Finally, we save the compiled results into an Excel file named `analysis_results.xlsx`, providing a comprehensive overview of our analysis.
# 

# In[68]:


results = []

for article in articles_list:
  
    metrics.update({"ID": article['id'], "URL": article['url']})
    metrics = calculate_metrics(article['text'], positive_words, negative_words)
    results.append(metrics)

df_results = pd.DataFrame(results)
column_order = ['ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVE SCORE', 
                'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORD', 'FOG INDEX', 
                'AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 
                'AVG WORD LENGTH']
df_results = df_results[column_order]
df_results.to_excel('Output_Result.xlsx', index=False)


# In[ ]:




