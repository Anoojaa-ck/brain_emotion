# ===================== Core Libraries =====================
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===================== TensorFlow / Keras =====================
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import (
    Dense,
    Flatten,
    GRU,
    Dropout,
    BatchNormalization,
    Input,
    Conv1D,
    Conv2D,
    MaxPooling1D,
    MaxPooling2D,
    Add,
    Reshape
)
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam

# ===================== Scikit-learn =====================
from sklearn.model_selection import (
    train_test_split,
    KFold,
    StratifiedKFold,
    cross_val_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score
)
from sklearn.decomposition import PCA
from sklearn import metrics

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# ===================== Signal Processing =====================
from scipy.io import loadmat
from scipy import signal
from scipy.stats import entropy
from scipy.fft import fft, ifft
from pywt import wavedec
from functools import reduce
import scipy

data = pd.read_csv("emotions.csv")
data.head()

sample = data.loc[0, 'fft_0_b':'fft_749_b']

plt.style.use('dark_background')
plt.figure(figsize=(15, 10))
plt.plot(range(len(sample)), sample)
plt.title("Features fft_0_b through fft_749_b", weight='bold', color='red')
plt.show()

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
data['label'] = le.fit_transform(data['label'])

y = data.pop('label')
X = data
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=48)
X_train = np.array(X_train).reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = np.array(X_test).reshape((X_test.shape[0], X_test.shape[1], 1))
y_train = pd.get_dummies(y_train)
y_test = pd.get_dummies(y_test)

from keras.layers import Flatten
from keras.layers import Dense

inputs = tf.keras.Input(shape=(X_train.shape[1], 1))
gru = tf.keras.layers.GRU(64, return_sequences=True)(inputs)
flat = Flatten()(gru)
outputs = Dense(3, activation='softmax')(flat)
model = tf.keras.Model(inputs, outputs)
model.summary()


def train_model(model, x_train, y_train, x_test, y_test, save_to, epoch=2):
    opt_adam = keras.optimizers.Adam(learning_rate=0.001)

    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=10)
    mc = ModelCheckpoint(save_to + '_best_model.h5', monitor='val_accuracy', mode='max', verbose=1, save_best_only=True)
    lr_schedule = tf.keras.callbacks.LearningRateScheduler(lambda epoch: 0.001 * np.exp(-epoch / 10.))

    model.compile(optimizer=opt_adam,
                  loss=['categorical_crossentropy'],
                  metrics=['accuracy'])

    history = model.fit(x_train, y_train,
                        batch_size=4,
                        epochs=epoch,
                        validation_data=(x_test, y_test),
                        callbacks=[es, mc, lr_schedule])

    saved_model = load_model(save_to + '_best_model.h5')

    return model, history


model, history = train_model(model, X_train, y_train, X_test, y_test, save_to='./', epoch=50)  #

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

model_acc = model.evaluate(X_test, y_test, verbose=0)[1]
print("Test Accuracy: {:.3f}%".format(model_acc * 100))

y_pred = np.array(list(map(lambda x: np.argmax(x), model.predict(X_test))))
y_test = y_test.idxmax(axis=1)

cm = confusion_matrix(y_test, y_pred)
clr = classification_report(y_test, y_pred)

plt.figure(figsize=(8, 8))
sns.heatmap(cm, annot=True, vmin=0, fmt='g', cbar=False, cmap='Blues')
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

