from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

import csv
from selenium import webdriver
import sys
import os
import re
from bs4.tests.test_tree import SiblingTest
 
from numpy.f2py.auxfuncs import throw_error
from urllib2 import urlparse
from urlparse import urlparse

class Deque:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def addFront(self, item):
        self.items.append(item)

    def addRear(self, item):
        self.items.insert(0,item)

    def removeFront(self):
        return self.items.pop()

    def removeRear(self):
        return self.items.pop(0)

    def size(self):
        return len(self.items)

#Since Bsoup is stronger for searching and parsing. We`ll need to search in Bsoup object
#selenium will just be used to store the links for clicking

#We want to find the title information in the page. How we do it.
# 1. find all the tags which may contain the title as an attribute. Well this may not look better.
# what we do next it. We try to find the "job title" which is visible on the screen   
class WebDriver(object):
    def __init__(self):
        try:
                #self.driver = webdriver.Chrome('./chromedriver')  # Optional argument, if not specified will search path.
                self.driver = webdriver.Firefox()
        except:
                print("Failed to open web driver")
                raise
    
    def load_page(self, link):
        self.driver.get(link)
        time.sleep(2) # Let the user actually see something!

    def get_driver(self):
        return self.driver
     
    def close_driver(self):
        self.driver.quit()


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True


def get_parent(current):
    if current is not None:
        if current.parent is not None:
            return current.parent
        return None
    return None

def get_sibling(current):
    if current is not None:
        if current.next_sibling is not None:
            if(type(current.next_sibling)==type(current)):
                return current.next_sibling
            return None
        return None
    return None 

def is_leaf(current):
    #print(len(current.contents))
    #print(current.contents)
    if len(current.contents) < 1 and len(current.contents)> 0:
        if(type(current.contents)==type(BeautifulSoup)):
            return False
        return True
    return False


#comparing two nodes
def compare_top_link_nodes(bSoup1, bSoup2):
    if type(bSoup1) is not type(bSoup2):
        return False
    for val in APPLY_LINKS: # some websited get multiple links for same job link using "apply" or "save job" 
        if val in  bSoup1.get_text():
            print("Apply link found")
            return False
    print("Printing bsoup11")
    print(bSoup1)    
    return(bSoup1.attrs.keys()==bSoup2.attrs.keys())

        
# match the tags class or id with job detail or else
TITLE_TAG = ["jobtitle", "job-title", "job title", "jobTitle-link", "jobs_list", "job description"]
DATE_TAG= ["Posted", "last posted", "updated", "date-posted", "date"]
COUNTRY_TAG = ["country"]
CITY_TAG = ["city"]
STATE_TAG = ["state"]
LOCATION_TAG = ["location"]
#extra job types
#add here job types.
JOB_TYPE1 = ["type", "department"]
JOB_TYPE2 = [""] 
#next page search tags.
NEXT_PAGE_TAG = ["Next"]

ATTRS = ['class', 'id', 'href', 'ng-click', 'title']
APPLY_LINKS = ["Apply", "Add to", "job cart"]

def normalize (text):
    return text.lower().strip()
#visible_texts = filter(visible, raw)
    
#this class represent top level Node. We can notice multiple but finally has to chose one
class topLevelJobNode(object):  
    def __init__(self, html_node):
        self.node = html_node
        self.siblings = []
        self.tupInfo = set([])
    
    def addSibling(self, html_sibling):  # called only for head node.
        self.siblings.append(html_sibling)
    
    def addTupleInfo (self, tupname):
        self.tupInfo.add(tupname)   
                   


#this class should help in locating the top level tags: like jobdetails, job-description.
#add your tags in the list so that it may useful for other websites.

