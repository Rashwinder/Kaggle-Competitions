# -*- coding: utf-8 -*-
"""Space Titanic.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/140kRIsdEHoegGl9fbR8Jt_Fas7_n4lEr

# Libraries.
"""

# Essentials.
import pandas as pd
import numpy as np
from collections import Counter

# Visualisations.
import seaborn as sns
import matplotlib.pyplot as plt

# Metrics.
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, KFold, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, mean_squared_error, f1_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler

# Commented out IPython magic to ensure Python compatibility.
# Mounting Google Drive onto Colab.
from google.colab import drive
drive.mount('/gdrive')
# %cd /gdrive

# Reproducibility.
import random
random.seed(1234)

train = pd.read_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/train.csv')
test = pd.read_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/test.csv')
test_passenger_id = test[['PassengerId']]

train.shape, test.shape

train.isnull().sum()

test.isnull().sum()

"""Because the test data has some missing values, it is best to join them and treat them as one data set.

# Data Exploration.
"""

train.sample(5)

train.describe()

sns.countplot(x = train['Age'])

"""## CryoSleep
The visualisation suggests that passengers who were in cryosleep had priority over those who were not in cryosleep when it came to being transported.
"""

sns.countplot(x = train['CryoSleep'], hue = train['Transported'])

"""## HomePlanet
The first visualisation suggests that most of the passengers who were transported came from Earth. This is further supported after including the CryoSleep variable as it shows most of the passengers who were not in cryosleep but were transported came from Earth.
"""

sns.countplot(x = train['HomePlanet'], hue = train['Transported'])

g = sns.FacetGrid(train, col = 'CryoSleep', sharex = False, sharey = False)
g.map_dataframe(sns.histplot, 'HomePlanet', hue = 'Transported', stat = 'percent', multiple = 'dodge')

"""## Destination
The visualisation suggests that passengers who were heading to TRAPPIST were the most likely to be transported.
"""

sns.countplot(x = train['Destination'], hue = train['Transported'])

"""## VIP
It's pretty evident that being a VIP did not give one priority over others when it came to being transported.
"""

sns.countplot(x = train['VIP'], hue = train['Transported'])

"""## Transported
The label count is relatively even across the board.
"""

sns.countplot(x = train['Transported'])

train['TotalSpending'] = train['RoomService'] + train['FoodCourt'] + train['ShoppingMall'] + train['Spa'] + train['VRDeck']
test['TotalSpending'] = test['RoomService'] + test['FoodCourt'] + test['ShoppingMall'] + test['Spa'] + test['VRDeck']

plt.rcParams['figure.figsize'] = [15, 7.5]
fig, ax = plt.subplots(2, 3)

sns.kdeplot(x = train['RoomService'], ax = ax[0, 0])
sns.kdeplot(x = test['RoomService'], ax = ax[0, 0])
ax[0, 0].set_title('RoomService')
ax[0, 0].set_xlabel('')
ax[0, 0].set_ylabel('')


sns.kdeplot(x = train['FoodCourt'], ax = ax[0, 1])
sns.kdeplot(x = test['FoodCourt'], ax = ax[0, 1])
ax[0, 1].set_title('FoodCourt')
ax[0, 1].set_xlabel('')
ax[0, 1].set_ylabel('')

sns.kdeplot(x = train['ShoppingMall'], ax = ax[0, 2])
sns.kdeplot(x = test['ShoppingMall'], ax = ax[0, 2])
ax[0, 2].set_title('ShoppingMall')
ax[0, 2].set_xlabel('')
ax[0, 2].set_ylabel('')

sns.kdeplot(x = train['Spa'], ax = ax[1, 0])
sns.kdeplot(x = test['Spa'], ax =  ax[1, 0])
ax[1, 0].set_title('Spa')
ax[1, 0].set_xlabel('')
ax[1, 0].set_ylabel('')

sns.kdeplot(x = train['VRDeck'], ax = ax[1, 1])
sns.kdeplot(x = test['VRDeck'], ax = ax[1, 1])
ax[1, 1].set_title('VRDeck')
ax[1, 1].set_xlabel('')
ax[1, 1].set_ylabel('')

sns.kdeplot(x = train['TotalSpending'], ax = ax[1, 2])
sns.kdeplot(x = test['TotalSpending'], ax = ax[1, 2])
ax[1, 2].set_title('TotalSpending')
ax[1, 2].set_xlabel('')
ax[1, 2].set_ylabel('')

fig.tight_layout()
plt.show()

"""# Preprocessing.

## Cabin
"""

train['Cabin'] = train['Cabin'].fillna(train['Cabin'].mode()[0])
test['Cabin'] = test['Cabin'].fillna(test['Cabin'].mode()[0])

train[['Deck', 'Num', 'Side']] = train['Cabin'].str.split('/', expand = True)
test[['Deck', 'Num', 'Side']] = test['Cabin'].str.split('/', expand = True)

train['Num'] = train['Num'].astype('int64')
test['Num'] = test['Num'].astype('int64')

"""## Missing Values Imputation.

### Numerical.
"""

