import time
import requests
from bs4 import BeautifulSoup
import re
import pickle
from datetime import datetime
from datetime import timedelta

def untag(driver):
    """
    Uses Selenium to tag loans given in taglist through the Firefox webdriver.
    :param driver:
    """
    toremove = []
    toadd = []
    parsed = BeautifulSoup(requests.get(
        "http://www.thomaswoodside.com/Untag/tagrequests.php").text,
                           "html.parser")
    requestlist = parsed.find("p").text
    requestlist = requestlist[:-8]

    for tountag in re.findall("Untag www\.kiva\.org/lend/[0-9]* #[A-z| ]* \|",
                     requestlist):
        tountag = tountag[:-2]
        split = tountag.split(" ")
        loanid = split[1].split("/")[-1]
        tag = split[2:]
        if type(tag) == list:
            tag = " ".join(tag)
        toremove.append([loanid, tag])
    for totag in re.findall(
            "Tag www\.kiva\.org/lend/[0-9]* #[A-z| ]* \|",
            requestlist):
        totag = totag[:-2]
        split = totag.split(" ")
        loanid = split[1].split("/")[-1]
        tag = split[2:]
        if type(tag) == list:
            tag = " ".join(tag)
        toadd.append([loanid, tag])

    removed = pickle.load(open("removed.pkl", "rb"))
    added = pickle.load(open("added.pkl", "rb"))

    toremovenew = []
    for loan in toremove:
        if loan not in removed:
            toremovenew.append(loan)

    toaddnew = []
    for loan in toadd:
        if loan not in added:
            toaddnew.append(loan)

    toremovedump = []
    toadddump = []
    for loan in toremove:
        toremovedump.append(loan)

    for loan in toadd:
        toadddump.append(loan)
    print(toremovenew)
    print(toaddnew)
    #[loanid,tag]
    mapping = {
        "#Schooling": "18",
        "#Elderly": "13",
        "#Fabrics": "26",
        "#Health and Sanitation": "27",
        "#Technology": "38",
        "#Eco-friendly": "9",
        "#Repeat Borrower": "28",
        "#Animals": "11",
        "#Refugee": "29",
        "#Widowed": "12",
        "#Trees": "36",
        "#Biz Durable Asset": "35",
        "#Repair Renew Replace" : "39",
        "#Single": "14",
        "#Female Education" : "37",
        "#Single Parent" : "17",
        "#First Loan" : "5",
        "#Supporting Family" : "31",
        "#Sustainable Ag" : "8",
        "#Job Creator": "30",
        "#Orphan" : "32",
        "#Parent": "16",
        "#Vegan" : "10",
        "#Woman Owned Biz" : "6"
    }


    if toremovenew:
        for loan in toremove:
            loanid = loan[0]
            tag = loan[1]
            try:
                tag = mapping[tag]
            except KeyError:
                continue
            driver.get("https://www.kiva.org/lend/" + str(loanid))
            if driver.find_element_by_css_selector("#loan-tag-" +
                                                               tag).get_attribute(
                "checked"):
                time.sleep(2)
                driver.execute_script(
                    "document.querySelector('label[for=loan-tag-" + tag + "]').click();")
                time.sleep(2)
    if toaddnew:
        for loan in toadd:
            loanid = loan[0]
            tag = loan[1]
            try:
                tag = mapping[tag]
            except KeyError:
                continue
            driver.get("https://www.kiva.org/lend/" + str(loanid))
            if not driver.find_element_by_css_selector("#loan-tag-" +
                                                               tag).get_attribute(
                "checked"):
                time.sleep(2)
                driver.execute_script(
                    "document.querySelector('label[for=loan-tag-" + tag + "]').click();")
                time.sleep(2)

    pickle.dump(toremovedump, open("removed.pkl", "wb"))
    pickle.dump(toadddump, open("added.pkl", "wb"))