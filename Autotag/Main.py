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

Runs all of the implemented systems
"""
import auxilary
import time
from datetime import timedelta
from datetime import datetime

form = """
query getLoans ($offset: Int){
  lend {
    loans (limit: 20, offset: $offset, filters: {distributionModel: field_partner},
           sortBy: newest){
      values {
        id,
        fundraisingDate,
        description,
        use,
        sector {
          name
        },
        activity {
          name
        },
        borrowers {
          id,
          gender
        },
        ... on LoanPartner {
          partnerId
        },
        geocode {
          country {
            name,
            isoCode
          },
          city
        },
        loanAmount,
        terms {
          lenderRepaymentTerm
        },
      }
    }
  }
}
"""

while True:
    try:
        lasttried = open("time.txt")
        for line in lasttried:
            lasttime = datetime.fromtimestamp(
                time.mktime(time.strptime(line, "%d %b %Y %H:%M:%S")))
        lasttried.close()
        print("Getting the initial list of loans.")
        loanlist = auxilary.getquery(form, lasttime)
        loanids = ""
        total = 0
        everyloan = []
        timetowrite = lasttime

        print("Getting the details of all of the loans.")
        for loan in loanlist:
            postedtime = datetime.fromtimestamp(time.mktime(
                time.strptime(loan["fundraisingDate"], "%Y-%m-%dT%H:%M:%SZ")))
            if postedtime - timetowrite > timedelta(microseconds=1):
                timetowrite = postedtime
            if lasttime - postedtime > timedelta(microseconds=1):
                continue
            everyloan.append(loan)
        print("complete1")
        auxilary.determinetags(everyloan)
        lasttried = open("time.txt", "w+")
        lasttried.write(
            time.strftime("%d %b %Y %H:%M:%S", timetowrite.timetuple()))
        lasttried.close()
        print("Waiting a minute...")
        time.sleep(60)
        print("Starting again.")
    except KeyError:
        print("Sorry, API limit eclipsed. Waiting 15 minutes...")
        time.sleep(900)
    except:
        print("Some kind of error. Waiting five minutes.")
        time.sleep(600)
