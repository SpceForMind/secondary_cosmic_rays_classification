import requests
import os
import random
from concurrent import futures

from secondary_cosmic_rays_classification.data_loader.load_config_creator.load_dates_config import LoadDatesConfig
from secondary_cosmic_rays_classification.data_loader.load_config_creator.load_day_config import LoadDayConfig

from secondary_cosmic_rays_classification.data_loader.dataset.date_and_pressure_dataset import DateAndPressureDataset


class ResponseHtmlContentSeparatorsToHookData:
    before_data__separator = 'start_date_time   RCORR_P'
    after_data__separator = '<'


class DataLoader:
    def load_data(self,
                  load_dates_config_path: str,
                  data_dir: str):
        self.__load_dates_config_path = load_dates_config_path
        self.__data_dir = data_dir

        load_dates_config = LoadDatesConfig()
        load_dates_config.read(path=load_dates_config_path)

        self.__processed_count_requests = 0
        self.__total_count_requests = len(load_dates_config.config)
        random.shuffle(load_dates_config.config)

        # Multi Thread Load requests
        with futures.ThreadPoolExecutor() as executor:
            res = [executor.submit(self.__load_data_by_day_config, load_day_config_dict)
                   for load_day_config_dict in load_dates_config.config[:1000]]
            futures.wait(res)
        # for load_day_config_dict in load_dates_config.config:
        #     self.__load_data_by_day_config(load_day_config_dict)

    def __load_data_by_day_config(self,
                                  load_day_config_dict: dict):
        load_day_config = LoadDayConfig()
        load_day_config.load_config_from_obj(
            config_dict=load_day_config_dict
        )
        dataset = DateAndPressureDataset()

        response = requests.post(
            url='https://www.nmdb.eu/nest/draw_graph.php?'
                'formchk=1&'
                'stations_color%5BAATA%5D=%2333CCCC&stations_color%5BAATB%5D=%2380A0E2&stations_color%5BAPTY%5D=%23778899&stations_color%5BARNM%5D=%231e90ff&stations_color%5BATHN%5D=%236a5acd&stations_color%5BBKSN%5D=%23db6767&stations_color%5BCALG%5D=%2355ee66&stations_color%5BCALM%5D=%23c48248&stations_color%5BDJON%5D=%23EF972B&stations_color%5BDOMB%5D=%23aaee3a&stations_color%5BDOMC%5D=%23b322aa&stations_color%5BDRBS%5D=%23AB9C48&stations_color%5BESOI%5D=%2340e0d0&stations_color%5BFSMT%5D=%2398F466&stations_color%5BHRMS%5D=%2363D7fe&stations_color%5BINVK%5D=%23D7553B&stations_color%5BIRK2%5D=%237fff00&stations_color%5BIRK3%5D=%2389c456&stations_color%5BIRKT%5D=%23339f56&stations_color%5BJBGO%5D=%23FF263C&stations_color%5BJUNG%5D=%23bdb76b&stations_color%5BJUNG1%5D=%239acd32&stations_color%5BKERG%5D=%23ffd700&stations_color%5BKIEL%5D=%23cd5c5c&stations_color%5BKIEL2%5D=%23ddcc5e&stations_color%5BLMKS%5D=%23f4a460&stations_color%5BMCRL%5D=%23ff8c00&stations_color%5BMGDN%5D=%23ff4500&stations_color%5BMOSC%5D=%239400d3&stations_color%5BMRNY%5D=%23da70d6&stations_color%5BMWSN%5D=%23C61704&stations_color%5BMXCO%5D=%23239d48&stations_color%5BNAIN%5D=%236CB0F4&stations_color%5BNANM%5D=%2300bbff&stations_color%5BNEU3%5D=%23F197F9&stations_color%5BNEWK%5D=%23F56C36&stations_color%5BNRLK%5D=%23c71585&stations_color%5BNVBK%5D=%239bcd9b&stations%5B%5D=OULU&stations_color%5BOULU%5D=%23b3ee3a&stations_color%5BPSNM%5D=%23E9A56A&stations_color%5BPTFM%5D=%239fc463&stations_color%5BPWNK%5D=%23E6A50E&stations_color%5BROME%5D=%23cdcd00&stations_color%5BSANB%5D=%23c4863a&stations_color%5BSNAE%5D=%2394439b&stations_color%5BSOPB%5D=%23DC8E90&stations_color%5BSOPO%5D=%23E2D417&stations_color%5BTERA%5D=%2366cdaa&stations_color%5BTHUL%5D=%23C3BE95&stations_color%5BTSMB%5D=%23245fbf&stations_color%5BTXBY%5D=%23FF3399&stations_color%5BYKTK%5D=%23cd96cd&stations_color%5BAHMD%5D=%23AABB23&stations_color%5BCLMX%5D=%23A54B5E&stations_color%5BHUAN%5D=%239EA723&stations_color%5BKGSN%5D=%23B98A3E&stations_color%5BMCMU%5D=%238D65F4&stations_color%5BZUGS%5D=%23934F21&stations_color%5BUFSZ%5D=%23876815&'
                'last_days=1&'
                'last_label=days_label&'
                'date_choice=bydate&'
                f'start_day={load_day_config.config_dict[LoadDayConfig.start_day]}&'
                f'start_month={load_day_config.config_dict[LoadDayConfig.start_month]}&'
                f'start_year={load_day_config.config_dict[LoadDayConfig.start_year]}&'
                f'start_hour={load_day_config.config_dict[LoadDayConfig.start_hour]}&'
                f'start_min={load_day_config.config_dict[LoadDayConfig.start_min]}&'
                f'end_day={load_day_config.config_dict[LoadDayConfig.end_day]}&'
                f'end_month={load_day_config.config_dict[LoadDayConfig.end_month]}&'
                f'end_year={load_day_config.config_dict[LoadDayConfig.end_year]}&'
                f'end_hour={load_day_config.config_dict[LoadDayConfig.end_hour]}&'
                f'end_min={load_day_config.config_dict[LoadDayConfig.end_min]}&'
                'gle_num=73&'
                'fd_num=53&'
                'tresolution=0&'
                'smoothval=0&'
                'dtype=corr_for_pressure&'
                'yunits=0&'
                'output=ascii&'
                'tabchoice=revori&'
                'overplot_color%5B%5D=%23F60F79&'
                'overplot_color%5B%5D=%23125465&'
                'overplot_color%5B%5D=%23781325&'
                'overplot_color%5B%5D=%23555555&'
                'overplot_color%5B%5D=%23561188&'
                'overplot_color%5B%5D=%23561188&'
                'extratype=null&'
                'combine=1'
                '&envplot_color%5B%5D=%237fff00&'
                'envplot_color%5B%5D=%2332CD32&'
                'envplot_color%5B%5D=%23008000&'
                'envplot_color%5B%5D=%239ACD32&'
                'shift=2&'
                'yscalemin=min&'
                'yscalemax=max&'
                'eventduration=**&transp=0&'
                'background_color=%23FFFFFF&'
                'margin_color=%23FFFFFF&'
                'text_color=%23222222&'
                'fontsize=1&'
                'ygrid=1&'
                'mline=1',
            headers={
                #    'Cookie': 'PHPSESSID=ra5papiqqda610bbmstnje426o',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        data_part = self.__hook_data_from_html_response(html_response=response.content)
        dataset.generate_dataset(data=data_part)
        start_date_y_m_d = f'{DateAndPressureDataset.date__sepparator}'.join(
            dataset.get_dataset(without_headder=True)[0].split(
            DateAndPressureDataset.data__sepparator)[0].split(DateAndPressureDataset.date__sepparator)[0 : 3]
        )

        dataset_name = f"{start_date_y_m_d}.txt"
        datasets_dir = os.path.join(self.__data_dir,
                                   f"{os.path.basename(self.__load_dates_config_path).split('.')[0]}_datasets")
        dataset_path = os.path.join(datasets_dir, dataset_name)

        if not os.path.exists(datasets_dir):
            print('Creating datasets dir: [{}]...'.format(datasets_dir))
            os.mkdir(datasets_dir)

        dataset.save(path=dataset_path)

        self.__processed_count_requests += 1
        print('Processed Requests: [{}/{}]...'.format(self.__processed_count_requests,
                                                      self.__total_count_requests))

    def __hook_data_from_html_response(self,
                                       html_response: bytes) -> str:
        html = html_response.decode('utf-8')
        data_part_right = html.split(ResponseHtmlContentSeparatorsToHookData.before_data__separator)[-1]
        data_part = data_part_right.split(
            ResponseHtmlContentSeparatorsToHookData.after_data__separator)[0].rstrip('\n').lstrip('\n')
        return data_part


if __name__ == '__main__':
    data_loader = DataLoader()
    config_setup_json_configs = [
        # '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/'
        # 'load_config_creator/json/high_dates.json',
        # '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/'
        # 'load_config_creator/json/middle_dates.json'
        # '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/'
        # 'load_config_creator/json/middle.json',
        '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/'
        'load_config_creator/json/calm.json',
        # '/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/'
        # 'load_config_creator/json/high.json'
    ]

    for json_config in config_setup_json_configs:
        data_loader.load_data(
            load_dates_config_path=json_config,
            data_dir='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/'
                     'data/all_days'
        )