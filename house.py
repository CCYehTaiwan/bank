from bs4 import BeautifulSoup
import requests
import os
import json
import random
import time

class House:
    
    def __init__(self):
        
        self.headers = {"User-Agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36\
          (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

    @staticmethod
    def split_owner(string):
        lady = ["小姐", "媽媽", "太太"]
        name = string.split(":")[1].split('/')[0][-3:]
        name = name.lstrip(" ")
        
        if 1 < len(name) <= 3:
            lastname  = name[0]
            firstname = name[1:]
            return lastname, name, "girl" if firstname in lady else "boy"
        elif len(name) > 3:
            return "", name, "boy"
    
    @staticmethod
    def split_phone(string):
        phone = string.split(",")[0]
        phone = phone.strip(" ")
        phone = "".join(phone.split("-"))

        return phone

    @staticmethod
    def transfer_string_to_number(string):
        parts = "".join(string.split(","))

        return int(parts)

    @staticmethod
    def select_sex(string):
        if "限女性" not in string:
            return "male"
        return "female"    

    @staticmethod
    def decide_role(string):
        if string == "屋主":
            return "owner"
        else:
            return "notowner"


    def get_house_detail(self, house_id):
        """ 房屋細節 """
        # 紀錄 Cookie 取得 X-CSRF-TOKEN, deviceid
        s = requests.Session()
        url = f'https://rent.591.com.tw/home/{house_id}'
        r = s.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        token_item = soup.select_one('meta[name="csrf-token"]')

        headers = self.headers.copy()
        headers['X-CSRF-TOKEN'] = token_item.get('content')
        headers['deviceid'] = s.cookies.get_dict()['T591_TOKEN']
        headers['device'] = 'pc'

        url = f'https://bff.591.com.tw/v1/house/rent/detail?id={house_id}'
        r = s.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            print('請求失敗', r.status_code)
            return
        house_detail = r.json()['data']
        return house_detail


    def search(self, filter_params=None, sort_params=None):

        """ 搜尋房屋 """
        page = 0
    
        # 紀錄 Cookie 取得 X-CSRF-TOKEN
        s = requests.Session()
        url = 'https://rent.591.com.tw/'
        r = s.get(url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        token_item = soup.select_one('meta[name="csrf-token"]')
    
        headers = self.headers.copy()
        headers['X-CSRF-TOKEN'] = token_item.get('content')

        # 搜尋房屋
        url = 'https://rent.591.com.tw/home/search/rsList'
        params = 'is_format_data=1&is_new_list=1&type=1'
    
        if filter_params:
            params += ''.join([f'&{key}={value}' for key, value, in filter_params.items()])
        else:
            params += '&region=1&kind=0' # region: 縣市, kind: 屋子類型

        s.cookies.set('urlJumpIp', filter_params.get('region', '1') if filter_params else '1', domain='.591.com.tw')

        # 排序參數
        if sort_params:
            params += ''.join([f'&{key}={value}' for key, value, in sort_params.items()])

        r = s.get(url, params=params, headers=headers)
        data = r.json()
        total_count = self.transfer_string_to_number(data['records'])

        all_information = list() 
        while page < (total_count / 30):
            params += f'&firstRow={page*30}'
            r = s.get(url, params=params, headers=headers)
            
            if r.status_code != requests.codes.ok:
                print('請求失敗', r.status_code)
                break
            page += 1
            print(f"page {page} is begin")
            data = r.json()

            p_id = list()
            for item in data['data']['data']:
                for k, v in item.items():
                    if k == "post_id":
                    
                        p_id.append(str(item[k]))
            
            for house_id in enumerate(p_id):
                house_information = dict()   
                
                detail = self.get_house_detail(house_id[1])
                city = filter_params.get('region', '1') if filter_params else '1'
                house_information['_id']     = house_id[1]
                house_information['city']    = city
                house_information['kindTxt'] = detail['favData']['kindTxt']

                if detail['favData']['kindTxt'] == "車位":
                    house_information['shape'] = detail['favData']['kindTxt']
                else:
                    house_information['shape'] = detail['info'][3]['value']

                house_information['price']        = detail['favData']['price']
                house_information['area']         = detail['favData']['area']
                house_information['principal']    = self.split_owner(detail['linkInfo']['name'])[1]
                house_information['lastname']     = self.split_owner(detail['linkInfo']['name'])[0]
                house_information['principalsex'] = self.split_owner(detail['linkInfo']['name'])[2]
                house_information['mobile']       = self.split_phone(detail['linkInfo']['mobile'])
                house_information['roleName']     = detail['linkInfo']['roleName']
                house_information['isrole']       = self.decide_role(detail['linkInfo']['roleName'])
                house_information['rule']         = self.select_sex(detail['service']['rule'])
                all_information.append(house_information)
            
            # 隨機 delay 一段時間
            time.sleep(random.uniform(2, 5))

        return total_count, all_information


if __name__ == "__main__":
    a = House()
    count, information = a.search({"region":"1"})


