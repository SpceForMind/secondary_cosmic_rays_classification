from typing import List
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset


class PlotOperationsOnDateAndPresureDataset:
    def merge_plots(self,
                    dataset_dir_paths: List[str],
                    img_save_dir_path: str):
        '''

        :param dataset_dir_paths:
            Must be list of such dataset dirs that contains same dataset filenames
            Sample:
            >>> [
            >>>         '/home/spaceformind/secondary_cosmic_rays_classification/'
            >>>         'secondary_cosmic_rays_classification/data/'
            >>>         'filtered/unsc_kalman_7_dates_datasets',
            >>>         '/home/spaceformind/secondary_cosmic_rays_classification/'
            >>>         'secondary_cosmic_rays_classification/data/'
            >>>         'loaded/unsc_kalman_7_dates_datasets'
            >>> ]
        :param img_save_dir_path:
        :return:
        '''
        self.__img_save_dir_path = img_save_dir_path

        dataset_filenames = [dataset_name for dataset_name in os.listdir(dataset_dir_paths[0])]
        self.__dataset_objects_by_dataset_name__dict = {
            dataset_name: []
            for dataset_name in dataset_filenames
        }

        for dataset_dir_path in dataset_dir_paths:
            for dataset_name in dataset_filenames:
                dataset_path = os.path.join(dataset_dir_path, dataset_name)
                dataset_obj = DateAndPressureDataset()
                dataset_obj.read(path=dataset_path)
                self.__dataset_objects_by_dataset_name__dict[dataset_name].append(dataset_obj)

        self.__plot_merged_and_save()

    def __plot_merged_and_save(self):
        for dataset_name, dataset_objects_list in self.__dataset_objects_by_dataset_name__dict.items():
            fig, ax = plt.subplots()
            plt.rcParams["figure.figsize"] = [18.5, 10.5]
            plt.rcParams["figure.autolayout"] = True
            #fig.set_dpi(100)

            random_colors = self.__get_count_colors(count=len(dataset_objects_list))

            for dataset_object, color in zip(dataset_objects_list, random_colors):
                datetimes_list = dataset_object.get_datetimes_list()
                presures_list = dataset_object.get_presures_list()

                # Ploting
                ax.plot(datetimes_list, presures_list, color)

            # Format your axis as required
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m-%d:%H"))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%y-%m-%d:%H"))
            plt.gcf().autofmt_xdate()

            save_path = os.path.join(self.__img_save_dir_path, dataset_name.replace('txt', 'png'))
            print('Saving plot: [{}]...'.format(save_path))
            plt.savefig(save_path)

    def __get_count_colors(self,
                                count: int) -> list:
        self.__collors = [
            'c',
            'r',
            'g',
            'b',
            'y',
            'k',
            'b',
            'm'
        ]

        return self.__collors[ : count]


if __name__ == '__main__':
    dataset_filtered = DateAndPressureDataset()
    dataset_filtered.read_all_datasets_from_dir(
        dir_path='/home/spaceformind/secondary_cosmic_rays_classification/'
                 'secondary_cosmic_rays_classification/data/'
                 'filtered/unsc_kalman_7_dates_datasets'
    )
    dataset_filtered.save(path='/home/spaceformind/secondary_cosmic_rays_classification/'
                               'secondary_cosmic_rays_classification/data/'
                               'filtered/unsc_kalman_7_dates_datasets_merged/from_2021_10_27_to_2021_11_02.txt')
    dataset_loaded = DateAndPressureDataset()
    dataset_loaded.read_all_datasets_from_dir(
        dir_path='/home/spaceformind/secondary_cosmic_rays_classification/'
                 'secondary_cosmic_rays_classification/data/'
                 'loaded/unsc_kalman_7_dates_datasets'
    )
    dataset_loaded.save(path='/home/spaceformind/secondary_cosmic_rays_classification/'
                             'secondary_cosmic_rays_classification/data/'
                             'loaded/unsc_kalman_7_dates_datasets_merged/from_2021_10_27_to_2021_11_02.txt')

    plot_operations = PlotOperationsOnDateAndPresureDataset()
    plot_operations.merge_plots(dataset_dir_paths=[
            '/home/spaceformind/secondary_cosmic_rays_classification/'
            'secondary_cosmic_rays_classification/data/'
            'loaded/unsc_kalman_7_dates_datasets_merged',
            '/home/spaceformind/secondary_cosmic_rays_classification/'
            'secondary_cosmic_rays_classification/data/'
            'filtered/unsc_kalman_7_dates_datasets_merged'
        ],
        img_save_dir_path='/home/spaceformind/secondary_cosmic_rays_classification/'
                          'secondary_cosmic_rays_classification/data/'
                          'plots/merged_filtered_and_loaded_data'
    )


