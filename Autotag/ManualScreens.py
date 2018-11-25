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

Provides manual screenings before a loan is considered by the random forest.
"""
import GetAge

def Animals(loan):
    """

    :param loan:
    :return:
    """
    if loan["activity"] == "Butcher Shop" or loan[
        "activity"] == "Food Market" or loan["activity"] == "Veterinary Sales" \
            or loan["activity"] == "General Store":
        return None
    return loan


def Fabrics(loan):
    """

    :param loan:
    :return:
    """
    if loan["activity"] == "Textiles" or "pagne" in loan["use"]:
        return None
    return loan


def Schooling(loan):
    """

    :param loan:
    :return:
    """
    if loan["sector"] == "Education":
        return None
    return loan


def Technology(loan):
    """

    :param loan:
    :return:
    """
    if (loan["partner_id"] == 202 and "solar light" in loan["description"]["texts"]["en"]) or \
                    loan["partner_id"] == 219 \
            or (loan["partner_id"] in [311, 393] and "water filter" in loan[
                "use"]) or "solar" in loan["use"]:
        return None
    return loan


def Trees(loan):
    """

    :param loan:
    :return:
    """
    partner = loan["partner_id"]
    if loan["partner_id"] == 202:
        return None
    if partner == 448:
        for term in ["coffee", "cacao", "cocoa", "bananas"]:
            if term in loan["description"]["texts"]["en"]:
                return None
    return loan


def Parent(loan):
    age = GetAge.GetAge(loan["description"]["texts"]["en"])
    if age and age >= 50:
        return None
    return loan


def EcoFriendly(loan):
    activity = loan["activity"]
    partner_id = loan["partner_id"]
    use = loan["use"]
    if partner_id == 202 or (
                partner_id in [311, 393] and
                    "water filter" in use):
        return None
    if partner_id in [452, 322, 448, 295, 449, 406, 329, 472]:
        return None
    if partner_id == 150 and (activity == "Farming" or
                              activity == "Agriculture"):
        return None
    if activity in ["Used Clothing","Used Shoes", "Bicycle Sales",
                    "Renewable Energy Products", "Recycled Materials",
                    "Recycling"]:
        return None
    if "solar" in use:
        return None
    if partner_id == 448:
        for term in ["coffee", "cacao", "cocoa", "bananas"]:
            if term in loan["description"]["texts"]["en"]:
                return None
    return loan


def BizDurableAsset(loan):
    if loan["sector"] == "Personal Use" or loan["activity"] == "Personal " \
                                                               "Housing " \
                                                               "Expenses":
        return None
    return loan

def RepeatBorrower(loan):
    if loan["partner_id"] in [438, 406]:
        return None
    return loan

def WomanOwnedBiz(loan):
    if loan["sector"] in ["Education",
                       "Housing",
                       "Personal Use", "Health",
                       "Construction"]:
        return None
    men = 0
    women = 0
    for borrower in loan["borrowers"]:
        if borrower["gender"] == "M":
            men += 1
        elif borrower["gender"] == "F":
            women += 1
    if women < men:
        return None
    return loan

def Refugee(loan):
	if loan["location"]["country"] == "Jordan":
		return None
	return loan