class JobDataExtractor(object):
    """
        Need A webdriver to initialize and URL to extract Links
    """
    def __init__(self, company=None, webdriver=None, url=None, bsoup = None):
        self.wdriver = webdriver
        self.main_url = url
        self.mnpage_bsoup = bsoup
        if webdriver is not None: 
              
            try:
                self.wdriver = webdriver
            except:
                print("Failed to Open WebDriver. please check the supported modules and their path")
                raise    
            self.wdriver.load_page(url)
            self.mnpage_bsoup = BeautifulSoup(self.wdriver.get_driver().page_source, 'lxml')
            
        if url is not None:
            r = urlparse(url)
            self.url_base = r.scheme + "://" + r.netloc
        """
            Links saver for Webdriver to go for next pages. 
        """
                
        self.compnayName = company
        
        self.job_links_href = [] 
        self.page_next_href = None
        
        self.jobLinks = []
        self.possible_top_link_nodes = []   
        
        self.current_page_number = 1   
    
    def addJobLink(self, href):
        self.job_links_href.append(href)
    
    def addNextLink(self, href):
        self.page_next_href = href
    
    def clearAll(self):
        self.job_links_href = []
        self.page_next_href = None    
        
        
    def exploreSubTrees(self, node, root, depth):
    #we need to find the node in rooted subtree. the node should be at 'depth'
    #when depth reach to 0 we need to find in all the siblings.
    #just find out the leftmost child and then traverse through siblings
        lstnode = root
        level = depth
        print("calles explore sub tress with depth", '%d' % (depth))
        print(root)
        while(level is not 0):
            for kids in lstnode.children:  #cousins
                #print(kids)
                if(type(kids) != type(node)):
                    print("Failed to find another kid...")
                    continue
                    
                lstnode = kids
                if lstnode is None:
                    return False
                if compare_top_link_nodes(lstnode, node) is True:
                    return True
                break # only left most test kid 
            
            level = level -1
            continue
        print("Level is", '%d' % (level))
        print(lstnode)
        for sibs in lstnode.next_siblings:
            print(sibs)
            if type(sibs) != type(lstnode):
                    continue
        
            if compare_top_link_nodes(sibs, node) is True:
                return True        
        
        return False    
    
    def locateEquivalentNode(self, bSoup):
        #we will find how much is the gap between the Link nodes, i.e similar node so that we can now what elements
        # can be in between.
        depth = 0 # depth=0 in siblings, depth =1 cousins , depth2 = grand cousins
        current = bSoup
           
        while True:
            #explore all uncles
            print("Prinitng current....")
            print(current)
            for sibs in current.next_siblings:
                if type(sibs) != type(current):
                    continue
                if self.exploreSubTrees(bSoup, sibs, depth) is True:
                    return depth
            current = get_parent(current)
            depth = depth + 1
            if depth > 10:
                print("Oopps level has gone beyond 10...Please check with the top level link node found")
                return -1 

    def extractInfoSubTrees(self, topNode): #BFS from top node
        bRoot = topNode.node
        dSoup  = Deque()
        dSoup.addRear(bRoot)
        while(dSoup.isEmpty() is False):
            fBSoup = dSoup.removeFront()
            for tups in exploreForTags(fBSoup):
                topNode.addTupleInfo(tups)
            if is_leaf(fBSoup):
                for tups in exploreForTags(fBSoup):
                    topNode.addTupleInfo(tups)
                
            else:     
                for kids in fBSoup.children :  #cousins
                    #print(kids)
                    if(type(kids) != type(bRoot)):
                        #print("Failed to find another kid...")
                        continue
                    #print("Adding kids in rear")
                    #print(kids)
                    dSoup.addRear(kids)        
        
        #print("Printing node info")
        
    def printAllLinks(self):
        print ("Total number of top links found" "%d" % (len(self.possible_top_link_nodes)))
          
        #for jLink in self.job_links_href:
        #        print("Going to load " '%s' % (jLink))      
         
    def getAllResults(self):
        jobList = [] # only list of key:val
        if len(self.possible_top_link_nodes) > 1:
            raise 
        topNode = self.possible_top_link_nodes[0]
        num_sibs = len(topNode.siblings)
        start=0
        while num_sibs >= 0:
            for jobset in topNode.tupInfo:
                rJobs = {}
                for jobs in jobset:
                    print(jobs)
                    if jobs[0] == 'jobLink':
                        rlink = jobs[1]
                        if (('http') not in rlink):
                            rlink = "%s%s" % (self.url_base, rlink)
                        rJobs['Link'] = rlink
                    elif jobs[0] == 'date':
                        rJobs['date'] = jobs [1]
                jobList.append(rJobs)
            topNode = topNode.siblings[start]
            start = start + 1
            num_sibs = num_sibs-1    
	    return (jobList)	       
                            
    
    def extractNextPageLink(self, bsoup):
    # we`ll just check for the next page links checking the text
    # "1" , "2" and "next" to make it sure its actually next    
        NEXT_PAGE_TEXT = ["1", "2", "Next"] 
        bsoup_next_page_link = None
        for link in bsoup.find_all('a'):
            try:
                if link.has_attr('href') is False:
                    continue
                is_link = link['href']
            except:
                pass
                continue 
            #print(link.get_text().strip())   
            if link.get_text().strip() == self.current_page_number:
                print("Extracting Next page link1...")
                self.page_next_href = str(self.current_page_number).strip()  
                return link
                """
                sib = get_sibling(link)
                if sib is not None:
                    if sib.get_text().strip() is "2":
                        print("Found Next page node")
                        return link
                """        
            """
            if link.get_text().strip() == "2":
                print("Extracting Next page link1...")
                
                sib = get_sibling(link)
                if sib is not None:
                    if sib.get_text().strip() is "3":
                        print("Found Next page node")
                        return link
            """                    
            #verify with "Next" keyword
            if (link.get_text().strip().lower() == "next"):
                self.addNextLink(link.get_text())
                return link['href']    
       
            
    """
    1) Load first job-page
    2) Extract all links and save in 'selLinksForPage' object
    3) Visit all links and extract data (yet to be done)
    4) Click on the next page if its not none.
    5) Go to #2 
    """       
     
    def runExtractor(self):
        self.extractAllHrefs(self.mnpage_bsoup)
        self.extractNextPageLink(self.mnpage_bsoup)
        
        if self.wdriver is None:
            return
            
        while self.page_next_href is not None:
            for jLink in self.job_links_href:
                print("Going to load " '%s' % (jLink))
                link=None
                
                try:
                    link = self.wdriver.driver.find_element_by_partial_link_text(jLink)
                    
                except:
                    print("Skipping...looks like Webdriver could not find the job link")
                    continue
                 
                link.click()      
                #wdriver.driver.get(jLink)
                time.sleep(8)
                self.wdriver.driver.back()
                time.sleep(12) 
            self.current_page_number = self.current_page_number +1
            print("Loading Next page...")
            print(self.page_next_href) 
            link = self.wdriver.driver.find_element_by_link_text(self.page_next_href)
            link.click()
            
            time.sleep(8)
            #wdriver.driver.get(selClickSaverPage.page_next_href)
            bsoup = BeautifulSoup(self.wdriver.get_driver().page_source, 'lxml')
            self.clearAll()
            self.extractAllHrefs(bsoup)
            self.extractNextPageLink(bsoup)
   
    def ifNodeVisited(self, nBsoup, visitedNodes):
        #check if node or ancestor visited
        depth = 8
        parent = nBsoup.parent    
        while (depth>0 and (parent is not None)):
            if parent in visitedNodes:
                return True
            else:
                parent = parent.parent
        
            depth = depth -1        
        return False 
    
    # we need to improve this . cant just delete the last element locater
    def removeRedundantNodes(self):
        for x in range (0, len(self.possible_top_link_nodes)-1):
            del self.possible_top_link_nodes[0]
      
    def extractClickableNodeText(self, tNode):
        bNode = tNode.node
        text = None
        bsoup = bNode.find_all('a')
        for hrefs in bsoup:
            try:
                text = hrefs.get_text()
            except:
                pass
                text = None
        
        return text    

    # if job top level node is visited then all kids should be makred visited 
    # We dont want to visit them again               
    def markAllKidsVisited(self, bRoot, visited_list):
        dSoup  = Deque()
        dSoup.addRear(bRoot)
        while(dSoup.isEmpty() is False):
            fBSoup = dSoup.removeFront()
            visited_list.add(fBSoup)
            for kids in fBSoup.children:   
                    #print(kids)
                if(type(kids) != type(bRoot)):
                        #print("Failed to find another kid...")
                    continue
                    #print("Adding kids in rear")
                    #print(kids)
                dSoup.addRear(kids)   
        
    def extractAllHrefs(self, bsoup):
        #  We are interested in two top level nodes which further has to be explored.        
        #we need to track the Bsoup nodes who have been visited.
        bSoup_visited = set([])
                 
        for link in bsoup.find_all('a'):
            #check whether leaf node. In most of the cases its leaf node
            top_link_found = False
                    
            try:
                if link.has_attr('href') is False:
                    
                    continue
               
            except:
                pass
                continue
            if link.has_attr('title'):
                print(link['title'].encode('utf-8').strip())
            if self.ifNodeVisited(link, bSoup_visited) is True:
                continue
        
            #Top level node locater for job link
            if ifTitleLinkTagPresent(link) is True:
                top_link_found = True    
                       
            #try one level above              
            if top_link_found is False:
                parent = get_parent(link)
                if parent is not None and parent.has_attr('class'):
                    if ifTitleLinkTagPresent(get_parent(link)) is True:
                        top_link_found = True        
                    
                    
            if top_link_found is False:           
                continue    
            print("Found top level link")          
            print("Locating equivalent node....at")
            
            maxd = self.locateEquivalentNode(link)
            if maxd < 0:
                print("Failed to locate equivalent node. The page is either has less than a job link or Wrong top link looked for..")
                continue
            print("Maxdepth = " , "%d" % (maxd))          
                        
            print("Setting for the parent...")
            current = link
            print(current)
            while(maxd>0):
                current = get_parent(current)
                maxd = maxd -1
            print("Next top Link node located...finding all uncles..")
            print(current)
            
            topNode = topLevelJobNode(current)
            self.extractInfoSubTrees(topNode)
            
            self.possible_top_link_nodes.append(topNode)
              
            bSoup_visited.add(current)
            self.markAllKidsVisited(current, bSoup_visited)
            
            
            for uncle in current.next_siblings:
                if(type(current) != type(uncle)):
                    continue
                topN = topLevelJobNode(uncle)
                self.extractInfoSubTrees(topN)
                bSoup_visited.add(uncle)
                self.markAllKidsVisited(uncle, bSoup_visited)
                #href_in_uncle = uncle.find_all('a')
                print("Printing uncle...")
                topNode.addSibling(topN)
            
        #if multiple top links node found we need to delete them.                  
        if(len (self.possible_top_link_nodes) > 1 ):
            self.removeRedundantNodes()
        
        # saving for Selenium to click
        rtopLevel = self.possible_top_link_nodes[0]
        self.addJobLink(self.extractClickableNodeText(rtopLevel))             
        
        for sibs in rtopLevel.siblings:
            self.addJobLink(self.extractClickableNodeText(sibs))
               

