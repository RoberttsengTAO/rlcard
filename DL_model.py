import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.callbacks import EarlyStopping
from matplotlib import pyplot
from sklearn import metrics, preprocessing
from sklearn.metrics import classification_report, confusion_matrix
import keras
import pandas as pd


def build_model():
    model = Sequential()
    model.add(Dense(1024, activation='relu', input_dim=90, kernel_initializer=keras.initializers.he_normal()))
    model.add(Dense(512, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(12, activation='softmax'))
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=['accuracy'])
    model.summary()
    return model


def decoder(output):
    output_decode = []
    for i in range(len(output)):
        output_decode.append(np.argmax(output[i]))
    return np.array(output_decode).reshape(len(output), 1)


if __name__ == '__main__':
    input_list = np.loadtxt('/Users/alex.chen/PycharmProjects/holdem_game/input_list_all')
    output_list = np.loadtxt('/Users/alex.chen/PycharmProjects/holdem_game/output_list_all')
    X_train, X_test, Y_train, Y_test = train_test_split(input_list, output_list, test_size=0.2, random_state=0)
    X_real_train, X_val, Y_real_train, Y_val = train_test_split(X_train, Y_train, test_size=0.2, random_state=0)

    model = build_model()
    callback = EarlyStopping(monitor="val_loss", patience=10, verbose=1, mode="auto")
    history = model.fit(X_real_train, Y_real_train, epochs=100, batch_size=32, validation_data=(X_val, Y_val), callbacks=[callback])
    model.save('prediction_model.h5')

    # plot loss during training
    pyplot.subplot(211)
    pyplot.title('Loss')
    pyplot.plot(history.history['loss'], label='train')
    pyplot.plot(history.history['val_loss'], label='val')
    pyplot.legend()
    # plot accuracy during training
    pyplot.subplot(212)
    pyplot.title('Accuracy')
    pyplot.plot(history.history['acc'], label='train')
    pyplot.plot(history.history['val_acc'], label='val')
    pyplot.legend()
    pyplot.show()

    Y_prediction = model.predict(X_test)
    real_action = decoder(Y_test)
    predictive_action = decoder(Y_prediction)

    accuracy = metrics.accuracy_score(real_action, predictive_action)

    target_names = ["check", "fold", "all-in", "raise-1", "raise-2", "raise-3", "raise-4",
                    "raise-10", "raise-20", "raise-50", "raise-100", "raise-200"]
    print(classification_report(real_action, predictive_action, target_names=target_names))

    cnf_matrix = confusion_matrix(real_action, predictive_action)
    df_cm = pd.DataFrame(cnf_matrix, index = target_names, columns = target_names)