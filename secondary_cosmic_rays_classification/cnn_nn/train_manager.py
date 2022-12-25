import glob
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
                    filters=64,
                    kernel_size=3,
                    activation='relu'
                ),
                input_shape=(24, 6, 10), # 24 * 60 -> 1440 ---> 24 * 6 * 10
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
            keras.layers.LSTM(100),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(100, activation='relu'),
            keras.layers.Dense(3, activation='sigmoid')
        ])
        self.__model.compile(
            loss='categorical_crossentropy',
            optimizer='adam'
        )
        self.__model.summary(line_length=100)

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
        X = X.reshape((24, 6, 10))
        Y = np.array(Y)
        Y_categorical = keras.utils.to_categorical(
            Y, num_classes=3
        )

        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(
            X,
            Y_categorical,
            test_size=0.15,
            random_state=42,
            stratify=Y_categorical
        )

        sm = SMOTE(sampling_strategy='auto', k_neighbors=5, random_state=12)
        self.X_train, self.Y_train = sm.fit_resample(self.X_train, self.Y_train)
        print(self.X_train.shape)


if __name__ == '__main__':
    CNNTrainManager().load_data()

