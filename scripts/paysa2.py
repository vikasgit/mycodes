from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

import csv
from selenium import webdriver
import sys
import os

page_num=2

# this class has all the company attributes. Titles , install path and others

class PaysaCompany(object):
    def __init__(self, company_name, root_path, web_driver):
	self.titles = []
        self.titles_list_pages = []
        self.name = company_name
        self.driver = web_driver
        self.dirname = os.path.join(root_path, company_name) 
        self.titles_dirname = os.path.join(self.dirname, 'titles')
        if not os.path.exists(self.dirname):
                  os.makedirs(self.dirname)
           # creating directory now we will save the pages in it later
        if not os.path.exists(self.titles_dirname):
                  os.makedirs(self.titles_dirname)
        self.title_base_url = '%s%s%s' % ('https://www.paysa.com/salaries-list/title/', self.name, '_p')  

    def open_company_pages_save(self, max_page):
        num=1
        while(num<max_page+1):
           company_titles_page = '%s%s%d' % (self.name, "_list_page_", num)
           company_title_page_path = os.path.join(self.dirname, company_titles_page)
           if os.path.isfile(company_title_page_path):
               num = num + 1
               continue 
           url = '%s%d' % (self.title_base_url, num)  
           self.driver.get(url);
           time.sleep(15) # Let the user actually see something!
#print(soup)
           soup = BeautifulSoup(self.driver.page_source, 'lxml')
           if not os.path.isfile(company_title_page_path):
               file = open(company_title_page_path, "w")
               file.write(str(soup))
               file.flush()
               file.close()
           num = num + 1

    def get_company_pages_path(self):
          print(self.name)	

    def get_all_titles_company(self, num):
           company_titles_page = '%s%s%d' % (self.name, "_list_page_", num)
           company_title_page_path = os.path.join(self.dirname, company_titles_page) 
           bsoup = BeautifulSoup(open(company_title_page_path), 'lxml')
           titles=[]
           try:
               for title in bsoup.findAll("div", {"class": "torso-listing-entry"}):
                  link = title.a['href']
                  titles.append('%s' %(link))
           finally:
               return titles
    
    # make sure this function is called with a title list page  
    def get_all_titles_curr_page(self, titles, num):
           url = '%s%d' % (self.title_base_url, num)  
           self.driver.get(url);
           time.sleep(8) # Let the user actually see something!
           for link in titles:
              print("Going to click for title link %s", link)
              file_link =  link.rsplit('/', 1)[-1] 
              file_name = '%s' % (file_link)
              if os.path.isfile(os.path.join(self.titles_dirname, file_name)):
                  continue
              time.sleep(8) # Let the user actually see something!
              try:
                  link_next = '%s%s%s%s' % ("//a[contains(@href,\"", link, "\"", ")]")
                  clickme = self.driver.find_element_by_xpath(link_next)
                  clickme.click()
              except:
                  print("Probably last page in this title page")
                  return
              time.sleep(8) # Let the user actually see something!
              soup = BeautifulSoup(self.driver.page_source, 'lxml')
              #print(soup)
              file = open(os.path.join(self.titles_dirname, file_name), "w")
              file.write(str(soup))
              #file.write(str(self.driver.page_source))
              file.flush()
              file.close()
              time.sleep(8) # Let the user actually see something!
              self.driver.back();
              time.sleep(8) # Let load the main page 
    
    def scrap_and_save_company(self):
              self.open_company_pages_save(2)
              for x in range (1, 3):
                  titles = self.get_all_titles_company(x)
                  self.get_all_titles_curr_page(titles, x)
 

class PaysaLevel2Scraper(object):
    def __init__(self, install_path):
	self.companies = []
	self.companies_link = []
        if install_path is '':
           self.PATH = os.getcwd() 
           self.COMPANY_PATH = os.path.join(self.PATH, 'companies')
        print("The install path is %s", self.PATH) 
	#for file in os.listdir(self.COMPANY_PATH):
        """ 
                bsoup = BeautifulSoup(open(file), 'lxml')	
                for r in bsoup.findAll("div", {"class": "torso-listing-entry"}):
                    link = '%s%s' % (self.url, r.a['href'])
        	    company = link.rsplit('/', 1)[-1]
                    self.companies.append(company)
                    self.companies_link.append(link)
        """
		     	 
    def open_driver(self):
	try:
  #driver = webdriver.Chrome('./chromedriver')  # Optional argument, if not specified will search path.
		self.driver = webdriver.Firefox()
	except:
		print("Failed to open web driver")
		raise
        return self.driver

    def close_driver(self):
        self.driver.quit()

if __name__ == '__main__':
   level2_scraper = PaysaLevel2Scraper(install_path='')
   companies = []
   spamReader = csv.reader(open('list'), delimiter=',')
   for row in spamReader:
      for col in row:
         companies.append(col.strip())
   for comp in companies:
         web_driver = level2_scraper.open_driver()
         scraper = PaysaCompany(company_name=comp, root_path=os.getcwd(), web_driver=web_driver)
         scraper.scrap_and_save_company()
         level2_scraper.close_driver()
    