def trySecondryLogicForTopLevelLink(hRef):
    #try some other things...like "jobid" and strings of digits
    #"career" and string of digits.
    print("Trying for...secondry logic for top level")
    #print(hRef)
    if 'search-job' in normalize(hRef):
            return False
    if((('job') in normalize(hRef)) and re.search(re.compile('\d{4}'), normalize(hRef))):
    #if((('jobid' or 'jobdetail' or 'job') in normalize(hRef)) and re.search(re.compile('\d{4}'), normalize(hRef))):
        print("found title ")
        return True
    elif (('position' in normalize(hRef)) and re.search(re.compile('\d{4}'), normalize(hRef))):
        return True
    else:
        return False   

def ifTitleLinkTagPresent(nBsoup):
    for attr in ATTRS:
        if nBsoup.has_attr(attr):
            text = nBsoup[attr]
            if attr is 'href':
                if trySecondryLogicForTopLevelLink(text) is True:
                    return True
            else:    # for 'class' and 'id'
                for val in TITLE_TAG:
                    if val in text :
                        print("Found if title" " %s" % (val))
                        return True
        
    return False

def ifDateTagPresent(tag):
    for val in DATE_TAG:
        if val in tag:
            print("Found if date" " %s" % (val))
            return True
    return False

def ifJobTypeTagPresent(text):
    for val in JOB_TYPE1:
        if val in normalize(text):
            return True
    return False

