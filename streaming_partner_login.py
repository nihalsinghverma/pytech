#Required Library
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import datetime as dt
import numpy as np

driver = webdriver.Chrome(ChromeDriverManager().install())

#load data from csv having user_name & password
df = pd.read_csv('streaming_login.csv')
df = df.fillna(0)
df['membership'] = ''
df['expiry'] = ''
df['remark'] = ''

for row in range(0,len(df)):
    usr = df.iloc[row]['user_name']
    pwd = df.iloc[row]['password']
    membership = ""
    expiry =""
    msg = ""
    driver.get('https://www.hotstar.com/in/subscribe/my-account') 
    print ("Hotstar Opend") 
    sleep(1)
    driver.find_element_by_css_selector('div.email-fb-button').click()
    print ("Ready for Login with username :", usr) 
    sleep(1)
    driver.find_element_by_id('emailID').send_keys(usr) 
    driver.find_element_by_css_selector('button.submit-button').click()
    sleep(1)
    try:
        otp_message = driver.find_element_by_css_selector('span.initial-text').text
    except:
        otp_message = ""

    if otp_message == 'Enter the 4-digit code sent to':
        msg = "login_error_otp"
        driver.find_element_by_css_selector('div.back-button').click()
    else:
        driver.find_element_by_id('password').send_keys(pwd)
        driver.find_element_by_css_selector('button.submit-button').click()    
        sleep(2) 
        try:
            msg = driver.find_element_by_css_selector('p.error-txt').text
            if "incorrect" in msg:
                msg = "login_error_password_incorrect"
        except:
            msg = "login_successfull"

    if msg != 'login_successfull':
        driver.get('https://www.hotstar.com/') 
        print ("loggin_failed code:", msg) 
    else:
        print(msg)
        driver.get("https://www.hotstar.com/in/subscribe/my-account/")
        sleep(2)
        membership = driver.find_element_by_css_selector('div.membership-title').text
        membership = membership[:membership.index('for')-1]
        validity   = driver.find_element_by_css_selector('div.membership-desc').text
        expiry = dt.datetime.strptime(validity[12:],'%d %b %Y').date()
        
        print("Membership Type:",membership,"validity:",expiry)
        #Logout the account 
        driver.find_element_by_css_selector('div.security-info').click() 

    df['status']     = np.where((df['user_name'] == usr) & (df['password'] == pwd) , 1, df['status'] ) 
    df['membership'] = np.where((df['user_name'] == usr) & (df['password'] == pwd) , membership, df['membership'])
    df['expiry']     = np.where((df['user_name'] == usr) & (df['password'] == pwd) , expiry, df['expiry']) 
    df['remark']  = np.where((df['user_name'] == usr) & (df['password'] == pwd) , msg, df['remark'])  

p = input("Are you sure want to close?")
driver.close()
