from datetime import datetime


class LoadDayConfig:
    start_day = 'start_day'
    start_month = 'start_month'
    start_year = 'start_year'
    start_hour = 'start_hour'
    start_min = 'start_min'
    end_day = 'end_day'
    end_month = 'end_month'
    end_year = 'end_year'
    end_hour = 'end_hour'
    end_min = 'end_min'
    
    def __init__(self):
        self.__start_day_hour = 0
        self.__start_day_min = 0
        self.__end_day_hour = 23
        self.__end_day_min = 59

    def load_config_from_obj(self,
                             config_dict: dict):
        self.config_dict = config_dict

    def create(self,
               day_start_date: datetime):
        self.config_dict = {
            LoadDayConfig.start_day: day_start_date.day,
            LoadDayConfig.start_month: day_start_date.month,
            LoadDayConfig.start_year: day_start_date.year,
            LoadDayConfig.start_hour: self.__start_day_hour,
            LoadDayConfig.start_min: self.__start_day_min,
            LoadDayConfig.end_day: day_start_date.day,
            LoadDayConfig.end_month: day_start_date.month,
            LoadDayConfig.end_year: day_start_date.year,
            LoadDayConfig.end_hour: self.__end_day_hour,
            LoadDayConfig.end_min: self.__end_day_min, 
        }