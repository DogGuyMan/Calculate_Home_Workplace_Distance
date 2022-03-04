from multiprocessing.connection import wait
from pickle import TRUE
import pandas as pd
import bs4 as beautifulSoup
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.common.alert import Alert

DEBUG_BOOL = TRUE

KAKAO_URL = "https://map.kakao.com/"
START_ADD = "집 이름 넣기"
driver = webdriver.Chrome("C:Program Files (x86)/chromedriver.exe")


def refrashBrowser():
    driver.refresh()
    driver.find_element_by_css_selector("body").click()
    nav_menu = waitElement("/html/body/div[5]/div[1]/div/div/ul/li[2]")
    nav_menu.click()
    driver.find_element_by_css_selector("body").click()


def waitElement(xpath):
    return WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))


def waitElements(xpath):
    element = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    return driver.find_elements_by_xpath(xpath)


def debugPrint(str):
    print(
        f"""

        {str}

        """
    )


def parseKRtime(inputStr):
    retAmount = 0
    if(len(inputStr) < 1):
        return int(999)
    if(inputStr.find("시간") == -1):
        numList = re.findall(r'\d+', inputStr)
        retAmount = int(numList[0])
    else:
        numList = re.findall(r'\d+', inputStr)
        if(len(numList) >= 2):
            retAmount = int(numList[0]) * 60 + int(numList[1])
        else:
            retAmount = int(numList[0]) * 60
    return retAmount

##############################################


dataBase = pd.read_csv('20220212.csv', encoding="UTF-8")
savedFile = pd.read_csv('distFile.csv', encoding="UTF-8")
collectedData = savedFile
driver.get(KAKAO_URL)
refrashBrowser()

#############################################


def SearchDest(i):
    timeList = list()

    try:
        start_pos = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[2]/div[2]/div[1]/div/div[1]/div[2]/form/input[1]")))
    except ElementClickInterceptedException as e:
        driver.find_element_by_xpath(
            "/html/body/div[5]/div[2]/div[2]/div[1]/div/div[1]/div[2]/input").click()
        start_pos = waitElement(
            "/html/body/div[5]/div[2]/div[2]/div[1]/div/div[1]/div[2]/form/input[1]")
    except TimeoutException as e:
        driver.find_element_by_xpath(
            "/html/body/div[5]/div[2]/div[2]/div[1]/div/div[1]/div[2]/input").click()
        start_pos = waitElement(
            "/html/body/div[5]/div[2]/div[2]/div[1]/div/div[1]/div[2]/form/input[1]")

    start_pos.send_keys(i)
    start_pos.send_keys(Keys.ENTER)
    time.sleep(0.5)

    switch_dest = waitElement("/html/body/div[5]/div[2]/div[2]/div[1]/a[2]")
    switch_dest.click()
    time.sleep(0.5)

    start_pos = waitElement(
        "/html/body/div[5]/div[2]/div[2]/div[1]/div/div[1]/div[2]/form/input[1]")
    start_pos.click()

    try:
        start_pos.send_keys(START_ADD)
        time.sleep(0.5)
        start_pos.send_keys(Keys.ENTER)
        time.sleep(0.5)
    except UnexpectedAlertPresentException as e:
        time.sleep(0.5)
        AlertArlam = driver.switch_to_alert()
        AlertArlam.accept()
        AlertArlam.dismiss()
        try:
            time.sleep(1)
            start_pos.send_keys(Keys.ENTER)
        except UnexpectedAlertPresentException as e:
            refrashBrowser()
            return SearchDest(i)

    tarnsPorts_tab = waitElement(
        "/html/body/div[5]/div[2]/div[2]/div[2]/div/a[2]")
    tarnsPorts_tab.click()
    result_data = waitElements(
        "/html/body/div[5]/div[2]/div[2]/div[5]/div[5]/ul")
    time.sleep(2)

    for e in result_data:
        line_parseing = e
        line_data = line_parseing.find_elements_by_css_selector(
            "li > div > span.time")
        for a in line_data:
            timeList.append(parseKRtime(str(a.text)))
        break
    refrashBrowser()

    if(len(timeList) < 1):
        return int(999)
    else:
        return min(timeList)


cnt = 0
print(len(savedFile["거리"]))

for i in dataBase["주소"]:
    if(cnt > len(savedFile["거리"])):
        # https://rfriend.tistory.com/482
        onlineData = pd.DataFrame.from_dict([{"주소": i, "거리": SearchDest(i)}])
        # https://freedata.tistory.com/53
        collectedData = pd.concat(
            [collectedData, onlineData], ignore_index=True)
        pd.DataFrame(data=collectedData, columns=["주소", "거리"]).to_csv(
            "distFile.csv", header=True)
    cnt += 1