def ifCityTagPresent(tag):
    if "city" in tag:
        return True
    return False

def ifCountryTagPresent(tag):
    if "country" in tag:
        return True
    return False

def ifStateTagPresent(tag):
    if "state" in tag:
        return True
    return False    

def ifLocationTagPresent(text):
    #print(text)
    if "location" in normalize(text):
        return True
    return False

def ifNextPageTagPresent(tag):
    if tag is None:
        return False
    if "next" in normalize(tag):
        return True
    return False

def ifJobIDTagPresent(tag):
    if "jobId" in tag:
        return True
    return False  

def exploreForTags(nBsoup):
    print("exploring for ##tags")
    tup_arr = []
    for attr in ATTRS:
        if nBsoup.has_attr(attr):
                if attr is 'href':
                    print(nBsoup['href'])
                    tup_arr.append(('jobLink', nBsoup['href']))
                    continue
                if type(nBsoup[attr])==type([]):
                     
                    for val in nBsoup[attr]:
                        #print(val)
                                                   
                        if ifCityTagPresent(val):
                            print(nBsoup.get_text().encode('utf-8').strip())
                            tup_arr.append(('CityName', nBsoup.get_text()))
                        elif ifCountryTagPresent(val):
                            print(nBsoup.get_text()) 
                            tup_arr.append(('Country', nBsoup.get_text()))
                        elif ifStateTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('State', nBsoup.get_text()))
                        elif ifLocationTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('Location', nBsoup.get_text()))
                        elif ifDateTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('Date', nBsoup.get_text()))
                        elif ifJobIDTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('JobId', nBsoup.get_text()))
                        elif ifJobTypeTagPresent(val):
                            print(nBsoup.get_text().encode('utf-8').strip())
                            tup_arr.append(('JobType', nBsoup.get_text().encode('utf-8').strip()))
                           
                else:
                        val = nBsoup[attr].encode('utf-8').strip()
                        print(val)
                        if ifCityTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('CityName', nBsoup.get_text()))
                        elif ifCountryTagPresent(val):
                            print(nBsoup.get_text()) 
                            tup_arr.append(('Country', nBsoup.get_text()))
                        elif ifStateTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('State', nBsoup.get_text()))
                        elif ifLocationTagPresent(val):
                            print(nBsoup.get_text().encode('utf-8').strip())
                            
                            tup_arr.append(('Location', nBsoup.get_text().encode('utf-8').strip()))
                        elif ifDateTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('Date', nBsoup.get_text()))
                        elif ifJobIDTagPresent(val):
                            print(nBsoup.get_text())
                            tup_arr.append(('JobId', nBsoup.get_text()))
                        elif ifJobTypeTagPresent(val):
                            print(nBsoup.get_text().encode('utf-8').strip())
                            tup_arr.append(('JobType', nBsoup.get_text().encode('utf-8').strip()))
               
    print("Explored ..tag")
    return tup_arr

def exploreSiblings(current):
    for sib in current.next_siblings:
        if(type(current) != type(sib)):
            continue
        exploreForTags(sib)  
        

if __name__ == '__main__':
    #url = "https://www.amazon.jobs/en-gb/job_categories/software-development?base_query=&loc_query=&job_count=10&result_limit=10&sort=relevant&category%5B%5D=software-development&cache"
#    url = "https://jobs.cisco.com/go/Engineering-Software/528500/?utm_source=careersite&utm_campaign=CDCCareersHome"
    url = "https://www.facebook.com/careers/search/?q=Engineer&location=menlo-park"
    url = "https://jobs.walmart.com/us/jobs?page=1&tags=ecommerce" 
    url = "https://krb-sjobs.brassring.com/TGnewUI/Search/Home/Home?partnerid=26059&siteid=5016##keyWordSearch=united%20states&locationSearch=&loggedIn=false"
    url = "https://oracle.taleo.net/careersection/2/joblist.ftl"
    #jdata = JobDataExtractor(webdriver=WebDriver(),  url=url)
    jdata = JobDataExtractor(bsoup=BeautifulSoup(open("oracle.soup")))
    jdata.runExtractor()
    jdata.printAllLinks()
    print(jdata.getAllResults())
  

    
