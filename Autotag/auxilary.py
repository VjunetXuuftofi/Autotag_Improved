"""
Copyright 2016 Thomas Woodside

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

All interactions with the internet happen here. Includes methods to pull data
from the Kiva API as well as identify and tag loans.
"""

import requests
import json
from selenium import webdriver
import time
from collections import defaultdict
from tqdm import tqdm
from datetime import timedelta
from datetime import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import numpy as np
import scipy
import Analysis
import ManualScreens
import pickle
import re
import untag
from bs4 import BeautifulSoup
from GetAge import GetAge
import os

clf = pickle.load(open('clf.pkl', 'rb'))
use_vect = pickle.load(open('use_vect.pkl', 'rb'))
description_vect = pickle.load(open('description_vect.pkl', 'rb'))
categorical_vect = pickle.load(open('categorical_vect.pkl', 'rb'))

machinetags = [
    {
        "Full Name": "#Animals",
        "ID": "11",
        "ManualChecks": ManualScreens.Animals,
        "Threshold": 0.785655245695
    },
    {
        "Full Name": "#Biz Durable Asset",
        "ID": "35",
        "ManualChecks": ManualScreens.BizDurableAsset,
        "Threshold": 0.816439684928
    },
    {
        "Full Name": "#Eco-friendly",
        "ID": "9",
        "ManualChecks": ManualScreens.EcoFriendly,
        "Threshold": 0.5
    },
    {
        "Full Name": "#Elderly",
        "ID": "13",
        "ManualChecks": None,
        "Threshold": 0.912540888232
    },
    {
        "Full Name": "#Fabrics",
        "ID": "26",
        "ManualChecks": ManualScreens.Fabrics,
        "Threshold": 0.645381374726
    },
    {
        "Full Name": "#Female Education",
        "ID": "37",
        "ManualChecks": None,
        "Threshold": 0.929702142234
    },
    {
        "Full Name": "#First Loan",
        "ID": "5",
        "ManualChecks": None,
        "Threshold": 0.722460268135
    },
    {
        "Full Name": "#Health And Sanitation",
        "ID": "27",
        "ManualChecks": None,
        "Threshold": 0.5
    },
    {
        "Full Name": "#Job Creator",
        "ID": "30",
        "ManualChecks": None,
        "Threshold": 0.82675634534
    },
    {
        "Full Name": "#Orphan",
        "ID": "32",
        "ManualChecks": None,
        "Threshold": 0.5
    },
    {
        "Full Name": "#Parent",
        "ID": "16",
        "ManualChecks": ManualScreens.Parent,
        "Threshold": 0.937206068292
    },
    {
        "Full Name": "#Refugee",
        "ID": "29",
        "ManualChecks": ManualScreens.Refugee,
        "Threshold": 0.896162931656
    },
    {
        "Full Name": "#Repair Renew Replace",
        "ID": "39",
        "ManualChecks": None,
        "Threshold": 0.880292568536
    },
    {
        "Full Name": "#Repeat Borrower",
        "ID": "28",
        "ManualChecks": ManualScreens.RepeatBorrower,
        "Threshold": 0.590667669341
    },
    {
        "Full Name": "#Schooling",
        "ID": "18",
        "ManualChecks": ManualScreens.Schooling,
        "Threshold": 0.581964935866
    },
    {
        "Full Name": "#Single",
        "ID": "14",
        "ManualChecks": None,
        "Threshold": 0.977335275615
    },
    {
        "Full Name": "#Single Parent",
        "ID": "17",
        "ManualChecks": ManualScreens.Parent,
        "Threshold": 0.82395091691
    },
    {
        "Full Name": "#Supporting Family",
        "ID": "31",
        "ManualChecks": None,
        "Threshold": 0.903586061182
    },
    {
        "Full Name": "#Sustainable Ag",
        "ID": "8",
        "ManualChecks": None,
        "Threshold": 0.650385213654
    },
    {
        "Full Name": "#Technology",
        "ID": "38",
        "ManualChecks": ManualScreens.Technology,
        "Threshold": 0.5
    },
    {
        "Full Name": "#Trees",
        "ID": "36",
        "ManualChecks": ManualScreens.Trees,
        "Threshold": 0.949196468512
    },
    {
        "Full Name": "#Unique",
        "ID": "13432432",
        "ManualChecks": None,
        "Threshold": 1.3
    },
    {
        "Full Name": "#Vegan",
        "ID": "10",
        "ManualChecks": None,
        "Threshold": 0.980441164315
    },
    {
        "Full Name": "#Widowed",
        "ID": "12",
        "ManualChecks": None,
        "Threshold": 0.870187288396
    },
    {
        "Full Name": "#Woman Owned Biz",
        "ID": "6",
        "ManualChecks": ManualScreens.WomanOwnedBiz,
        "Threshold": 0.920744151572
    },


    ]

