import glob
import os

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics._classification import accuracy_score
from imblearn.over_sampling import SMOTE

import tensorflow as tf
from tensorflow import keras

from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset


class CNNTrainManager:
    def create_model(self):
        self.__model = keras.models.Sequential([
            keras.layers.TimeDistributed(
                keras.layers.Conv1D(
                    filters=256,
                    kernel_size=3,
                    activation='relu'
                ),
                input_shape=(12, 12, 10),  # 24 * 60 -> 1440 ---> 24 * 6 * 10
            ),
            keras.layers.TimeDistributed(
                keras.layers.Conv1D(
                    filters=128,
                    kernel_size=3,
                    activation='relu')
            ),
            keras.layers.TimeDistributed(
                keras.layers.Conv1D(
                    filters=64,
                    kernel_size=3,
                    activation='relu')
            ),
            keras.layers.TimeDistributed(
                keras.layers.Dropout(0.5)
            ),
            keras.layers.TimeDistributed(
                keras.layers.MaxPooling1D(pool_size=2)
            ),
            keras.layers.TimeDistributed(keras.layers.Flatten()),
            keras.layers.LSTM(64),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(3, activation='sigmoid')
        ])
        self.__model.compile(
            loss='categorical_crossentropy',
            optimizer='adam',
            metrics=['accuracy']
        )
        self.__model.summary(line_length=100)

    def fit(self,
            epochs: int = 50):
        self.__model.fit(
            x=self.X_train,
            y=self.Y_train,
            epochs=epochs,
            batch_size=32,
            shuffle=True
        )

    def test(self):
        self.__metric = self.__model.evaluate(
            x=self.X_test,
            y=self.Y_test
        )
        self.__acc = self.__metric[1]

    def save(self,
             ckpt_dir_path: str):
        metric_str = str(self.__acc * 10000).split('.')[0]
        path = os.path.join(ckpt_dir_path, f'{metric_str}_ckpt.h5')
        print(path)
        self.__model.save(filepath=path)

    def load_data(self,
                  train_dir_path: str):
        data_paths = glob.glob(f'{train_dir_path}*')
        print(data_paths)
        class_names = [path.split('/')[-1] for path in data_paths]
        class_names_dict = {
            class_name: i
            for i, class_name in zip(range(len(class_names)), class_names)
        }

        X = []
        Y = []

        for data_path in data_paths:
            dataset = DateAndPressureDataset()
            dataset.read_all_datasets_from_dir(
                dir_path=data_path,
                batched=True
            )
            pressures_batched_list = dataset.get_batched_pressures_list(
                scaling=True
            )
            class_name = data_path.split('/')[-1]
            label = class_names_dict[class_name]

            print(data_path)

            for pressures_batch in pressures_batched_list:
                X.append(np.array(pressures_batch))
                Y.append(label)

        X = np.array(X)
        print(X.shape)
        Y = np.array(Y)
        Y_categorical = keras.utils.to_categorical(
            Y, num_classes=3
        )

        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(
            X,
            Y_categorical,
            test_size=0.2,
            random_state=42,
            stratify=Y_categorical
        )

        # sm = SMOTE(sampling_strategy='auto', k_neighbors=20, random_state=12)
        # self.X_train, self.Y_train = sm.fit_resample(self.X_train, self.Y_train)

        self.X_train = self.X_train.reshape((-1, 12, 12, 10))
        self.X_test = self.X_test.reshape((-1, 12, 12, 10))


if __name__ == '__main__':
    classifier = CNNTrainManager()

    classifier.load_data(
        train_dir_path='/home/user/projects/rays/secondary_cosmic_rays_classification/data/all_days/'
    )
    classifier.create_model()
    classifier.fit(
        epochs=10
    )
    classifier.test()
    classifier.save(
        ckpt_dir_path='/home/user/projects/rays/secondary_cosmic_rays_classification/cnn_nn/ckpt'
    )
