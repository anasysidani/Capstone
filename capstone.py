import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import time
from bs4 import BeautifulSoup

import selenium
from selenium import webdriver
import pandas as pd
import numpy as np
from selenium import webdriver  

from time import sleep
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


from io import StringIO

import re
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from pathlib import Path

## File path
here = Path(__file__).resolve()
edgedriver_path = here.parents[0] / 'msedgedriver.exe'

# Function to perform the scraping
def scrape_linkedin(keyword, geo_location):
    # Setup WebDriver (Make sure to specify the path to where your chromedriver is located)
    #options = webdriver.EdgeOptions()
    #options.add_argument("--lang=en-GB")
    #browser = webdriver.Edge( options=edge_options, executable_path=edgedriver_path)

    # Login to LinkedIn
    browser.get('https://www.linkedin.com/uas/login')
    browser.maximize_window()
    sleep(3)
   # finding username section and entering details
    username = browser.find_element("id", "username")
    username.send_keys("anas.y.sidani@gmail.com")  #recommended to use a fake account

# finding password section and entering details
    pword = browser.find_element("id", "password")
    pword.send_keys("Dancing123@")
# Wait for the page to load completely
    time.sleep(3)
 
    browser.find_element("xpath", '//button[@data-litms-control-urn="login-submit"]').click()
    sleep(3)

    # Navigate to the search page with dynamic keyword

    if geo_location == ['UAE']:
        geo_location_code = '"104305776"'
    if geo_location == ['KSA']:
        geo_location_code = '"100459316"'
    if geo_location == ['Qatar']:
        geo_location_code = '"104170880"'
    if geo_location == ['UAE', 'KSA', 'Qatar']:
        geo_location_code = '"104305776"%2C"100459316"%2C"104170880"'
    if geo_location == ['UAE', 'KSA']:
        geo_location_code = '"104305776"%2C"100459316"'
    if geo_location == ['Qatar', 'KSA']:
        geo_location_code = '"104170880"%2C"100459316"'
    if geo_location == ['Qatar', 'UAE']:
        geo_location_code = '"104170880"%2C"104305776"'
    search_url = f'https://www.linkedin.com/search/results/people/?geoUrn=%5B{geo_location_code}%5D&keywords={keyword}&origin=GLOBAL_SEARCH_HEADER'
    browser.get(search_url)
    sleep(3)

    return search_url





def get_links_list(search_url, num_of_pages):

    # Initialize an empty list to store the links
    links_list = []

    # Initialize an emoty list to store the names

    names = []


    # Initialize an empty list to store the companies

    companies = []

    # Initialize an empty list to store the positions

    positions = []

    locations = []

    # Start a loop to scrape multiple pages (adjust the range as needed)
    for page in range(1, num_of_pages+1):

        print(page)
        browser.get(search_url + f"&page={page}")

        print(browser.current_url)
        # Wait for the page to load completely
        time.sleep(15)
        try:
            # Find all the links on the current page and add them to the list
            links = browser.find_elements("xpath",'//*[@class="reusable-search__result-container"]')        
            link_counter = 0  # Initialize a counter for the links

            
            for link in links:
                URL=link.find_element(By.TAG_NAME,'a')
                links_list.append(URL.get_attribute('href'))
                link_counter += 1  # Increment the link counter
                                            
            # Wait for the next page to load (adjust the sleep time as needed)
            time.sleep(20)
        
        except Exception as e:
            print(f"Error on page {page+1}: {e}")

    return links_list

def get_result_df(links_list):


    names = []
    companies = []
    positions = []
    locations = []
    profile_link = []


    for profile in links_list:

        try:

            browser.get(profile)
            time.sleep(5)
            wait = WebDriverWait(browser, 10)

            name = browser.find_element(By.TAG_NAME,'h1')

            company = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Current company:")]')))

            position = browser.find_element('xpath','//*[@class="text-body-medium break-words"]')

            location = browser.find_element('xpath','//*[@class="text-body-small inline t-black--light break-words"]')

            names.append(name.text)
            companies.append(company.text)
            positions.append(position.text)
            locations.append(location.text)
            profile_link.append(profile)

            # Create df
            df = pd.DataFrame({
                'Name': names,
                'Company': companies,
                'Position': positions,
                'Location': locations,
                'Link': profile_link
            })

            # Drop rows where company is nan
            df = df[df['Company'].notna() & df['Company'].str.strip().astype(bool)]



        except:
            pass

    return df




edge_options = Options()
service = Service(edgedriver_path)
browser = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)

st.sidebar.title('Navigation')
page = st.sidebar.selectbox("Select Page", ["LinkedIn Scraper", "Power BI Dashboard"])
# Streamlit interface
if page == "LinkedIn Scraper":
    st.title('LinkedIn Scraper')

    with st.form("my_form"):
        keyword = st.text_input("Enter the job position or keyword:")
        num_of_pages = st.number_input("How many pages do you want to scrape:", min_value=1, value=1, step=1)
        geo_location = st.multiselect(options=['UAE', 'KSA', 'Qatar'], label='Target country:') 

        submitted = st.form_submit_button("Scrape LinkedIn")
        if submitted:
             with st.spinner('Generating Leads...'):
                 search_url = scrape_linkedin(keyword, geo_location)
                 links_list = get_links_list(search_url, int(num_of_pages))
                 result_df = get_result_df(links_list)
             st.dataframe(data=result_df, use_container_width=True, hide_index=True) 

    if submitted:
        st.download_button(label="Download Results as Excel",
                           data=result_df.to_csv().encode('utf-8'),
                           file_name='linkedin_profiles.csv',
                           mime='text/csv') 
        

        
            

elif page == "Power BI Dashboard":
    st.title('Power BI Dashboard')
   
    power_bi_url = 'https://app.powerbi.com/reportEmbed?reportId=a5f61da2-708d-48b2-adc6-f86b37d19cb4&autoAuth=true&ctid=c7ba5b1a-41b6-43e9-a120-6ff654ada137'

    # Embedding code for Power BI dashboard
    html_code = f'<iframe title="Intrvw" width="1140" height="541.25" src="https://app.powerbi.com/reportEmbed?reportId=a5f61da2-708d-48b2-adc6-f86b37d19cb4&autoAuth=true&ctid=c7ba5b1a-41b6-43e9-a120-6ff654ada137" frameborder="0" allowFullScreen="true"></iframe>'
    
    # Display the embedded dashboard
    st.markdown(html_code, unsafe_allow_html=True)
