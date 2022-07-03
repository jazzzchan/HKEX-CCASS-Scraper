#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 14:55:35 2022

@author: jessiechen
reference: https://github.com/Cathy272272272/HKEX-web-scraping/blob/master/HKEX.py
"""

import time

import requests, json
from lxml import etree
from datetime import datetime, timedelta
from urllib.parse import quote
import urllib3


urllib3.disable_warnings()


def get_days(day1, day2):
    date1 = datetime.strptime(day1, "%Y-%m-%d")
    date2 = datetime.strptime(day2, "%Y-%m-%d")
    days = (date2-date1).days
    return days

class Function:

    def __init__(self, window, value):
        self.today = str(datetime.today().date()).replace('-','')
        self.s = requests.Session()

        self.window = window
        self.value = value

    def get_arguments(self):
        url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"
        headers = {
            'Host': 'www3.hkexnews.hk',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://sc.hkexnews.hk/'  #https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referer
                    }
        try:
            response = self.s.get(url, headers=headers, verify=False, timeout=5)
        except:
            txt = 'arguments timeout，click【trend plot】again'
            self.window.write_event_value('message', txt)
            return 'error'

        html = etree.HTML(response.text)
        __VIEWSTATE = html.xpath('.//input[@name="__VIEWSTATE"]/@value')[0]
        self.__VIEWSTATE = quote(__VIEWSTATE,'utf-8')
        self.__VIEWSTATEGENERATOR = html.xpath('.//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]

        return

    def get_data(self, date, code):

        date_form = date.replace('-','/')
        url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"
        payload = f"__EVENTTARGET=btnSearch&__EVENTARGUMENT=&__VIEWSTATE={self.__VIEWSTATE}&__VIEWSTATEGENERATOR={self.__VIEWSTATEGENERATOR}&today={self.today}&sortBy=shareholding&sortDirection=desc&alertMsg=&txtShareholdingDate={date_form}&txtStockCode={code}&txtStockName=&txtParticipantID=&txtParticipantName=&txtSelPartID="
        headers = {
            'Host': 'www3.hkexnews.hk',
            'origin': 'https://www3.hkexnews.hk',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://www3.hkexnews.hk/sdw/search/searchsdw.aspx'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload, verify=False,timeout=5)
        except:
            txt = 'Current connection timeout: %s'%date
            self.window.write_event_value('message', txt)
            return

        html = etree.HTML(response.text)
        data_list = html.xpath('.//tbody/tr')
        
        for data in data_list:
            info = {}
            info['Date'] = date
            try:
                info['Participant ID'] = data.xpath('.//td[@class="col-participant-id"]/div[@class="mobile-list-body"]/text()')[0]
            except:
                info['Participant ID'] = ''
            try:
                info['Participant Name'] = data.xpath('.//td[@class="col-participant-name"]/div[@class="mobile-list-body"]/text()')[0]
            except:
                info['Participant Name'] = ''
            try:
                info['Address'] = data.xpath('.//td[@class="col-address"]/div[@class="mobile-list-body"]/text()')[0]
            except:
                info['Address'] = ''
            try:
                info['Shareholding'] = data.xpath('.//td[contains(@class,"col-shareholding ")]/div[@class="mobile-list-body"]/text()')[0].replace(',','')
            except:
                info['Shareholding'] = ''
            try:
                info['Threshold % of Total'] = data.xpath('.//td[contains(@class,"col-shareholding-percent")]/div[@class="mobile-list-body"]/text()')[0].replace(',','').replace('%','')
            except:
                info['Threshold % of Total'] = ''

            self.DATA.append(info)


    def run(self):
        day = get_days(self.value['startdate'], self.value['enddate'])
        result = self.get_arguments()
        if result == 'error':
            return

        date = datetime.strptime(self.value['enddate'], "%Y-%m-%d").date()
        self.window.write_event_value('message', 'Getting data......')
        time.sleep(2)
        self.DATA = []
        for i in range(day+1):
            date_str = str(date)
            self.window.write_event_value('message', 'Getting %s data......'%date_str)
            self.get_data(date_str, code=self.value['stockcode'])
            date = date - timedelta(days=1)

        self.window.write_event_value('message', 'Finished')
        self.window.write_event_value('result', self.DATA)


