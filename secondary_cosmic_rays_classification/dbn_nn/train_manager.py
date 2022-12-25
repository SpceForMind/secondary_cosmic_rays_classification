import glob
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics._classification import accuracy_score
from imblearn.over_sampling import SMOTE

from tensorflow import keras

from secondary_cosmic_rays_classification.dbn_nn.dbn.tensorflow import SupervisedDBNClassification
from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset


class DBNTrainManager:
    def create_model(self,
                     hidden_layers_structure: list = [264, 264],
                     learning_rate_rbm: float = 0.05,
                     learning_rate: float = 0.1,
                     n_epochs_rbm: int = 1,
                     n_iter_backprop: int = 10,
                     batch_size: int = 32,
                     activation_function: str = 'relu',
                     dropout_p: float = 0.2
                     ):
        self.__classifier = SupervisedDBNClassification(
            hidden_layers_structure=hidden_layers_structure,
            learning_rate_rbm=learning_rate_rbm,
            learning_rate=learning_rate,
            n_epochs_rbm=n_epochs_rbm,
            n_iter_backprop=n_iter_backprop,
            batch_size=batch_size
            #activation_function=activation_function,
            #dropout_p=dropout_p
        )
        print('yes')

    def fit(self):
        self.__classifier.fit(
            self.X_train,
            self.Y_train
        )
        Y_pred = self.__classifier.predict(self.X_test)
        accuracy = accuracy_score(self.Y_test, Y_pred)
        print('Done.\nAccuracy: %f' % accuracy)

        str_accuracy = str(accuracy * 10000).split('.')[0]
        self.__classifier.save(
            save_path=f'/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/'\
                      f'dbn_nn/ckpt/{str_accuracy}'
        )

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
        Y = np.array(Y)
        # Y_categorical = keras.utils.to_categorical(
        #     Y, num_classes=3
        # )

        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(
            X,
            Y,
            test_size=0.15,
            random_state=42,
            stratify=Y
        )

        sm = SMOTE(sampling_strategy='auto', k_neighbors=5, random_state=12)
        self.X_train, self.Y_train = sm.fit_resample(self.X_train, self.Y_train)
        print(self.X_train.shape)


if __name__ == '__main__':
    dbn = DBNTrainManager()
    dbn.load_data(
        train_dir_path='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data/spacewheatherlive/'
    )
    dbn.create_model()
    dbn.fit()






