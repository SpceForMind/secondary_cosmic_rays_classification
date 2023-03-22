import glob
import os

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics._classification import accuracy_score
from imblearn.over_sampling import SMOTE

import tensorflow as tf
from tensorflow import keras

from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset


class AutoencTrainManager:
    def create_model(self):
        # Размерность кодированного представления
        encoding_dim = 64

        # Deep AutoEnc
        # # Энкодер
        # # Входной плейсхолдер
        # input_img = keras.layers.Input(
        #     shape=(6, 6, 5, 2, 2, 2))
        # # Вспомогательный слой решейпинга
        # flat_img = keras.layers.Flatten()(input_img)
        # x = keras.layers.Dense(encoding_dim * 8, activation='relu')(flat_img)
        # x = keras.layers.Dense(encoding_dim * 4, activation='relu')(x)
        # x = keras.layers.Dense(encoding_dim * 2, activation='relu')(x)
        # encoded = keras.layers.Dense(encoding_dim, activation='linear')(x)
        #
        #
        # # Декодер
        # # Раскодированное другим полносвязным слоем изображение
        # input_encoded = keras.layers.Input(shape=(encoding_dim,))
        # x = keras.layers.Dense(encoding_dim * 2, activation='relu')(input_encoded)
        # x = keras.layers.Dense(encoding_dim * 4, activation='relu')(x)
        # x = keras.layers.Dense(encoding_dim * 8, activation='relu')(x)
        # flat_decoded = keras.layers.Dense(1440, activation='sigmoid')(x)
        # decoded = keras.layers.Reshape((6, 6, 5, 2, 2, 2))(flat_decoded)


        # CNN AutoEnc
        # input_img = keras.layers.Input(
        #          shape=(36, 40))
        #
        # x = keras.layers.Conv1D(128, kernel_size=7, activation='relu', padding='same')(input_img)
        # x1 = keras.layers.MaxPooling1D(padding='same')(x)
        # x2 = keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(x1)
        # x3 = keras.layers.MaxPooling1D(padding='same')(x2)
        # encoded = keras.layers.Conv1D(40, kernel_size=7, activation='relu', padding='same')(x3)
        #
        # input_encoded = keras.layers.Input(shape=(9, 40))
        # x = keras.layers.Conv1D(64, kernel_size=7, activation='relu', padding='same')(input_encoded)
        # x = keras.layers.UpSampling1D()(x)
        # x = keras.layers.Conv1D(128, kernel_size=2, activation='relu', padding='same')(x)
        # x = keras.layers.UpSampling1D()(x)
        # decoded = keras.layers.Conv1D(40, kernel_size=7, activation='sigmoid', padding='same')(x)

        encoding_dim = 16
        lambda_l1 = 0.00001

        # Энкодер
        input_img = keras.layers.Input(shape=(12, 12, 10))
        flat_img = keras.layers.Flatten()(input_img)
        x = keras.layers.Dense(encoding_dim * 3, activation='relu')(flat_img)
        x = keras.layers.Dense(encoding_dim * 2, activation='relu')(x)
        encoded = keras.layers.Dense(encoding_dim, activation='linear',
                                     activity_regularizer=keras.regularizers.L1L2(lambda_l1))(x)

        # Декодер
        input_encoded = keras.layers.Input(shape=(encoding_dim,))
        x = keras.layers.Dense(encoding_dim * 2, activation='relu')(input_encoded)
        x = keras.layers.Dense(encoding_dim * 3, activation='relu')(x)
        flat_decoded = keras.layers.Dense(1440, activation='sigmoid')(x)
        decoded = keras.layers.Reshape((12, 12, 10))(flat_decoded)

        # Модели, в конструктор первым аргументом передаются входные слои, а вторым выходные слои
        # Другие модели можно так же использовать как и слои
        self.__encoder = keras.models.Model(input_img, encoded, name="encoder")
        self.__decoder = keras.models.Model(input_encoded, decoded, name="decoder")
        self.__autoencoder = keras.models.Model(input_img, self.__decoder(self.__encoder(input_img)),
                                                name="autoencoder")

        self.__autoencoder.compile(
            loss='binary_crossentropy',
            optimizer='adam',
            # metrics=['val_loss']
        )
        self.__autoencoder.summary(line_length=100)

    def fit(self,
            epochs: int = 50,
            batch_size: int = 32):
        self.__autoencoder.fit(
            x=self.X_train,
            y=self.X_train,
            epochs=epochs,
            shuffle=True,
            batch_size=32,
            validation_data=(self.X_test, self.X_test)
        )

    def test(self):
        self.__metric = self.__autoencoder.evaluate(
            x=self.X_test,
            y=self.Y_test
        )
        self.__acc = self.__metric[1]

    def save(self,
             ckpt_dir_path: str):
        metric_str = str(self.__acc * 10000).split('.')[0]
        path = os.path.join(ckpt_dir_path, f'{metric_str}_ckpt.h5')
        print(path)
        self.__autoencoder.save(filepath=path)

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
    classifier = AutoencTrainManager()

    classifier.create_model()
    classifier.load_data(
        train_dir_path='/home/user/projects/rays/secondary_cosmic_rays_classification/data/all_days/'
    )
    classifier.fit(
        epochs=50
    )
    # classifier.test()
    # classifier.save(
    #     ckpt_dir_path='/home/user/projects/rays/secondary_cosmic_rays_classification/cnn_nn/ckpt'
    # )
