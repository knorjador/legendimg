
import re
import pandas as pd
import mlflow

from collections import Counter
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


SOURCE = '../data/psychExp.txt'
EMOTIONS = ['joy', 'fear', 'anger', 'sadness', 'disgust', 'shame', 'guilt']
DECIMALS = 4

MODELS = {
    "svc": { "class_": SVC, "name": "SVC" },
    "lsvc": { "class_": LinearSVC, "name": "LinearSVC" },
    "dt": { "class_": DecisionTreeClassifier, "name": "DecisionTreeClassifier" },
    "rf": { "class_": RandomForestClassifier, "name": "RandomForestClassifier" }
}

# HYPER_PARAMETERS = {
#     "svc": { 'C': [1, 2, 3, 5, 10, 15, 20, 30, 50, 70, 100], 'tol': [0.1, 0.01, 0.001, 0.0001, 0.00001] },
#     "lsvc": { 'C': [1, 2, 3, 5, 10, 15, 20, 30, 50, 70, 100], 'tol': [0.1, 0.01, 0.001, 0.0001, 0.00001] },
#     "dt": {'max_depth': [None, 10, 20, 30, 40, 50], 'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4]},
#     "rf": {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20, 30, 40, 50], 'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4]}
# }

HYPER_PARAMETERS = {
    "svc": { 'C': [1, 2], 'tol': [0.1, 0.01] },
    "lsvc": { 'C': [1, 2], 'tol': [0.1, 0.01] },
    "dt": {'max_depth': [10, 20], 'min_samples_split': [2, 5], 'min_samples_leaf': [1, 2]},
    "rf": {'n_estimators': [50, 100], 'max_depth': [10, 20], 'min_samples_split': [2, 5], 'min_samples_leaf': [1, 2]}
}


def read_file(file_name): 
    data_list  = []
    with open(file_name, 'r') as f: 
        for line in f: 
            line = line.strip()
            label = ' '.join(line[1:line.find(']')].strip().split())
            text = line[line.find(']')+1:].strip()
            data_list.append([label, text])
    return data_list


def ngram(token, n): 
    output = []
    for i in range(n-1, len(token)): 
        ngram = ' '.join(token[i-n+1:i+1])
        output.append(ngram) 
    return output


def create_feature(text, nrange=(1, 1)):
    text_features = [] 
    text = text.lower() 
    text_alphanum = re.sub('[^a-z0-9#]', ' ', text)
    for n in range(nrange[0], nrange[1]+1): 
        text_features += ngram(text_alphanum.split(), n)
    text_punc = re.sub('[a-z0-9]', ' ', text)
    text_features += ngram(text_punc.split(), 1)
    return Counter(text_features)


def convert_label(item, name): 
    items = list(map(float, item.split()))
    label = ''
    for idx in range(len(items)): 
        if items[idx] == 1: 
            label += name[idx] + ' '
    return label.strip()


def train_sentiment(model, hyparams):
    name = MODELS[model]['name']
    mlflow.set_experiment('legendImg')

    active_run = mlflow.active_run()
    if active_run:
        mlflow.end_run(active_run.info.status)

    X_all = []
    y_all = []
    source_txt = read_file(SOURCE)

    for label, text in source_txt:
        y_all.append(convert_label(label, EMOTIONS))
        X_all.append(create_feature(text, nrange=(1, 4)))

    X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=0.2, random_state=42)

    vectorizer = DictVectorizer(sparse = True)
    X_train = vectorizer.fit_transform(X_train)
    X_test = vectorizer.transform(X_test)

    with mlflow.start_run(run_name=name):
        grid_obj = GridSearchCV(MODELS[model]['class_'](), param_grid=hyparams, cv=2)
        grid_obj.fit(X_train, y_train)

        train_acc = accuracy_score(y_train, grid_obj.predict(X_train))
        test_acc = accuracy_score(y_test, grid_obj.predict(X_test)) 

        mlflow.log_params(grid_obj.best_params_)
        mlflow.log_metrics({
            'train_acc': train_acc,
            'test_acc': test_acc
        })
        mlflow.sklearn.log_model(grid_obj.best_estimator_, name)
        logged_model = 'runs:/{}/{}'.format(mlflow.active_run().info.run_id, name)
        mlflow.register_model(logged_model, name + '_' + pd.Timestamp.now().strftime('%Y_%m_%d_%H_%M_%S'))

    print()
    print()
    print(' > Score train: ' + str(train_acc))
    print(' > Score test: ' + str(test_acc))
    print()
    print()

    return { 'train_acc': round(train_acc, DECIMALS), 'test_acc': round(test_acc, DECIMALS) }