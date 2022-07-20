from datetime import datetime
import json
import os

from secondary_cosmic_rays_classification.data_loader.load_config_creator.load_day_config import LoadDayConfig


class LoadDatesConfig:
    def read(self,
             path: str):
        with open(path, 'r') as f:
            print('Reading Load Dates Config: [{}]'.format(path))
            self.config = json.load(f)

    def create_from_txt_file_with_dates(self,
                                        path_to_txt: str,
                                        num_sep_in_txt: str = '.',
                                        json_dir_to_save: str = None):
        self.config = []

        with open(path_to_txt, 'r') as f:
            dates = [line.strip('\n') for line in f.readlines()]

            for date in  dates:
                year, month, day = [int(number) for number in date.split(sep=num_sep_in_txt)]

                load_day_config = LoadDayConfig()
                load_day_config.create(
                    day_start_date=datetime(
                        year=year,
                        month=month,
                        day=day
                    )
                )

                self.config.append(load_day_config.config_dict)

            if json_dir_to_save is not None:
                json_config_path = os.path.join(
                    json_dir_to_save,
                    '{}.json'.format(os.path.basename(path_to_txt).split('.')[0])
                )
                self.save(path=json_config_path)

    def save(self,
             path: str):
        with open(path, 'w') as f:
            print('Save Dates Load Config: [{}]'.format(path))
            json.dump(self.config, f)


if __name__ == '__main__':
    load_dates_config = LoadDatesConfig()
    task_setup_txt_files_with_dates = [
        '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/load_config_creator/txt/unsc_kalman_7_dates.txt'
    ]

    for path_to_txt in task_setup_txt_files_with_dates:
        load_dates_config.create_from_txt_file_with_dates(
            path_to_txt=path_to_txt,
            json_dir_to_save='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/load_config_creator/json'
        )