# from filterpy.kalman import UnscentedKalmanFilter, MerweScaledSigmaPoints
from pykalman import UnscentedKalmanFilter
import numpy as np
import random
import os

from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset

from secondary_cosmic_rays_classification.data_math_tools.math_operations_on_date_and_presure_dataset import \
    MathOperationsOnDateAndPresureDataset


class SetupUnscentedKalmanFilter:
    # def __init__(self,
    #              datasets_dir_path: str):
    #     self.__filter = UnscentedKalmanFilter(
    #         dim_x=2,  # we have only [Time - 1-dim] & [Preasure - scalar that mean also 1-dim]
    #         dim_z=1,  # cause output is {Presure} - scalar value
    #         dt=60,    # cause meassurement period is [1 min]
    #         fx=SetupUnscentedKalmanFilter.__fx,
    #         hx=SetupUnscentedKalmanFilter.__hx,
    #         points=MerweScaledSigmaPoints(n=4, alpha=.1, beta=2., kappa=-1)  # default setup
    #     )
    #
    #     self.__read_data(datasets_dir_path=datasets_dir_path)
    #
    #     self.__filter.x = np.array([self.__data[0], self.__data[1]])
    #     self.__filter.P *= 0.2
    #     self.__filter.R = np.diag([0.09, 0.09])

    def __setup_calman_filter(self):
        st_deviation = MathOperationsOnDateAndPresureDataset.compute_dataset_standard_deviation(
            dataset_path=self.__dataset_path
        )
        self.__uk_filter = UnscentedKalmanFilter(
            SetupUnscentedKalmanFilter.__fx,
            SetupUnscentedKalmanFilter.__hx,
            observation_covariance=st_deviation ** 2,
            n_dim_state=1,
            n_dim_obs=1,
            initial_state_mean=self.__presures[0]
        )

        self.print_setup()

    def print_setup(self):
        print('UKF Setup:\n------------------------------\n')
        print('R:', self.__uk_filter.observation_covariance)

    def __read_data(self,
                    dataset_path: str):
        dataset = DateAndPressureDataset()
        dataset.read(path=dataset_path)
        self.__dataset_path = dataset_path

        self.__presures = dataset.get_presures_list()
        self.__dates = dataset.get_datetimes_list()

    def filter_data(self,
                    dataset_path):
        self.__read_data(dataset_path=dataset_path)
        self.__setup_calman_filter()

        state_means, state_cov = self.__uk_filter.smooth(self.__presures)
        self.__state_means__presures_filtered = list(state_means.flatten())
        self.__state_cov = list(state_cov.flatten())

    def save_and_plot_filtered_data(self,
                                    filtered_datasets_dir_path: str,
                                    img_datasets_dir_path: str,
                                    dataset_name: str = None):
        if dataset_name is None:
            dataset_name = self.__dataset_path.split('/')[-1]
        if not dataset_name.endswith('.txt'):
            dataset_name = f'{dataset_name}.txt'

        save_data_path = os.path.join(filtered_datasets_dir_path, dataset_name)
        dataset = DateAndPressureDataset()
        dataset.generate_dataset_from_presure_list_and_datetime_list(
            presure_list=self.__state_means__presures_filtered,
            datetime_list=self.__dates,
            path_to_save=save_data_path
        )

        plot_name = '{}.png'.format(dataset_name.split('.')[0])
        save_plot_path = os.path.join(img_datasets_dir_path, plot_name)
        dataset.plot(save_path=save_plot_path)

    @staticmethod
    def __hx(state,
             noise):
        return state + np.cos(noise)

    @staticmethod
    def __fx(state,
             noise):
        return state + np.sin(noise)


if __name__ == '__main__':
    datasets_dir_path= '/home/spaceformind/secondary_cosmic_rays_classification/' \
                       'secondary_cosmic_rays_classification/data/loaded/unsc_kalman_7_dates_datasets'

    setup = SetupUnscentedKalmanFilter()

    for dataset_name in os.listdir(datasets_dir_path):
        datset_path = os.path.join(datasets_dir_path, dataset_name)
        setup.filter_data(dataset_path=datset_path)
        setup.save_and_plot_filtered_data(
            filtered_datasets_dir_path='/home/spaceformind/secondary_cosmic_rays_classification/'
                                       'secondary_cosmic_rays_classification/data/'
                                       'filtered/unsc_kalman_7_dates_datasets',
            img_datasets_dir_path='/home/spaceformind/secondary_cosmic_rays_classification/'
                                  'secondary_cosmic_rays_classification/data/'
                                  'plots/filtered_data/unsc_kalman_7_dates_datasets'
        )