def signin(tountag=True):
    """

    :return:
    """
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
    )

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent

    # Initializes a selenium driver and logs into Kiva.
    driver = webdriver.PhantomJS(desired_capabilities=dcap,
                                 service_args=['--ssl-protocol=any'],
                                 executable_path="/usr/local/bin/phantomjs")
    driver.get("https://www.kiva.org/login")
    driver.set_window_size(800, 600)
    email = driver.find_element_by_id("loginForm_email")
    email.send_keys("autotaggingkiva@gmail.com")
    password = driver.find_element_by_id("loginForm_pass")
    password.send_keys(os.environ["KIVA_AUTOTAG_PASSWORD"])
    staysignedin = driver.find_element_by_id("loginForm_persist_login")
    staysignedin.click()
    submit = driver.find_element_by_id("loginForm_submit")
    submit.click()
    time.sleep(2)
    if tountag:
        untag.untag(driver)
    return driver


def kivatag(taglist):
    """
    Uses Selenium to tag loans given in taglist through the Firefox webdriver.
    :param taglist:
    """
    driver = signin()
    if len(taglist) < 1:
        print("No new loans to tag.")
        return None
    print("Commencing Tagging")
    for loan in tqdm(taglist):
        tags = taglist[loan]
        if not tags:
            continue
        print("Tagging loan " + str(loan) + " with " + str(tags))
        driver.get("https://www.kiva.org/lend/" + str(loan))
        for tag in tags:
            if not driver.find_element_by_css_selector("#loan-tag-" +
                                                           tag).get_attribute(
                "checked"):
                time.sleep(2)
                driver.execute_script("document.querySelector('label["
                                      "for=loan-tag-" + tag + "]').click();")
                time.sleep(3)
    print("Done Tagging.")


def getinfo(IDs):
    """
    Pulls and returns data about specific loans from the Kiva API.
    Includes a time sleep to ensure that usage limits aren't exceeded.
    No more than 100 loan ID
    :param IDs:
    :return loans:
    """
    response = requests.get("http://api.kivaws.org/v1/loans/" + IDs + ".json",
                            params={"appid": "com.woodside.autotag"})
    time.sleep(60 / 55)
    loans = json.loads(response.text)["loans"]
    return loans


