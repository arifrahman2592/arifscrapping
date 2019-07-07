import getpass
import calendar
import os
import platform
import sys
import urllib.request
import requests

#import emoji untuk emoji
import emoji
#import sys emoji dan sys masih testing saja
import sys

#import library mysql untuk save ke database
import mysql.connector

import unicodedata

#alternative ngambil data dari tag html, blm terpakai sih, saat ini masih pakai xpath aja
from bs4 import BeautifulSoup

#selenium ini yang menjalankan browser
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


total_scrolls = 5
current_scrolls = 0
scroll_time = 5
old_height = 0

# -------------------------------------------------------------
# -------------------------------------------------------------

def check_height():
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height


# -------------------------------------------------------------
# -------------------------------------------------------------

# helper function: used to scroll the page
def scroll():
    global old_height
    current_scrolls = 0

    while (True):
        try:
            if current_scrolls == total_scrolls:
                return

            old_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.05).until(lambda driver: check_height())
            current_scrolls += 1
        except TimeoutException:
            break
    return

def simpan_post_ke_mysql(data_tupple):
    mydb = mysql.connector.connect(host="localhost",user="root",passwd="",database="dataset_facebook")
    mycursor = mydb.cursor()
    sql = "INSERT INTO timeline (nomor, isi_post) VALUES (%s, %s)"
    val = data_tupple
    mycursor.executemany(sql, val)
    mydb.commit()


#ternyata, setelah diteliti skrip ini hanya bisa ngambil yang dari foto
def coba_ambil_isi_status(isi_status):
    status = "eek"
    #jika isi statusnya cuman langsung tag p
    try:
        #status = isi_status
        list_status = isi_status.find_elements_by_xpath(".//p")
        isis = ""
        for x in list_status:
            x = x.text
            #Your data contains characters outside of the Basic Multilingual Plane.
            #Emoji's for example, are outside the BMP, and the window system used by IDLE, Tk, cannot handle such characters.
            isis += ''.join(x.encode('unicode-escape').decode('utf-8'))
            
            #isis = x.encode('unicode-escape').decode('utf-8')
        status = isis
    except:
        pass
    return status

def coba_ambil_isi_komentar(card):
    try:
        list_komen = card.find_elements_by_xpath(".//ul")
        for komen in list_komen:
            print(komen.text)
    except:
        print("gagal mendapatkan komen")
    


def scraping_timeline(id):
    driver.get("https://facebook.com/"+id+"/timeline")
    
    scroll()
    hasil = []
    list_read_more = driver.find_elements_by_xpath("//a[@class='see_more_link']")

    #karena banyak readmore, maka diperulangkan, lalu di expand tiap perulangan
    for item in list_read_more:
        driver.execute_script("arguments[0].click();", item)

    #list komentar yang diringkes oleh facebook, semacam readmore komentar
    list_read_more_komentar = driver.find_elements_by_xpath("//a[@class='_4sxc _42ft']")
    for tiap in list_read_more_komentar:
        driver.execute_script("arguments[0].click();", tiap)

    # wait until title is present
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.userContent")))

    #mendapatkan list tiap cards update status
    list_cards = driver.find_elements_by_xpath("//*[@class='_5pcb _4b0l _2q8l']")
   
    for card in list_cards:
        
        #print(coba_ambil_isi_status(card))
        #coba_ambil_isi_komentar(card)
        #print(post)s

        isi = "";
        paragraf_status = card.find_elements_by_xpath(".//p")
        for paragraf in paragraf_status:
            status = paragraf.text;
            isi += ''.join(status.encode('unicode-escape').decode('utf-8'))
            isi += "\n";

        #disini harusnya simpan ke mysql, namun karena belum mencoba komentar maka di print() saja dulu
        #print(isi)
        
        mydb = mysql.connector.connect(host="localhost",user="root",passwd="",database="dataset_facebook")
        mycursor = mydb.cursor()
        sql = "INSERT INTO timeline (username, isi_post) VALUES (%s, %s)"
        val = (id, isi)
        mycursor.execute(sql, val)
        mydb.commit()
        id_barusan = mycursor.lastrowid

        #setelah status dapat ke print, maka selanjutnya mencari komentar
        list_komentar = card.find_elements_by_xpath(".//div[@data-testid='UFI2Comment/body']")
        for komentar in list_komentar:
            isi_komentar = komentar.text
            isis = ''.join(isi_komentar.encode('unicode-escape').decode('utf-8'))
            #print(isis)
            sql = "INSERT INTO komentar (id_timeline, isi_komentar) VALUES (%s, %s)"
            val = (id_barusan, isis)
            mycursor.execute(sql, val)
            mydb.commit()
    
    
    #print(len(list_cards))
    #print(list_cards)


def login():
    try:
        global driver

        options = Options()

        #  Code to disable notifications pop up of Chrome Browser
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        # options.add_argument("headless")

        try:
            platform_ = platform.system().lower()
            if platform_ in ['linux', 'darwin']:
                driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
            else:
                driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
        except:
            print("Kindly replace the Chrome Web Driver with the latest one from"
                  "http://chromedriver.chromium.org/downloads"
                  "\nYour OS: {}".format(platform_)
                 )
            exit()

        driver.get("https://facebook.com")
        driver.maximize_window()

        # filling the form
        driver.find_element_by_name('email').send_keys("your_username")
        driver.find_element_by_name('pass').send_keys("your_password")

        # clicking on login button
        driver.find_element_by_id('loginbutton').click()

    except Exception as e:
        print("There's some error in log in.")
        print(sys.exc_info()[0])
        exit()

login()
scraping_timeline("someone.user.account")

