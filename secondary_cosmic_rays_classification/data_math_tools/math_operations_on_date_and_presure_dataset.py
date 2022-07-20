import os
import math

from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset


class MathOperationsOnDateAndPresureDataset:
    @staticmethod
    def compute_dataset_expected_value(dataset_path: str):
        dataset = DateAndPressureDataset()
        dataset.read(path=dataset_path)
        presures_list = dataset.get_presures_list()

        return sum(presures_list) / len(presures_list)

    @staticmethod
    def compute_datasets_expected_value(datasets_dir_path: str):
        expected_values_list = []

        for dataset_name in os.listdir(datasets_dir_path):
            dataset_path = os.path.join(datasets_dir_path, dataset_name)
            expected_value = MathOperationsOnDateAndPresureDataset.compute_dataset_expected_value(
                dataset_path=dataset_path
            )
            expected_values_list.append(expected_value)

        print('E([{}]) ='.format(datasets_dir_path), sum(expected_values_list) / len(expected_values_list))

        return sum(expected_values_list) / len(expected_values_list)

    @staticmethod
    def compute_dataset_dispersion(dataset_path: str):
        expected_value = MathOperationsOnDateAndPresureDataset.compute_dataset_expected_value(
            dataset_path=dataset_path
        )
        dataset = DateAndPressureDataset()
        dataset.read(path=dataset_path)
        presures_list = dataset.get_presures_list()

        return sum([(expected_value - presure) ** 2 for presure in presures_list]) / len(presures_list)

    @staticmethod
    def compute_datasets_dispersion(datasets_dir_path: str):
        dispersions_list = []

        for dataset_name in os.listdir(datasets_dir_path):
            dataset_path = os.path.join(datasets_dir_path, dataset_name)
            dispersion = MathOperationsOnDateAndPresureDataset.compute_dataset_dispersion(
                dataset_path=dataset_path
            )
            dispersions_list.append(dispersion)

        print('D([{}]) ='.format(datasets_dir_path), sum(dispersions_list) / len(dispersions_list))

        return sum(dispersions_list) / len(dispersions_list)

    @staticmethod
    def compute_dataset_standard_deviation(dataset_path: str):
        print('St_Dev([{}]) ='.format(dataset_path),
              math.sqrt(MathOperationsOnDateAndPresureDataset.compute_dataset_dispersion(
                  dataset_path=dataset_path
        )))

        return math.sqrt(MathOperationsOnDateAndPresureDataset.compute_dataset_dispersion(
            dataset_path=dataset_path
        ))

    @staticmethod
    def compute_datasets_standard_deviation(datasets_dir_path: str):
        print('St_Dev([{}]) ='.format(datasets_dir_path),
              math.sqrt(MathOperationsOnDateAndPresureDataset.compute_datasets_dispersion(
                  datasets_dir_path=datasets_dir_path
        )))

        return math.sqrt(MathOperationsOnDateAndPresureDataset.compute_datasets_dispersion(
            datasets_dir_path=datasets_dir_path
        ))

