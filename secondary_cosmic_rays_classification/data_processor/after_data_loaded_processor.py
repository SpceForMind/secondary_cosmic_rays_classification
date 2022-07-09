from datetime import datetime, timedelta
import os

from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset


class AfterDataLoadedProcessor:
    date__key = 'data'
    pressure__key = 'pressure'

    def fill_miss_data_by_median(self,
                                 path_to_datasets_dir: str,
                                 median_padding: int = 30):
        '''

        :param path_to_dataset:
        :param median_padding: if 30 -> we get
                               30 left & 30 right of missed value meassures

        :return:
        '''
        print('Process Datasets Dir [{}]:'.format(path_to_datasets_dir))

        for daset_name in os.listdir(path_to_datasets_dir):
            path_to_dataset = os.path.join(path_to_datasets_dir, daset_name)
            print('Processing [{}]...'.format(path_to_dataset))

            dataset = DateAndPressureDataset()
            dataset.read(path=path_to_dataset)
            data_lines = dataset.get_dataset(without_headder=True)
            self.__date_and_pressure_list = []
            self.__median_padding = median_padding

            for data_line in data_lines:
                date_str, pressure_str = data_line.split(DateAndPressureDataset.data__sepparator)
                year, month, day, hour, min, sec = [
                    int(date_part) for date_part in date_str.split(DateAndPressureDataset.date__sepparator)
                ]
                date_datetime = datetime(year=year, month=month, day=day, hour=hour, minute=min, second=sec)

                self.__date_and_pressure_list.append({
                    AfterDataLoadedProcessor.date__key: date_datetime,
                    AfterDataLoadedProcessor.pressure__key: float(pressure_str)
                })

            if self.__find_missed_data_and_insert_median_value():
                self.__update_dataset_with_additional_data(path_to_dataset=path_to_dataset)
            else:
                print('!!! Data has no missed values !!!')

    def __update_dataset_with_additional_data(self,
                                              path_to_dataset):
        updated_dataset = DateAndPressureDataset()
        prepared_data_list = []

        for item in self.__date_and_pressure_list:
            date = item[AfterDataLoadedProcessor.date__key]
            pressure_str = str(item[AfterDataLoadedProcessor.pressure__key])
            date_str = f'{DateAndPressureDataset.date__sepparator}'.join(
                [str(date.year), str(date.month), str(date.day),
                 str(date.hour), str(date.minute), str(date.second)]
            )

            prepared_data_list.append(f'{date_str}{DateAndPressureDataset.data__sepparator}{pressure_str}')

        updated_dataset.load_from_prepared_data(prepared_data_list=prepared_data_list)
        updated_dataset.save(path=path_to_dataset)

    def __generate_missed_data(self,
                                left_data_idx: int) -> dict:
        end_idx = len(self.__date_and_pressure_list) - 1
        start_idx = 0

        if  left_data_idx + self.__median_padding > end_idx:
            values_to_end_idx = end_idx - left_data_idx
            right_take_idx = end_idx
            left_take_idx = left_data_idx - (2 * self.__median_padding - values_to_end_idx)
        elif left_data_idx - self.__median_padding < start_idx:
            values_to_start_idx = left_data_idx - start_idx
            left_take_idx = start_idx
            right_take_idx = left_data_idx + (2 * self.__median_padding - values_to_start_idx)
        else:
            left_take_idx = left_data_idx - self.__median_padding
            right_take_idx = left_data_idx + self.__median_padding

        window_values = [item[AfterDataLoadedProcessor.pressure__key]
                         for item in self.__date_and_pressure_list[left_take_idx : right_take_idx]]
        median_value = sorted(window_values)[int(len(window_values) / 2)]
        missed_date = self.__date_and_pressure_list[left_data_idx][AfterDataLoadedProcessor.date__key] + \
                      timedelta(minutes=1)

        return {
            AfterDataLoadedProcessor.date__key: missed_date,
            AfterDataLoadedProcessor.pressure__key: median_value
        }

    def __find_missed_data_and_insert_median_value(self) -> bool:
        '''

        :return: if data was modified by new missed values -> True
                                                    / else -> False
        '''
        data_has_missed_values = True
        previous_data_len = len(self.__date_and_pressure_list)

        while data_has_missed_values:
            # In cycle bellow switch it to True if data has missed values / else -> while {False} and break out
            data_has_missed_values = False
            missed_data_and_index_pairs_list = []

            for data_idx in range(len(self.__date_and_pressure_list)):
                if data_idx + 1 > len(self.__date_and_pressure_list) - 1:
                    break

                part_data = self.__date_and_pressure_list[data_idx]
                next_part_data = self.__date_and_pressure_list[data_idx + 1]
                timedelta = next_part_data[AfterDataLoadedProcessor.date__key] - \
                            part_data[AfterDataLoadedProcessor.date__key]

                if int(timedelta.total_seconds()) > 60:
                    missed_data = self.__generate_missed_data(left_data_idx=data_idx)
                    missed_data_and_index_pairs_list.append(
                        (missed_data, data_idx)
                    )
                    data_has_missed_values = True

            for missed_data, idx_after_insert in missed_data_and_index_pairs_list:
                self.__date_and_pressure_list.insert(
                    idx_after_insert + 1,
                    missed_data
                )

        return len(self.__date_and_pressure_list) > previous_data_len



if __name__ == '__main__':
    data_processor = AfterDataLoadedProcessor()
    setup_task_daatasets_path = [
        '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/data/calm_days_dates_datasets',
        '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/data/low_storm_dates_datasets',
        '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/data/high_storm_dates_datasets'
    ]

    for path_to_datasets in setup_task_daatasets_path:
        data_processor.fill_miss_data_by_median(
            path_to_datasets_dir=path_to_datasets
        )


