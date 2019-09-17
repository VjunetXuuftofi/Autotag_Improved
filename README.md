# Autotag

## Overview:
All loans on Kiva.org are assigned tags that give lenders more search criteria. 
Examples include #SingleParent and #WomanOwnedBusiness. In the past, 100% of tags were administered by a volunteer group.
This system uses a Random Forest, along with a series of hard coded rules, to automatically apply tags to certain loans.
Volunteers can easily remove eroneous tags through a website.

DataPrep.ipynb prepares training data. RandomForestModel.ipynb contains the training code using 
a Random Forest operating on loan descriptions with a bag of words approach. Model.ipynb was an experimental model 
using an LSTM, but it did not perform as well.

The Autotag directory contains the production code.