numerical_features = [col for col in train.columns if train[col].dtype in ['int64', 'float64']]
numerical_transformer = Pipeline(steps = [
    ('imputer', SimpleImputer(strategy = 'median')),
    ('scaler', StandardScaler()),
])

preprocessor = ColumnTransformer(transformers = [
    ('num_transform', numerical_transformer, numerical_features)
])

pipeline = Pipeline(steps = [
    ('preprocessor', preprocessor)
])
pipeline

train[numerical_features] = pd.DataFrame(pipeline.fit_transform(train[numerical_features]),
                                         index = train[numerical_features].index, 
                                         columns = train[numerical_features].columns)

test[numerical_features] = pd.DataFrame(pipeline.fit_transform(test[numerical_features]),
                                        index = test[numerical_features].index,
                                        columns = test[numerical_features].columns)

"""### Categorical"""

cat = ['HomePlanet', 'Destination', 'CryoSleep', 'VIP']

for col in cat:
  train[col] = train[col].fillna(train[col].mode()[0])
  test[col] = test[col].fillna(test[col].mode()[0])

train.drop(['PassengerId', 'VIP', 'Name', 'Cabin'], axis = 1, inplace = True)
test.drop(['PassengerId', 'VIP', 'Name', 'Cabin'], axis = 1, inplace = True)

train.isnull().sum()

test.isnull().sum()

"""# Label Encoding."""

train['CryoSleep'] = [1 if w == True else 0 for w in train['CryoSleep']]

test['CryoSleep'] = [1 if w == True else 0 for w in test['CryoSleep']]

train['Transported'] = [1 if label == True else 0 for label in train['Transported']]

cols = ['HomePlanet', 'Destination', 'Deck', 'Side']
dummied_train = pd.get_dummies(train, columns = cols, drop_first = True)
dummied_test = pd.get_dummies(test, columns = cols, drop_first = True)

dummied_train.sample()

dummied_test.sample()

