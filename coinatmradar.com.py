#!/usr/bin/env python3
import os
import re
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains


class ScraperX:
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument('--headless')

    def __init__(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.is_signed_in = False
        self.is_country_selected = False
        self.is_first_upload = True

    def get_btc_atms(self, url, country):
        actions = ActionChains(self.driver)
        self.driver.get(url)
        sleep(3)
        # Select country
        self.driver.find_element_by_link_text(country).click()
        sleep(3)
        print("Country:", country)
        number_of_atms_country = self.driver.find_element_by_tag_name('h6').text
        number_of_atms_country = re.findall(r'\d+', number_of_atms_country)
        if len(number_of_atms_country) > 0:
            number_of_atms_country = int(number_of_atms_country[0])
        print("Total ATMS in the country:", number_of_atms_country)
        cities = [city.get_attribute('href') for city in self.driver.find_element_by_class_name('cities-list').find_elements_by_tag_name('a')]
        for city in cities:
            print("City:", city)
            self.driver.get(city)
            sleep(2)
            number_of_atms = self.driver.find_element_by_tag_name('h6').text
            number_of_atms = re.findall(r'\d+', number_of_atms)
            if len(number_of_atms) > 0:
                number_of_atms = int(number_of_atms[0])
            print("Total ATMS in the city:", number_of_atms)
            if number_of_atms > 11:
                number_of_atms -= 10
                while number_of_atms > 0:
                    try:
                        load_more = self.driver.find_element_by_class_name('load-more')
                        actions.move_to_element(load_more)
                        sleep(1)
                        actions.click(load_more.find_element_by_tag_name('a'))
                        actions.perform()
                        sleep(2)
                        number_of_atms -= 10
                    except NoSuchElementException as exe:
                        break
            atms = [atm.get_attribute('href') for atm in self.driver.find_elements_by_link_text('Details')]
            print("ATMs Loaded:", len(atms))
            for atm in atms:
                atm_details = {}
                # phone = ''
                # print("ATM:", atm)
                self.driver.get(atm)
                sleep(1)
                company_name = self.driver.find_elements_by_tag_name('fieldset')[1].find_elements_by_tag_name('p')[0].text
                company_name = company_name[16:]
                # company_phone = self.driver.find_elements_by_tag_name('fieldset')[1].find_elements_by_tag_name('p')[1].text
                # company_email = self.driver.find_elements_by_tag_name('fieldset')[1].find_elements_by_tag_name('p')[2].text
                location_text = self.driver.find_elements_by_tag_name('fieldset')[2].text
                # atm_city = self.driver.find_elements_by_tag_name('fieldset')[2].find_elements_by_tag_name('p')[0].find_element_by_tag_name('a').text
                location = self.driver.find_elements_by_tag_name('fieldset')[2].find_elements_by_tag_name('p')[1].text
                # print("Location Text:", location_text)
                if 'Open hours:' in location_text:
                    open_hours = re.findall(r'(?<=Open hours:\n)(.*)', location_text)
                    if len(open_hours) > 0:
                        open_hours = open_hours[0]
                        open_hours = re.sub(',', '', open_hours)
                        open_hours = re.sub('\\n', '/', open_hours)
                else:
                    open_hours = ''
                if 'Business phone:' in location_text:
                    self.driver.find_element_by_class_name('show-biz-phone').click()
                    sleep(1)
                    # phone = self.driver.find_element_by_class_name('biz-phone').text
                    # phone = re.findall(r'(.*)', phone)
                    # phone = phone[0]
                    full_address = self.driver.find_elements_by_tag_name('fieldset')[2].find_elements_by_tag_name('p')[3].text

                    # try:
                    #     open_hours = self.driver.find_elements_by_tag_name('fieldset')[2].find_elements_by_tag_name('p')[4].text
                    # except IndexError:
                    #     open_hours = ''
                else:
                    full_address = self.driver.find_elements_by_tag_name('fieldset')[2].find_elements_by_tag_name('p')[2].text
                    # try:
                    #     open_hours = self.driver.find_elements_by_tag_name('fieldset')[2].find_elements_by_tag_name('p')[3].text
                    # except IndexError:
                    #     open_hours = ''
                full_address = re.sub(',', '', full_address[8:])
                full_address = re.findall('(.*)(?=.*)', full_address)
                # print("Addres Splitted:", full_address)
                address = full_address[1]
                atm_city = full_address[3]
                zip_code = re.findall(r'(\d+)', atm_city)
                if len(zip_code) > 0:
                    zip_code = zip_code[0]
                else: zip_code = ''
                city_name = re.findall(r'(\D+)', atm_city)
                city_name = city_name[0]
                atm_city = zip_code+' '+city_name
                coin = self.driver.find_element_by_id('fee-struct')
                buy_text = coin.find_elements_by_tag_name('td')[1].find_element_by_tag_name('span').get_attribute('class')
                if 'ok_2' in buy_text:
                    buy = 'Yes'
                else: buy = 'No'
                sell_text = coin.find_elements_by_tag_name('td')[2].find_element_by_tag_name('span').get_attribute('class')
                if 'ok_2' in sell_text:
                    sell = 'Yes'
                else: sell = 'No'
                try:
                    daily_limit = self.driver.find_elements_by_tag_name('fieldset')[3].find_elements_by_tag_name('p')[4].text
                    # print("Daily Limit:", daily_limit)
                    daily_limit = re.findall(r'(\d+)', daily_limit)
                    if len(daily_limit) > 0:
                        daily_limit = daily_limit[0]
                    else:
                        try:
                            daily_limit = self.driver.find_elements_by_tag_name('fieldset')[3].find_elements_by_tag_name('p')[5].text
                            # print("Daily Limit:", daily_limit)
                            daily_limit = re.findall(r'(\d+)', daily_limit)
                            if len(daily_limit) > 0:
                                daily_limit = daily_limit[0]
                            else:
                                try:
                                    daily_limit = self.driver.find_elements_by_tag_name('fieldset')[3].find_elements_by_tag_name('p')[6].text
                                    # print("Daily Limit:", daily_limit)
                                    daily_limit = re.findall(r'(\d+)', daily_limit)
                                    if len(daily_limit) > 0:
                                        daily_limit = daily_limit[0]
                                    else:
                                        daily_limit = ''
                                except NoSuchElementException:
                                    daily_limit = ''
                        except NoSuchElementException:
                            daily_limit = ''
                except NoSuchElementException:
                    daily_limit = ''
                atm_details['Country'] = [country]
                atm_details["City"] = [atm_city]
                atm_details["Address"] = [address]
                atm_details["Location"] = [location[9:]]
                atm_details["Open hours"] = [open_hours]
                atm_details["Operator"] = [company_name]
                atm_details["Buy"] = [buy]
                atm_details["Sell"] = [sell]
                atm_details["Daily Limit"] = [daily_limit]
                print("ATM Details:", atm_details)
                df = pd.DataFrame.from_dict(atm_details)
                # if file does not exist write header
                if not os.path.isfile(country + '.csv'):
                    df.to_csv(country + '.csv', index=None)
                else:  # else if exists so append without writing the header
                    df.to_csv(country + '.csv', mode='a', header=False, index=None)

    def finish(self):
        self.driver.close()
        self.driver.quit()


def main():
    # ***************************************************************
    #    The program starts from here
    # ***************************************************************
    main_url = 'https://coinatmradar.com/countries/'
    countries_done = ['Italy', 'Netherlands', 'Germany']
    countries = ['Austria']
    scraperx = ScraperX()
    for country in countries:
        scraperx.get_btc_atms(url=main_url, country=country)
    scraperx.finish()


if __name__ == '__main__':
    main()