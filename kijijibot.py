#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import yaml
import argparse
try:
    from IPython import embed
except ImportError:
    print 'IPython is not installed'

xpath = {}
xpath['ads_page_btn'] = "//a[contains(text(), 'Mon Kijiji')]"
xpath['login_page_btn'] = "//a[contains(text(), 'Ouvrir une session')]"
xpath['email_input'] = "//input[@class = 'kdd_email']"
xpath['pw_input'] = "//input[@name = 'Password']"
xpath['login_btn'] = "//input[@id = 'signinbtn']"
xpath['ads_category_btn'] = "//a[contains(text(), 'vente, vente de détail')]"
xpath['post_ads_btn'] = "//input[@id = 'PostAd']"
xpath['post_ads_page_btn'] = "//a[contains(@class, 'button-open')]"
xpath['ad_title'] = "//input[@name = 'Title']"
xpath['ad_desc'] = "//textarea[@name = 'Description']"
xpath['ad_address'] = "//input[@name = 'MapAddress']"
xpath['videos_input'] = "//input[@name = 'AdVideoUrl']"
xpath['ad_delete_btn'] = "//a[@title = 'Supprimer']"

class Kijijibot():

    def __init__(self, args):
        
        self.base_url = 'http://www.kijiji.ca/h-grand-montreal/80002'
        self.config = yaml.load(open("./config/config.yaml", 'r'))
        self.args = args
        self.ads = self.config.get('ads')
        print 'ads', self.ads

        if self.config.get('dev'):
            self.driver = webdriver.Chrome()
            self.driver.set_window_position(0,0)
            self.driver.set_window_size(1650,725)
        else:
           self.driver = webdriver.Remote(
                command_executor=self.config.get('browserstack'),
                desired_capabilities= {'browser': 'Chrome', 'browser_version': '35.0', 'os': 'Windows', 'os_version': '7', 'resolution': '1024x768'}
            )

        self.driver.get(self.base_url)

        try:
            self.run()
        except:
            raise
        finally:
            if self.driver:
                self.driver.quit()

    def find_and_click(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()

    def find_and_sendkeys(self, xpath, text):
        self.driver.find_element_by_xpath(xpath).send_keys(text)

    def run(self):

        self.username = self.config.get('username')
        self.password = self.config.get('pw')

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,xpath['login_page_btn'])))

        self.login()

        if self.args.delete_ads:
            self.delete_ads()

        if self.args.post_ads:
            self.post_ads()

        self.logout()

    def login(self):
        self.find_and_click(xpath['login_page_btn'])

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,xpath['login_btn'])))

        self.find_and_sendkeys(xpath['email_input'], self.username)
        self.find_and_sendkeys(xpath['pw_input'], self.password)

        self.find_and_click(xpath['login_btn'])

    def go_to_the_ads_page(self):
        self.driver.get("http://montreal.kijiji.ca/c-SelectCategory")

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,xpath['ads_category_btn'])))

    def delete_ads(self):
        self.go_to_home()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,xpath['ads_page_btn'])))

        self.find_and_click(xpath['ads_page_btn'])

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//div[contains(text(), 'Mes annonces')]")))

        del_btns = self.driver.find_elements_by_xpath(xpath['ad_delete_btn'])

        for del_btn in del_btns:
            self.driver.find_element_by_id(del_btn.get_attribute('id')).click()

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//div[contains(text(), 'Supprimer l')]")))

            self.driver.execute_script("document.getElementsByName('SurveyResponse')[3].checked = true")
            self.driver.execute_script("document.getElementById('ManageMyAdsDeleteForm').submit()")

    def go_to_home(self):
        self.driver.get(self.base_url)

    def post_ads(self):
        for ad in self.ads:

            #Skip disabled ad
            if ad.get('enabled') == False:
                continue

            self.go_to_home()

            self.go_to_the_ads_page()

            self.find_and_click(xpath['ads_category_btn'])

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(), 'Détails de l')]")))

            #Ad type
            self.driver.execute_script("document.getElementById('A_JobType_ID').options[1].selected = true")

            #Ad title
            self.find_and_sendkeys(xpath['ad_title'], ad.get('title'))

            #Ad desc
            self.find_and_sendkeys(xpath['ad_desc'], ad.get('desc'))

            #Ad subarea
            self.driver.execute_script("document.getElementById('SubArea').options[4].selected = true")

            #Ad address
            self.find_and_sendkeys(xpath['ad_address'], ad.get('address'))

            #Terms of use
            self.driver.execute_script("document.getElementById('TermsCheck').checked = true")

            #Videos
            self.driver.find_element_by_xpath(xpath['videos_input']).clear()

            #Post
            self.driver.execute_script("document.getElementById('MainForm').submit()")
        

    def logout(self):
        self.driver.get('http://montreal.kijiji.ca/c-SignOut')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kijiji bot')
    parser.add_argument('-d', action = 'store_true', dest = 'delete_ads', help = 'Delete all the ads')
    parser.add_argument('-p', action = 'store_true', dest = 'post_ads', help = 'Post the enabled ads')
    args = parser.parse_args()

    Kijijibot(args)
