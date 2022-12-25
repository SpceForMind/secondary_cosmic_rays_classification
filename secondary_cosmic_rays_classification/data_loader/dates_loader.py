from typing import Tuple, List, Any
from datetime import datetime, timedelta
from random import shuffle
import json
import os
import requests
from bs4 import BeautifulSoup
import re


class CalmDatesLoader:
    start_year = 1996
    end_year = 2022

    calm_storm_dir = 'calm_40'

    def generate_calm_dates_by_exclude_high_and_mid_storm_days(self,
                                                               count: int,
                                                               high_storm_dates_dir: str,
                                                               middle_storm_dates_dir: str,
                                                               save_dir: str = None):
        self.__all_dates = []
        start_date = datetime(CalmDatesLoader.start_year, month=1, day=1)
        end_date = datetime(CalmDatesLoader.end_year, month=12, day=31, hour=23, minute=59)
        delta = timedelta(days=1)

        cur_date = start_date

        while cur_date <= end_date:
            self.__all_dates.append(cur_date)
            cur_date += delta

        high_storm_dates = [fname.split('.')[0] for fname in os.listdir(high_storm_dates_dir)]
        middle_storm_dates = [fname.split('.')[0] for fname in os.listdir(middle_storm_dates_dir)]
        converted_high_storm_dates = []
        converted_mid_storm_dates = []

        for high_date in high_storm_dates:
            year, month, day = high_date.split('-')
            converted_high_storm_dates.append(datetime(year=int(year), month=int(month), day=int(day)))

        for mid_date in middle_storm_dates:
            year, month, day = mid_date.split('-')
            converted_mid_storm_dates.append(datetime(year=int(year), month=int(month), day=int(day)))

        excluded_dates = converted_mid_storm_dates + converted_high_storm_dates

        for exc_date in excluded_dates:
            self.__all_dates.remove(exc_date)

        shuffle(self.__all_dates)
        self.__picked_dates = self.__all_dates[ : count]

        if save_dir is not None:
            self.__save_samples(save_dir=save_dir)

        return self.__picked_dates

    def __save_samples(self,
                       save_dir: str):
        path_dir = os.path.join(save_dir, CalmDatesLoader.calm_storm_dir)

        if not os.path.exists(path_dir):
            os.mkdir(path_dir)

        path = os.path.join(path_dir, 'calm_dates.txt')
        picked_dates_str = [f'{date.year}.{date.month}.{date.day}' for date in self.__picked_dates]

        with open(path, 'w') as f:
            f.write('\n'.join(picked_dates_str))
            print(f'Saved: [{path}]')


class HighAndMiddleDatesLoader:
    url_pattern = 'https://www.spaceweatherlive.com/ru/avroralnaya-aktivnost/tor-50-reyting-geomagnitnyh-shtormov/god/%i.html'
    start_year = 1996
    end_year = 2022

    middle_high_th__ = 5

    high_storm_dir__ = 'high'
    middle_storm_dir__ = 'middle'

    def load_top_50_storms_for_each_year(self,
                                         save_dir: str):
        self.__all_dates = []
        self.__all_storm_indexes = []
        i = 0

        for year in range(HighAndMiddleDatesLoader.start_year, HighAndMiddleDatesLoader.end_year + 1):
            resp = requests.get(
                url=HighAndMiddleDatesLoader.url_pattern % year,
                # cookies={
                #     "key": "0ee785ad-0a13-4dad-b13c-120333fb640b"
                # }
                headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.3.954 (beta) Yowser/2.5 Safari/537.36'
                }
            )
            soup_parser = BeautifulSoup(resp.content, 'html.parser')
            tds = soup_parser.findAll('td')
            trs = soup_parser.findAll('tr')
            dates = []
            storm_indexes = []

            for td in tds:
                if re.search('[0-9]{4}/[0-9]{2}/[0-9]{2}', td.text):
                    preprocessed_date = td.text.replace('/', '.')
                    dates.append(preprocessed_date)

            dates = dates[:50]

            for tr in trs:
                try:
                    index = tr.findAll('td')[11]
                    storm_indexes.append(int(re.search('\d+', index.text)[0]))
                except Exception:
                    pass

            self.__all_dates += dates
            self.__all_storm_indexes += storm_indexes
            i += 1
            delta = HighAndMiddleDatesLoader.end_year - HighAndMiddleDatesLoader.start_year
            print(f'Progress: [{i}/{delta}]')

        self.__save_samples(save_dir=save_dir)

    def __separate_to_high_and_middle(self) -> Tuple[List[Any], List[Any]]:
        high_dates = []
        middle_dates = []

        for date, storm_index in zip(self.__all_dates, self.__all_storm_indexes):
            if storm_index >= HighAndMiddleDatesLoader.middle_high_th__:
                high_dates.append(date)
            else:
                middle_dates.append(date)

        return middle_dates, high_dates

    def __save_samples(self,
                       save_dir: str):
        mid_dates, high_dates = self.__separate_to_high_and_middle()
        middle_path = os.path.join(save_dir, HighAndMiddleDatesLoader.middle_storm_dir__)
        high_path = os.path.join(save_dir, HighAndMiddleDatesLoader.high_storm_dir__)

        if not os.path.exists(middle_path):
            os.mkdir(middle_path)

        if not os.path.exists(high_path):
            os.mkdir(high_path)

        with open(os.path.join(middle_path, 'middle_dates.txt'), 'w') as f:
            f.write('\n'.join(mid_dates))
            print(f'Saved Middle Dates[count: {len(mid_dates)}] - [{middle_path}]')

        with open(os.path.join(high_path, 'high_dates.txt'), 'w') as f:
            f.write('\n'.join(high_dates))
            print(f'Saved High Dates[count: {len(high_dates)}] - [{high_path}]')