def determinetags(loans):
    """
    Takes a complete list of loan objects and determines which tags each one should have, storing this in a defaultdict.
    Then, feeds this data to taglist for tagging.
    :param loans:
    """

    print("Determining the tags that each loan should have.")
    tags = defaultdict(set)
    for page in loans:
        for loan in tqdm(page):
            try:
                loanid = loan["id"]
                try:
                    description = loan["description"]["texts"]["en"]
                except KeyError:
                    continue
                use = loan["use"]
                sector = loan["sector"]
                activity = loan["activity"]
                numborrowers = len(loan["borrowers"])
                partner = loan["partner_id"]
                country = loan["location"]["country"]
                this_loan = tags[loanid]
                if partner == 202:
                    this_loan.add("8")
                    this_loan.add("9")
                    if "solar light" in description:
                        this_loan.add("38")
                if GetAge(description) and GetAge(description) >= 50:
                        this_loan.add("13")
                if activity == "Textiles":
                    this_loan.add("26")
                if sector == "Health":
                    this_loan.add("27")
                if sector == "Education":
                    this_loan.add("18")
                if partner == 219:  # Ruma
                    this_loan.add("38")
                if partner in [311, 393] and "water filter" in use:
                    this_loan.add("27")
                    this_loan.add("9")
                    this_loan.add("38")
                if partner in [452, 322]:  # NEW, African Clean Energy
                    this_loan.add("27")
                    this_loan.add("9")
                    this_loan.add("38")
                if partner in [448, 295]:
                    this_loan.add("8")
                    this_loan.add("9")
                if partner == 449:
                    this_loan.add("8")
                    this_loan.add("9")
                    this_loan.add("36")
                    this_loan.add("10")
                if partner == 150 and (activity == "Farming" or
                                                      activity == "Agriculture"):
                    this_loan.add("8")
                    this_loan.add("9")
                if activity == "Used Clothing" or activity == "Used Shoes" or activity == "Bicycle Sales" \
                        or activity == "Renewable Energy Products" or activity == "Recycled Materials" \
                        or activity == "Recycling":
                    this_loan.add("9")
                if "solar" in use:
                    this_loan.add("9")
                    this_loan.add("38")
                if partner == 438 and 2 <= numborrowers <= 9:
                    this_loan.add("28")
                if partner == 406:
                    this_loan.add("27")
                    this_loan.add("9")
                if partner == 288:
                    this_loan.add("10")
                if partner == 329:
                    this_loan.add("9")
                    this_loan.add("35")
                    this_loan.add("27")
                if partner in [379, 305, 458]:
                    this_loan.add("18")
                    this_loan.add("37")
                if "pagne" in use:
                    this_loan.add("26")
                if partner == 448:
                    for term in ["coffee", "cacao", "cocoa", "bananas"]:
                        if term in description:
                            this_loan.add("36")
                            this_loan.add("9")
                            this_loan.add("8")
                            break
                if partner == 472:
                    this_loan.add("9")
                    this_loan.add("8")
                if partner == 406:
                    this_loan.add("27")
                    this_loan.add("28")
                if partner == 245 and sector == "Education":
                    match = re.findall("([0-9]+)%", description)
                    if len(match) > 0:
                        percent = int(match[0][0])
                        if percent >= 25:
                            this_loan.add("37")
                soup = BeautifulSoup(requests.get(
                    "https://www.kiva.org/lend/" + str(loan["id"])).text,
                                     "html.parser")
                if soup.select("p.show-previous-loan-details"):
                    this_loan.add("28")
                if partner == 225:  # Novica
                    continue
                if country == "Jordan":
                    this_loan.add("29")

                try:
                    town = loan['location']['town']
                except KeyError:
                    town = ''

                categorical = [{0: activity, 1: sector, 2: loan['location']['country_code'],
                                3: town, 4: partner}]

                numeric = [[int(loan['loan_amount']), int(loan['terms']['repayment_term'])]]

                borrowers = loan['borrowers']
                if borrowers is not None:
                    female = 0.
                    for borrower in borrowers:
                        female += borrower['gender'] == 'F'
                    numeric[0].append(female/len(borrowers))
                    numeric[0].append(len(borrowers))
                else:
                    continue

                use_transformed = use_vect.transform([use])
                description_transformed = description_vect.transform([description])
                categorical = categorical_vect.transform(categorical).toarray()
                base = np.hstack((categorical, numeric))
                base_sparse = scipy.sparse.csr_matrix(base)
                combined = scipy.sparse.csr_matrix(scipy.sparse.hstack((base_sparse, use_transformed,
                                                                        description_transformed)))
                predictions = clf.predict_proba(combined)

                for i, taginfo in enumerate(machinetags):
                    if not taginfo["ManualChecks"] or taginfo["ManualChecks"](loan):
                        if predictions[i][0][1] > taginfo["Threshold"]:
                            print("ML tag")
                            this_loan.add(taginfo["ID"])
                if "17" and "14" in this_loan:
                    this_loan.remove("14")
                if "17" in this_loan:
                    this_loan.add("16")
            except Exception as e:
                print(e)
                print("Error in determine tags")
    kivatag(tags)


def getquery(form, lasttime=None):
    """
    Takes in an HTTP form and submits this form with the Kiva API. All data
    from the form is returned as a list of dictionaries. Optionally,
    a datetime object can be included to stop getting more information once
    that data is older than the query.
    :param form:
    :param lasttime:
    :return queryresults:
    """
    queryresults = []
    info = requests.get("http://api.kivaws.org/v1/loans/search.json",
                        params=form).text
    info = json.loads(info)
    for i in range(1, int(info["paging"]["pages"])):
        form["page"] = str(i)
        response = requests.get("http://api.kivaws.org/v1/loans/search.json",
                                params=form)
        time.sleep(60 / 55)
        loans = json.loads(response.text)["loans"]
        queryresults.append(loans)
        if lasttime:
            out = False
            for loan in loans:
                postedtime = datetime.fromtimestamp(time.mktime(
                    time.strptime(loan["posted_date"], "%Y-%m-%dT%H:%M:%SZ")))
                if lasttime > postedtime:
                    out = True
                    break
            if out:
                break
    return queryresults

