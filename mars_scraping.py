########
###Web Scraping and Mongo DB homework
###by Dustin Rice
###11/16/2018
########
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from splinter import Browser
import time

def usgs_findlink(html):
    """Takes HTML from https://astrogeology.usgs.gov/ hemisphere search results"""
    """returns a dictionary with {title:<title>, img_url:<url>"""
    lsoup = bs(html, "html.parser")
    img_url = lsoup.find('dt', text='Filename').find_next_sibling().a['href']
    #Finds the table entry filename, then 'next sibling' finds the table entry next to it, which is the link 
    #(accessed by .a to find the anchor tag, and [href] to read the text)
    
    lastchar = lsoup.title.text.find(' Enhanced') #Finds the char number of the space before the word enhanced - 
    #which comes after the hemisphere name in the HTML title
    title = lsoup.title.text[:lastchar] #slices the HTML title up to that character number
    out_dict = {"title": title, "img_url": img_url}
    return out_dict

def scrape():
    """scrapes Nasa Mars News, featured JPL imagery, Space-facts.com, and USGS Astrogeology"""
    """returns a dictionary with several subdictionaries:"""
    """News containing news_title and news_text.  JPL containing img_title and img_url"""
    """facts containing a string HTML table.  Weather containing a string"""
    """USGS containing a list of dictionaries each with title and img_url"""
    """Function contains multiple .sleep() and may take a few seconds to run.  Will launch a chrome window."""
    # ## Mars News Section
    #Requests.get doesn't seem to return the latest articles, they may be loaded by Javascript
    #Chromedriver will be used instead.
    #Set up the chromedriver browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser("chrome", **executable_path, headless=False)
    browser.visit('https://mars.nasa.gov/news/') #send it to the URL
    time.sleep(3) #Wait for loading
    mnews_html = browser.html #get the HTML
    nasa_soup = bs(mnews_html, "html.parser") #Parse the HTML into soup
    # Each article is in a li with class 'slide', we only need the first one.
    latestnews=nasa_soup.find('li', class_='slide')
    news_title=latestnews.find('div', class_='content_title').get_text()
    news_text=latestnews.find('div', class_='article_teaser_body').get_text()
    news_dict = {
        'news_title' : news_title,
        'news_text' : news_text
        }

    # ## JPL Images
    #We can get the data from the JPL space images site with requests.get but the directions ask for splinter/chromedriver
    jpl_url = 'https://www.jpl.nasa.gov'
    jpl_search = '/spaceimages/?search=&category=Mars'
    browser.visit(f'{jpl_url}{jpl_search}')
    time.sleep(3)
    jpl_html = browser.html
    jpl_soup = bs(jpl_html, "html.parser")
    #The featued image is in a section with class 'main_feature'
    #The URL is listed in the article tag's style key, in the format:
    #"background-image: url('/spaceimages/images/wallpaper/PIA19964-1920x1200.jpg');"
    img_style = jpl_soup.find('section', class_='main_feature').article['style']
    img_loc = img_style.find('url') #runs through the text string to find the character position where 'url' is listed
    img_loc += len("url('") #skip past the part of the string that says url('
    img_end = len(img_style) - len("');") #stop before the part of the string that says ');
    img_url = jpl_url + img_style[img_loc:img_end] 
    #img_style[img_loc:img_end] slices out the URL part of the string based on character positions found in the last two lines - then we append the JPL base URL, since the HTML lists a relative URL
    img_title = jpl_soup.find('section', class_='main_feature').article['alt'] #gets the alt text, which appears to always be the title of the image
    img_dict = {
        'img_title' : img_title, 'img_url' : img_url
        }

    # ##Weather
    weather_html = requests.get('https://twitter.com/marswxreport?lang=en') 
    #twitter lets us get the html through requests.get() so let's do that
    twit_soup = bs(weather_html.text, "html.parser") #pass HTML to soup
    weather=twit_soup.find('div', class_='js-tweet-text-container').get_text() #This will get only the latest tweet
    weather=weather.replace('\n','') #strip out newline characters

    # ## Space-facts.com table
    #Only one table is returned
    mfacts_df = pd.read_html('https://space-facts.com/mars/')[0]
    mfacts_df.rename(columns={'0':'Description'})
    #create table HTML with pandas to_html method
    table_html = mfacts_df.to_html(index=False, header=False)
    table_html = str(table_html).replace('\n','') #For unclear reasons, strip declined to remove the \n tags, the replace method was substituted.

    #    ## USGS Astrogeology
    root_url='https://astrogeology.usgs.gov'
    browser.visit(root_url + '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    time.sleep(3)
    usgs_results_html = browser.html
    usgs_results_soup = bs(usgs_results_html, "html.parser")
    hemisphere_image_urls = [] #This will contain the dictionaries requested by the assignment
    linklist = [] #this will contain relative path URLs that will be extracted from the soup
    astrogeo_items = usgs_results_soup.find_all('div', class_='item')
    #Gather up the addresses we need to scrape
    for item in astrogeo_items: 
        linklist.append(item.a['href'])
    #Loop through and get the data from each one, using the function we just made
    for link in linklist:
        browser.visit(root_url + link)
        time.sleep(4)
        lhtml = browser.html
        hemisphere_image_urls.append(usgs_findlink(lhtml))
    

    # ##Return
    scrape_dict = {
        "News" : news_dict,
        "JPL" : img_dict,
        "Weather" : weather,
        "Facts" : table_html,
        "USGS" : hemisphere_image_urls
    }
    return scrape_dict