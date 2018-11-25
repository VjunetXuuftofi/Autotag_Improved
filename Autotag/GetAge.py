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

A useful function of get the age of a borrower if it is given in the
description.
"""

import re


def GetAge(description):
    """
    :param description: A description possibly containing the borrower's age.
    :return: The borrower's age as an int, if not found, returns None.
    """
    match = re.findall(
        "([1-9][0-9])( |\-)(years old|years of age|year old|year\-old)",
        description)
    if len(match) == 0:
        match = re.findall(" (is|aged?) ([1-9][0-9])", description)
        if len(match) == 0:
            match = re.findall("(, )([1-9][0-9])(, )", description)
            if len(match) == 0:
                match = re.findall("(born in) (19[0-9][0-9])", description)
                if len(match) == 0:
                    return None
                else:
                    try:
                        return 2016 - int(match[0][1])
                    except:
                        return None
            else:
                try:
                    return int(match[0][1])
                except:
                    return None
        else:
            try:
                return int(match[0][1])
            except:
                return None
    else:
        try:
            return int(match[0][0])
        except:
            return None
