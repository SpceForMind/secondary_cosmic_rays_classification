import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Tuple, Any

from secondary_cosmic_rays_classification.data_loader.data_string_content_info import DataStringContentInfo


class DateAndPressureDataset:
    date_info__header = 'DateInfo'
    pressure__header = 'Pressure'
    data__sepparator = DataStringContentInfo.between_date_info_and_pressure__sepparator
    date__sepparator = DataStringContentInfo.year_month_day__sepparator

    def __init__(self):
        self.clear_and_set_headder()

    def plot(self,
             save_path: str):
        datetimes_list = self.get_datetimes_list()
        presures_list = self.get_presures_list()

        fig, ax = plt.subplots()
        plt.rcParams["figure.figsize"] = [18.5, 10.5]
        plt.rcParams["figure.autolayout"] = True
        fig.set_dpi(100)
        ax.plot(datetimes_list, presures_list)

        # Format your axis as required
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H"))
        _ = plt.xticks(rotation=90)

        print('Saving plot: [{}]...'.format(save_path))
        plt.savefig(save_path)

    def load_from_prepared_data(self,
                                prepared_data_list: list):
        self.__dataset += prepared_data_list

    def get_dataset_as_datetimes_and_presures_list(self) -> List[Tuple[datetime, float]]:
        presures_list = self.get_presures_list()
        datetimes_list = self.get_datetimes_list()
        datetimes_and_presures_list = [(date, presure)
                                       for date, presure in zip(datetimes_list, presures_list)]

        return datetimes_and_presures_list

    def get_presures_list(self) -> List[float]:
        presures_list = []

        for line in self.__dataset[1 : ]:
            presures_list.append(
                float(line.split(DateAndPressureDataset.data__sepparator)[1])
            )

        return presures_list

    def get_datetimes_list(self) -> List[datetime]:
        datetimes_list = []

        for line in self.__dataset[1:]:
            date_str = line.split(DateAndPressureDataset.data__sepparator)[0]
            yr, mth, day, hour, min, sec = date_str.split(DateAndPressureDataset.date__sepparator)
            date_datetime = datetime(
                year=int(yr),
                month=int(mth),
                day=int(day),
                hour=int(hour),
                minute=int(min),
                second=int(sec)
            )
            datetimes_list.append(date_datetime)

        return datetimes_list

    def get_dataset(self,
                    without_headder: bool = False) -> List[str]:
        if without_headder:
            return self.__dataset[1: ]

        return self.__dataset

    def read(self,
             path: str):
        with open(path, 'r') as f:
            print('Reading Dataset: [{}]...'.format(path))
            self.__dataset = [line.strip('\n') for line in f.readlines()]

    def read_all_datasets_from_dir(self,
                                   dir_path: str):
        self.clear_and_set_headder()

        for dataset_name in os.listdir(dir_path):
            path = os.path.join(dir_path, dataset_name)

            with open(path, 'r') as f:
                data = [line.strip('\n') for line in f.readlines()[1 : ]]
                self.__dataset += data

    def save(self,
             path: str):
        with open(path, 'w') as f:
            print('Saving dataset: [{}]...'.format(path))
            f.write('\n'.join(self.__dataset))

    def clear_and_set_headder(self):
        self.__dataset = [
            f'{DateAndPressureDataset.date_info__header}'
            f'{DateAndPressureDataset.data__sepparator}'
            f'{DateAndPressureDataset.pressure__header}'
        ]

    def generate_dataset_from_presure_list_and_datetime_list(self,
                                                             presure_list: List[float],
                                                             datetime_list: List[datetime],
                                                             path_to_save: str = None):
        self.clear_and_set_headder()

        for date, presure in zip(datetime_list, presure_list):
            date_str = f'{DateAndPressureDataset.date__sepparator}'.join([
                str(date.year),
                str(date.month),
                str(date.day),
                str(date.hour),
                str(date.minute),
                str(date.second)
            ])
            presure_str = str(presure)
            self.__dataset.append(
                f'{date_str}{DateAndPressureDataset.data__sepparator}{presure_str}'
            )

        if path_to_save is not None:
            self.save(path=path_to_save)

    def generate_dataset(self,
                         data: str,
                         path_to_save: str = None):
        '''
        :param data: sample of loaded:
        2019-12-28 00:00:00;112.501
        ...

        :return:
        '''
        self.clear_and_set_headder()

        for data_str in data.split('\n'):
            transformed_data_str = self.__transform_date_in_data_string_to_single_format(data_str=data_str)
            self.__dataset.append(transformed_data_str)

        if path_to_save is not None:
            self.save(path=path_to_save)

    def __transform_date_in_data_string_to_single_format(self,
                                                         data_str: str) -> str:
        year_month_day, hour_min_sec_and_pressure = data_str.split(
            DataStringContentInfo.between_YrMthDay_and_HrMnSc__sepparator
        )
        hour_min_sec, pressure = hour_min_sec_and_pressure.split(
            DataStringContentInfo.between_date_info_and_pressure__sepparator
        )

        hour_min_sec = hour_min_sec.replace(DataStringContentInfo.hour_min_sec__sepparator,
                                            DateAndPressureDataset.date__sepparator)
        year_month_day = year_month_day.replace(DataStringContentInfo.year_month_day__sepparator,
                                                DateAndPressureDataset.date__sepparator)
        transformed_data_str = f'{year_month_day}{DateAndPressureDataset.date__sepparator}{hour_min_sec}' \
                               f'{DataStringContentInfo.between_date_info_and_pressure__sepparator}{pressure}'

        return transformed_data_str


if __name__ == '__main__':
    datasets_dir_path = '/home/spaceformind/secondary_cosmic_rays_classification/' \
                        'secondary_cosmic_rays_classification/data/loaded/unsc_kalman_7_dates_datasets'

    for dataset_name in os.listdir(datasets_dir_path):
        path = os.path.join(datasets_dir_path, dataset_name)
        dataset = DateAndPressureDataset()
        dataset.read(path=path)
        dataset.plot(
            save_path='/home/spaceformind/secondary_cosmic_rays_classification/'
                      'secondary_cosmic_rays_classification/data/plots/loaded_data/'
                      'unsc_kalman_7_dates_datasets/{}.png'.format(
                dataset_name.split('.')[0]
            )
        )