class SpaceWeatherLiveDatesLoader:
    __req_url = 'https://www.spaceweatherlive.com/ru/arhiv.html'
    __calm_prefix = 'Kp'
    __storm_prefix = 'G'

    def parse_all_days(self,
                       txt_dir: str):
        self.__calm_days = []
        self.__middle_days = []
        self.__high_days = []

        for year in range(1996, 2023):
            for month in range(1, 13):
                print(f'Processing: [{month}/{year}]...')
                resp = requests.post(
                    url=SpaceWeatherLiveDatesLoader.__req_url,
                    data={
                        'taal': 'RU',
                        'maand': month,
                        'jaar': year,
                        'verzenden': None
                    },
                    headers={
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.3.954 (beta) Yowser/2.5 Safari/537.36',
                        'content-type': 'application/x-www-form-urlencoded',
                        'accept-language': 'ru,en;q=0.9',
                        'authority': 'www.spaceweatherlive.com'
                    },
                    cookies={
                    # 'CookieScriptConsent': json.dumps({
                    #     "googleconsentmap": {
                    #         "ad_storage": "targeting",
                    #         "analytics_storage": "performance",
                    #         "functionality_storage": "functionality",
                    #         "personalization_storage": "functionality",
                    #         "security_storage": "functionality"},
                    #     "action": "reject", "categories": "[]",
                    #     "CMP": "CPkXcYLPkXcYLF2ADBENCaCgAAAAAAAAAAAAAAAAAAAA.YAAAAAAAAAAA"
                    # }),
                        'SPSI': '3db377cc5ad32806affb3cba4c2df410',
                    #     'SPSE': '03aCYyiV9mGrgUK43TsM1jxhpdX1nAYaG0FKQxsIz3HxV+EGkzv/DRNHeC5oonipzojcK3TLR1qpfZEM9qFPfw==',
                    #     'spcsrf': '5e5e82784a9ee3ca89c924bf32137ac2',
                    #     'adOtr': '73H73cb5cda'
                    }
                )
                soup_parser = BeautifulSoup(resp.content, 'html.parser')

                for cell in soup_parser.findAll("td", {'class': "text-center border border-light px-0"}):
                    day = cell.findAll("h3")[0].text
                    index = cell.findAll("div", {'class': "float-end text-end"})[0].text
                    date = f'{day}.{month}.{year}'

                    if SpaceWeatherLiveDatesLoader.__calm_prefix in index:
                        self.__calm_days.append(date)
                    else:
                        try:
                            storm_index = int(re.search(r'\d', index)[0])
                        except Exception:
                            break
                        
                        if storm_index > 1:
                            self.__high_days.append(date)
                        else:
                            self.__middle_days.append(date)

        self.save(txt_dir=txt_dir)
                            
    def save(self,
             txt_dir: str):
        with open(os.path.join(txt_dir, 'calm.txt'), 'w') as f:
            f.write('\n'.join(self.__calm_days))
        
        with open(os.path.join(txt_dir, 'middle.txt'), 'w') as f:
            f.write('\n'.join(self.__middle_days))
            
        with open(os.path.join(txt_dir, 'high.txt'), 'w') as f:
            f.write('\n'.join(self.__high_days))


if __name__ == '__main__':
    # HighAndMiddleDatesLoader().load_top_50_storms_for_each_year(
    #     save_dir='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/'
    #              'data_loader/load_config_creator/txt/spaceweatherlive'
    # )
    # CalmDatesLoader().generate_calm_dates_by_exclude_high_and_mid_storm_days(
    #     count=900,
    #     high_storm_dates_dir='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data/spacewheatherlive/high',
    #     middle_storm_dates_dir='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data/spacewheatherlive/middle',
    #     save_dir='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/load_config_creator/txt/spaceweatherlive/'
    # )
    SpaceWeatherLiveDatesLoader().parse_all_days(
        txt_dir='/home/spaceformind/secondary_cosmic_rays_classification/secondary_cosmic_rays_classification/data_loader/load_config_creator/txt/spaceweatherlive_full'
    )