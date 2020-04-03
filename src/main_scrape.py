# main.py
import csv
import itertools
import requests
import bs4
import re
import pandas as pd
import scrape_utilities
import sys


from datetime import date



def main(file_name):

    list_of_counties = scrape_utilities.read_csv(file_name)
    print('making a dictionary of data')
    dictionary_data = scrape_utilities.make_data_dict(list_of_counties)
    print('writing to dictionary')
    scrape_utilities.write_to_csv(dictionary_data)


if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 2:
        file = args[1]

    main(file)