train_X, test_X, train_y, test_y = train_test_split(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'], test_size = 0.1)

train_X, val_X, train_y, val_y = train_test_split(train_X, train_y, test_size = 0.2)

train_X.shape, val_X.shape, test_X.shape, train_y.shape, val_y.shape, test_y.shape

"""# Model Building and Evaluation."""

Model = {}

"""## Random Forest"""

from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier()
rf.fit(train_X, train_y)
val_pred = rf.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = rf.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['rf'] = {}
Model['rf']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['rf']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

rf.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""### Feature Importance"""

plt.barh(train_X.columns, rf.feature_importances_)

"""## Bagging"""

from sklearn.ensemble import BaggingClassifier

bag = BaggingClassifier()
bag.fit(train_X, train_y)
val_pred = bag.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = bag.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['bag'] = {}
Model['bag']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['bag']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

bag.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""### Feature Importance"""

feature_importances = np.mean([
    tree.feature_importances_ for tree in bag.estimators_
], axis=0)

plt.barh(train_X.columns, feature_importances)

"""## Logistic Regression"""

from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(max_iter = 10000, penalty = 'l2')
lr.fit(train_X, train_y)
val_pred = lr.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = lr.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['lr'] = {}
Model['lr']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['lr']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

lr.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""## Support Vector"""

from sklearn.svm import SVC

svc = SVC()
svc.fit(train_X, train_y)
val_pred = svc.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = svc.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['svc'] = {}
Model['svc']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['svc']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

svc.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""## Multi Layer Perceptron"""

from sklearn.neural_network import MLPClassifier

mlp = MLPClassifier(max_iter = 10000)
mlp.fit(train_X, train_y)
val_pred = mlp.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = mlp.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['mlp'] = {}
Model['mlp']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['mlp']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

mlp.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""## KNeighbours"""

from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier()
knn.fit(train_X, train_y)
val_pred = knn.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = knn.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['knn'] = {}
Model['knn']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['knn']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

knn.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""## Extreme Gradient Boosting"""

from xgboost import XGBClassifier

xgb = XGBClassifier()
xgb.fit(train_X, train_y)
val_pred = xgb.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = xgb.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['xgb'] = {}
Model['xgb']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['xgb']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

xgb.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""### Feature Importance"""

plt.barh(train_X.columns, xgb.feature_importances_)

"""## Naive Bayes"""

from sklearn.naive_bayes import GaussianNB

nb = GaussianNB()
nb.fit(train_X, train_y)
val_pred = nb.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = nb.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['nb'] = {}
Model['nb']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['nb']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

nb.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""## Gradient Boosting"""

from sklearn.ensemble import GradientBoostingClassifier

gb = GradientBoostingClassifier()
gb.fit(train_X, train_y)
val_pred = gb.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = gb.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['gb'] = {}
Model['gb']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['gb']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

gb.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

"""### Feature Importance"""

plt.barh(train_X.columns, gb.feature_importances_)

Model

"""# Results"""

params = {
    'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)],
    'solver': ['adam'],
    'alpha': [0.0001, 0.05],
    'learning_rate': ['constant','adaptive'],
    'max_iter': [200, 400, 600, 800, 1000]
}

grid = GridSearchCV(MLPClassifier(), params, cv = 5, n_jobs = -1)
grid.fit(train_X, train_y)

grid.best_score_, grid.best_estimator_

from sklearn.neural_network import MLPClassifier

mlp2 = MLPClassifier(alpha=0.05, learning_rate='adaptive', max_iter=800)

mlp2.fit(train_X, train_y)
val_pred = mlp2.predict(val_X)
print('F1 score on the validation set is {}'.format(f1_score(y_true = val_y, y_pred = val_pred)))

test_pred = mlp2.predict(test_X)
print('F1 score on the Test set is {}'.format(f1_score(y_true = test_y, y_pred = test_pred)))

Model['mlp2'] = {}
Model['mlp2']['Validation'] = round(f1_score(y_true = val_y, y_pred = val_pred), 4)
Model['mlp2']['Test'] = round(f1_score(y_true = test_y, y_pred = test_pred), 4)

mlp2.fit(dummied_train.drop(['Transported'], axis = 1), dummied_train['Transported'])

Model

"""## Keras"""

import tensorflow as tf
import keras
from keras import Sequential
from keras.layers import Dense, Dropout, BatchNormalization, Input
from keras.callbacks import EarlyStopping

model = Sequential()

model.add(Input(train_X.shape[1]))

model.add(Dense(128, activation = 'relu'))
model.add(Dropout(0.15))
model.add(BatchNormalization())

model.add(Dense(128, activation = 'relu'))
model.add(BatchNormalization())
model.add(Dropout(0.15))

model.add(Dense(128, activation = 'relu'))
model.add(BatchNormalization())

model.add(Dense(64, activation = 'relu'))
model.add(BatchNormalization())

model.add(Dense(32, activation = 'relu'))
model.add(BatchNormalization())

model.add(Dense(1, activation = 'sigmoid'))

model.compile(optimizer = 'RMSProp', loss = 'binary_crossentropy', metrics = ['accuracy'])

early_stop = EarlyStopping(monitor = 'val_loss',
                           patience = 10)

history = model.fit(train_X, train_y, validation_data = [val_X, val_y], 
                    epochs = 100, batch_size = 64,
                    verbose = 1,
                    callbacks = [early_stop])

keras_pred = model.predict(val_X)
keras_pred = [True if p >= 0.5 else False for p in keras_pred]
f1_score(y_true = val_y, y_pred = keras_pred)

"""# Predictions.

## Random Forest
"""

# Support Vector Classifier
RF = rf.predict(dummied_test)
RF = ['True' if p == 1 else 'False' for p in RF]
Counter(RF)

test_passenger_id['Transported'] = RF
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/RF_submission.csv', index = False)

"""## Bagging"""

# Support Vector Classifier
BAG = bag.predict(dummied_test)
BAG = ['True' if p == 1 else 'False' for p in BAG]
Counter(BAG)

test_passenger_id['Transported'] = BAG
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/BAG_submission.csv', index = False)

"""## Logistic Regression"""

# Support Vector Classifier
LR = lr.predict(dummied_test)
LR = ['True' if p == 1 else 'False' for p in LR]
Counter(LR)

test_passenger_id['Transported'] = LR
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/LR_submission.csv', index = False)

"""## Support Vector Classifier"""

# Support Vector Classifier
SVC = svc.predict(dummied_test)
SVC = ['True' if p == 1 else 'False' for p in SVC]
Counter(SVC)

test_passenger_id['Transported'] = SVC
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/SVC_submission.csv', index = False)

"""## Multi Layer Perceptron"""

# Support Vector Classifier
MLP = mlp.predict(dummied_test)
MLP = ['True' if p == 1 else 'False' for p in MLP]
Counter(MLP)

test_passenger_id['Transported'] = MLP
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/MLP_submission.csv', index = False)

"""## KNeighbours"""

# KNeighbours
KNN = knn.predict(dummied_test)
KNN = ['True' if p == 1 else 'False' for p in KNN]
Counter(KNN)

test_passenger_id['Transported'] = KNN
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/KNN_submission.csv', index = False)

"""## Extreme Gradient Boosting"""

# Extreme Gradient Boosting
XGB = xgb.predict(dummied_test)
XGB = ['True' if p == 1 else 'False' for p in XGB]
Counter(XGB)

test_passenger_id['Transported'] = XGB
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/XGB_submission.csv', index = False)

"""## Naive Bayes"""

# Naive Bayes
NB = nb.predict(dummied_test)
NB = ['True' if p == 1 else 'False' for p in NB]
Counter(NB)

test_passenger_id['Transported'] = NB
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/NB_submission.csv', index = False)

"""## Gradient Boosting"""

# Gradient Boosting
GB = gb.predict(dummied_test)
GB = ['True' if p == 1 else 'False' for p in GB]
Counter(GB)

test_passenger_id['Transported'] = XGB
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/XGB_submission.csv', index = False)

# Gradient Boosting
KER = model.predict(dummied_test)
KER = ['True' if p >= 0.5 else 'False' for p in KER]
Counter(KER)

test_passenger_id['Transported'] = KER
test_passenger_id.to_csv('/gdrive/MyDrive/Kaggle Competitions/Spaceship Titanic/KER_submission.csv', index = False)