from secondary_cosmic_rays_classification.data_loader.data_string_content_info import DataStringContentInfo


class DateAndPressureDataset:
    date_info__header = 'DateInfo'
    pressure__header = 'Pressure'
    data__sepparator = DataStringContentInfo.between_date_info_and_pressure__sepparator
    date__sepparator = DataStringContentInfo.year_month_day__sepparator

    def __init__(self):
        self.__dataset = [
            f'{DateAndPressureDataset.date_info__header}'
            f'{DateAndPressureDataset.data__sepparator}'
            f'{DateAndPressureDataset.pressure__header}'
        ]

    def load_from_prepared_data(self,
                                prepared_data_list: list):
        self.__dataset += prepared_data_list

    def get_dataset(self,
                    without_headder: bool = False):
        if without_headder:
            return self.__dataset[1: ]

        return self.__dataset

    def read(self,
             path: str):
        with open(path, 'r') as f:
            self.__dataset = [line.strip('\n') for line in f.readlines()]

    def save(self,
             path: str):
        with open(path, 'w') as f:
            print('Saving dataset: [{}]'.format(path))
            f.write('\n'.join(self.__dataset))

    def clear(self):
        self.__dataset = [
            f'{DateAndPressureDataset.date_info__header}'
            f'{DateAndPressureDataset.data__sepparator}'
            f'{DateAndPressureDataset.pressure__header}'
        ]

    def generate_dataset(self,
                         data: str,
                         path_to_save: str = None):
        '''
        :param data: sample of data:
        2019-12-28 00:00:00;112.501
        ...

        :return:
        '''
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
