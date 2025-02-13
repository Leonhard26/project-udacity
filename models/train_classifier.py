import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import sys
import random

from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

import pickle

from sklearn.metrics import classification_report, accuracy_score

import nltk
import re
from nltk.tokenize import word_tokenize, WhitespaceTokenizer
from nltk.stem import WordNetLemmatizer

import random
from sklearn.model_selection import train_test_split

from sklearn.externals import joblib


def load_data(database_filepath):
    print(database_filepath)
    table_name = 'df'
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_table(table_name,engine)
    X = df['message']
    y = df.iloc[:,5:]
    category_names = y.columns
    return X,y,category_names
    
def tokenize(text):
    token_list = WhitespaceTokenizer().tokenize(text)
    lemmatizer = WordNetLemmatizer()
    
    final_tokens = []
    for i in token_list:
        i = lemmatizer.lemmatize(i).lower().strip('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
        i = re.sub(r'\[[^.,;:]]*\]', '', i)
        
        if i != '':
            final_tokens.append(i)
        
    return final_tokens

def build_model():
    pipeline = Pipeline([('vect', CountVectorizer(tokenizer=tokenize)),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultiOutputClassifier(RandomForestClassifier()))])
    return pipeline

def evaluate_model(model, X_test, Y_test, category_names):
    y_pred = model.predict(X_test)
    print(classification_report(Y_test.iloc[:,1:].values, np.array([x[1:] for x in y_pred]), target_names=category_names))

def save_model(model, model_filepath):
    joblib.dump(model, model_filepath)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names =load_data(database_filepath)
        #X, Y, category_names = load_data('sqlite:///' + database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()