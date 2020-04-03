import csv
import requests
import bs4
import re
import pandas as pd
from datetime import date

# CountyData(name, website)
# .add_soup()
# .make_data(class_name.county())


def write_to_csv(dict_data):
    day_scrape = date.today().strftime('%b_%d_%Y')
    file_name = 'COVID Data Scrape' + day_scrape + '.csv'
    fields = ["Date", "County", "Cases", 'Tests', 'Deaths', 'Recovered']
    with open(file_name, "w", newline="") as f:
            w = csv.DictWriter(f, fields)
            w.writeheader()
            for k in dict_data[day_scrape]:
                dict_data[day_scrape][k].update({'County':k, 'Date': day_scrape})
                w.writerow({field: dict_data[day_scrape][k].get(field) for field in fields})


def make_data_dict(list_of_counties):
    count_dict = {}
    day_scrape = date.today().strftime('%b_%d_%Y')
    count_dict.setdefault(day_scrape)
    count_dict[day_scrape] = {}

    for x in list_of_counties:
        try:
            x = CountyData(x[0], x[1])
            x.add_soup()
            func = 'x.make_data(x.' + str(x.name) +'())'
            exec(func)
            # print("DATA SCRAPED for",x.name,x.scrape)
            count_dict[day_scrape].update( {x.name : {'Cases': x.positive_cases, 'Tests': x.total_tests, \
                              'Deaths' : x.deaths, 'Recovered': x.recovered }})

        except:
            count_dict[day_scrape].update( {x.name : {'Cases': None, 'Tests': None, \
                          'Deaths' : None, 'Recovered': None }})
    return(count_dict)

def read_csv(file, close=False):
        """
            Read csv into list
            @type file: file
            @param file: the read file
            @rtype: list
            @return: the CountyURL object list
        """
        if not file:
            raise Exception('The file is none.')

        county_list = []
        with open(file, 'r') as reader:
            for row in reader:
                if row:
                    row = row.split(',')
                    county = row[0].strip()
                    corona_url = row[1].strip()
                    county_object = (county, corona_url)
                    county_list.append(county_object)

        if close:
            file.close()
        # print(county_list)
        return county_list


def regex_paragraph_1(list_level_1):
    '''
    Makes a 'paragraph' of text from a list in order to perform REGEX..
    Returns a text of combined strings for parsing.
    '''
    paragraph = ''
    for x in list_level_1:
            paragraph += x + ' '
    return(paragraph)


class CountyData(object):
    def __init__(self, county_name, corona_url):
        """
            Init method for County object
            @type county_name: string
            @param county_name: county name
            @type corona_url: string
            @param corona_url: County's Public Health CoronaVirus url

            Other attributes
            @type soup: BeautifulSoup Object
            @parameter soup: html_Code of url
            @type scrape: function
            @parameter scrape: unique function that scrapes corona data of corona url

            @rtype:  dictionary
            @return: Dictionary of COVID_19 cases, deaths, tests administered, number of recovered persons
        """
        self.county_name = county_name
        self.corona_url = corona_url
        self.soup = None
        self.scrape = None
        self.name = self.make_function_name()
        self.positive_cases = None
        self.total_tests = None
        self.deaths = None
        self.recovered = None
        self.date_of_scrape = date.today().strftime('%b_%d_%Y')


    def add_soup(self):
        self.soup = self.run_bs4()
        return("SOUP ADDED")

    def make_function_name(self):
        name = self.county_name.lower()
        self.name = name.replace(" ", '_')

        return(self.name)

    def run_bs4(self):
        '''
        Function runs beautifulSoup to get a fresh scrape of a given link.
        Parameters : a url
        Return: a Beautiful Soup object ready to be parsed
        '''
        link = self.corona_url

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko)\
                      Chrome/80.0.3987.122 Safari/537.36'
        headers = {'User-Agent': user_agent}
        try:
            page = requests.get(link, headers=headers)

        # If a request error, exit
        except requests.exceptions.RequestException as e:
            print("Error at ", e)
            exit()

        self.soup = bs4.BeautifulSoup(page.content, "html.parser")

        return(self.soup)

    def make_data(self, tuple_):
        self.scrape = tuple_
        self.positive_cases = self.scrape[0]
        self.total_tests = self.scrape[2]
        self.deaths = self.scrape[1]
        self.recovered = self.scrape[3]

        return(self.positive_cases,self.total_tests, self.deaths,self.recovered  )


   # HERE IS A LIST OF COUNTY SPECIFIC SCRAPES


    def berkeley(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''

        print("THIS CiTY IS ALSO OFTEN INCLUDED IN ALAMEDA COUNTY COUNTS. \
           BEWARE OVERCOUNTING")
        for x in self.soup.find_all('p'):
            if 'cases' in str(x):
                try:
                    text=x.find('strong').find(text=True)
                except:
                    pass

        return((text, 0,0,0))

    def alameda(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''

    # REQUIRES A DOWNLOAD FIRST-->SAVE AS A MHTML FILE AND LOAD VIA PATHFILE
    # Find Positive Cases
        cases = re.findall(r'Positive Cases: <em>([0-9]+)', self.soup)[0]

    # Find No. of Deaths
        deaths = re.findall(r'Deaths: <em>([0-9]+)', self.soup)[0]

        return((cases, deaths,0,0))

    def amador(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        # SPAN TAG
        # PARAGRAPH
        paragraph = ''
        for x in self.soup.find_all('span'):
            for y in x.find_all(text=True):
                paragraph +=  y.strip()+ ' '

        # regex to clean string
        cases = re.findall(r'Cases As of [A-Z][a-z]+ [0-9]+, [0-9]+: ([0-9]+)', paragraph)[0]

        return((cases, 0,0,0))

    def butte(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        # TD TOTAL  NO TESTS OR RECOVERED
        paragraph = ''
        for no, x in enumerate(self.soup.find_all('td')):
            if 'Total' in str(x):
                paragraph += self.soup.find_all('td')[no+1].find(text=True).strip() + ' '

        cases = re.findall(r'([0-9]+) ([0-9]+)', paragraph)[0][0]
        deaths = re.findall(r'([0-9]+) ([0-9]+)', paragraph)[0][1]
        return((cases, deaths,0,0))

    def calaveras(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''

        for x in self.soup.find_all('span', class_= 'Head', id="dnn_ctr8879_dnnTITLE_titleLabel"):
            results = x.contents[0]

        case = re.findall(r'Number of confirmed cases in Calaveras County: ([0-9]+)', results)[0]

        return((case, 0,0,0))

    def colusa(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''

        for x in self.soup.find_all('div', class_="fr-view"):
            for row in x.find_all('strong'):
                # print(row)
                if 'Cases' in str(row):
                    cases = row.find(text=True)

        cases = re.findall(r'Cases: ([0-9]+)', cases)[0]

        return((cases, 0,0,0))

    def contra_costa(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''

        paragraph = ' '
        for x in self.soup.find_all('div', class_="txtNew"):
            for y in x.find_all('h1'):
                paragraph += y.find(text=True) + ' '

        deaths = re.findall(r'DEATHS ([0-9]+)', paragraph)[0]
        cases = re.findall(r'TOTAL CASES ([0-9]+)', paragraph)[0]


        return((cases, deaths, 0,0))


    def del_norte(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        paragraph = ''
        for x in self.soup.find_all('div'):
            for z in x.find_all(text=True):
            # print(z.strip())
                paragraph += z.replace('\xa0', '').strip() + ' '
        # print(paragraph)
        tests = re.findall(r'Total Number of Tests Administered               ([0-9]+)', paragraph)[0]
        cases = re.findall(r'Number of Positive COVID-19 Cases               ([0-9]+)', paragraph)[0]
        # print(tests, cases)
        return((cases, 0,tests,0))

    def el_dorado(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        paragraph_ = ''
        for x in self.soup.find_all('table'):
            text = x.find_all(text=True)
            for no, y in enumerate(text):
                paragraph_ += y.strip().replace('\n', '').replace('\u200b', '') +' '
            # print(paragraph_)

        cases = re.findall(r'Positive Tests ([0-9]+)', paragraph_)[0]
        # print(cases)
        deaths =re.findall(r'Deaths ([0-9]+)', paragraph_)[0]
        # print(deaths)
        cases = cases
        tests = re.findall(r'Number of Tests\*\*  ([0-9]+)', paragraph_)[0]
        # print(tests)

        return((cases, deaths, tests,0))

    def fresno(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        paragraph_case = ''
        paragraph_deaths = ''
        paragraph_tests = ''
        for no, x in enumerate(self.soup.find_all('li')):
            text = x.find(text=True)
            # print(text)
            if 'cases' in text:
                paragraph_case += self.soup.find_all('li')[no+1].find(text=True) + ' '
                paragraph_case += self.soup.find_all('li')[no+2].find(text=True) + ' '
                paragraph_case += self.soup.find_all('li')[no+3].find(text=True) + ' '
            if 'deaths' in text:
                paragraph_deaths += text + ' '
            if 'Tests' in text:
                paragraph_tests += text + ' '

        paragraph_tests = paragraph_tests.replace(',', '')
        # print(paragraph_case,paragraph_deaths,paragraph_tests)

        cases = re.findall(r'([0-9]+) \(Travel-Related\) ([0-9]+) \(Person-to-Person\) ([0-9]+) \(Community-Spread\)',\
                   paragraph_case)
        tests = re.findall(r'([0-9]+) \(Tests',paragraph_tests)[0]
        cases = sum([int(x) for x in cases[0]])

        return((cases, 0,tests,0))

    def glenn(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        paragraph = ''
        for x in soups[11].find_all('strong'):
            for y in x.find_all(text=True):
                paragraph += y.strip() + ' '
        cases = re.findall(r'COVID-19 Cases ([0-9]+)', paragraph)[0]
        tests = 32
        return((cases, 0, tests, 0))

    def humboldt(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        positive = []
        for x in soups[12].find_all('div', class_="outer col col24 first last"):
            # print(x)
            for y in x.find_all('div'):
                text =y.find(text=True)
                # print(text)
                positive.append(str(text).replace('\n', "").replace('\t', "").replace('\r', ""))
        paragraph = regex_paragraph_1(positive)
        cases = re.findall(r'Total [new]* positive cases [confirmed]* on [A-Z][a-z]+ [0-9]+: ([0-9]+) |Total positive cases [confirmed]* on [A-Z][a-z]+ [ ]*[0-9]+: [ ]*([0-9]+)', paragraph)
        tot = len(cases)
        for x,y in zip(cases[:tot/2], cases[tot/2:]):
            no_case += int(x[0]) + int(y[1])


        return((no_cases + 10, 0,848,0))

    def imperial(self):
        '''
        Function that uniquely scrapes Covid Info off that county or city's health page.
        Returns ((no. positive cases, no. deaths, total tests administered, recovered cases)
        The '0' without a variable name meant information was not found on website (YET...).
        '''
        texts=[]
        paragraph = ''
        for x in self.soup.find_all('div', class_="panel-body"):
            # print(x)
            for y in x.find_all('td'):
                text = y.find(text=True)
                if text:
                    paragraph += text.replace('\xa0', "") +' '

        cases = re.findall(r'\(Confirmed Cases\) ([0-9]+)', paragraph)[0]
        tests = re.findall(r'Total Tested ([0-9]+)', paragraph)[0]

        return((cases, 0, tests, 0))

    def inyo(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for no, x in enumerate(soups[14].find_all('table')):
            for y in x.find_all('li'):
                for z in y.find_all(text=True):
                    # print(z)
                    paragraph += str(z).strip() + ' '

        mono = ''
        for no, x in enumerate(soups[14].find_all('p')):
            for y in x.find_all('span'):
                for z in y.find_all(text=True):
                    mono += z.strip() + ' '

        paragraph = paragraph.replace("\n", "").replace("\xa0", "").replace("\t", "")

        deaths= re.findall(r'([0-9]+) deaths', paragraph)[0]
        cases= re.findall(r'([0-9]+) confirmed', paragraph)[0]
        tests = re.findall(r'Tests Administered: ([0-9]+)', paragraph)[0]

        return((cases, death, tests,0))

    def kern(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        # return ("VERIFY, website blocks scrapes, has an image or has no info")

    def kings(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        paragraph = ''

        for x in self.soup.find_all('b'):
            # print(x)
            for y in x.find_all('h3'):
                # print(x)
                paragraph += str(y) + ' '

        # print(paragraph)
        cases = re.findall(r'Confirmed Cases: ([0-9]+)', paragraph)[0]
        tests = re.findall(r'Samples Collected by Health Dept.: ([0-9]+)', paragraph)[0]

        return((cases, 0, tests, 0))

    def lake(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        # return("VERIFY, website blocks scrapes, has an image or has no info")

    def lassen(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return("VERIFY, website blocks scrapes, has an image or has no info")

    def long_beach(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        self.corona_url = 'http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'
        self.soup = self.run_bs4()

        paragraph = ''
        for x in self.soup.find_all('table'):
            for y in x.find_all(text=True):
                paragraph += y.strip().replace('\xa0', '') +' '



        results= re.findall(r'- Long Beach  ([0-9]+)', paragraph)
        # print(results)
        cases = results[0]
        deaths = results[1]
        return((cases, deaths, 0, 0))


    def los_angeles(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # print("LA_COUNTY COUNTS CAN INCLUDE PASADENA AND LONG BEACH COUNTIES. \
               # DOUBLE CHECK COUNT METHODS. BEWARE OVERCOUNTING. THIS COUNT\
               # DOES NOT INCLUDE THOSE TWO COUNTIES")
        paragraph = ''
        for x in self.soup.find_all('table'):
            # print(x.find_all('th'))
            for te, num in zip(x.find_all('th'), x.find_all('td')):
                # print(te.find(text=True), num.find(text=True))
                paragraph += num.find(text=True).strip().replace('\xa0', '') +' '
                paragraph += te.find(text=True).strip().replace('\xa0', '') + ' '


        cases= re.findall(r'Total Cases ([0-9]+)*', paragraph)[0]
        deaths = re.findall(r'Deaths  \- Los Angeles County \(excl.LBandPas\) ([0-9]+)', paragraph)[0]

        return((cases, deaths, 0, 0))


    def madera(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        info = []
        for x in self.soup.find_all('div', id='widget_685_4225_1649'):
            text = x.find_all('td')
            for y in x.find_all('td'):
                try:
                    if int(y.find(text=True)):
                        info.append(int(str(y.find(text=True)).replace('\xa0', "")))
                except:
                    pass

        cases = int(max(info))

        return((cases, 0,0,0))



    def marin(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # print('at MARIN')
        paragraph = ''
        for x in self.soup.find_all('table', class_="table table-striped table-hover cols-1"):
            for y in x.find_all('tbody'):
                for no, z in enumerate(y.find_all(text=True)):
                    # print(z)
                    if len(z) > 1:
                        paragraph += z.strip()+ ' '

        # print(paragraph)
        # 0-18 years 4 19-34 years 12 35-49 Years 26 50-64 Years 35 65 years or older 31 Total Cases 108
        cases = re.findall(r'Total Cases ([0-9]+)', paragraph)[0]


        return((cases, 0,0,0))


    def mariposa(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('div', class_="fr-view"):
            for y in x.find_all('strong'):
                for z in y.find_all(text=True):
                    paragraph += z.strip().replace('\xa0', "")+ ' '

        # gets all text into a paragraph for regex

        # print(paragraph)
        # of 04/02/2020 at 9:00 am. Total Tested:   51
        # Total Pending:  10 Total Negative: 41 Total Positive: 0 Total Deaths: 0

        # finds number of positive cases
        cases = re.findall(r'Total Positive: ([0-9]+)', paragraph)[0]
        tests = re.findall(r'Total Tested:   ([0-9]+)', paragraph)[0]
        deaths = re.findall(r'Total Deaths: ([0-9]+)', paragraph)[0]


        return((cases, tests, deaths, 0))

    def mendocino(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # print("AT MENDICINO")
        paragraph =  ''
        for x in self.soup.find_all('div', id="widget_313_6901_4337"):
            for y in x.find_all('li'):
                text = y.find_all(text=True)
                # print(text)
                for z in text:
                    paragraph += z.strip() +' '
        # print(paragraph)
        pos = re.findall(r'Positive tests: ([0-9]+)', paragraph)[0]
        tests = re.findall(r'Total tests: ([0-9]+)', paragraph)[0]

        return((pos, tests, 0, 0))


    def merced(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        info={}
        for x in self.soup.find_all('table'):
            for title, no in zip(x.find_all('th'), x.find_all('td')):
                info[title.find(text=True)] = int(no.find(text=True))

        # Dictionary info {'Tests': 46, 'Cases': 1, 'Deaths': 0, 'Recoveries': 0}
        return((info['Cases'], info['Deaths'], info['Tests'], info['Recoveries']))


    def modoc(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return('VERIFY. Website blocks scrapes, has an image, or has no info.')

    def mono(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        self.corona_url = 'https://www.inyocounty.us/covid-19/local-updates'
        self.soup = self.run_bs4()
        mono = ''
        for no, x in enumerate(self.soup.find_all('p')):
            for y in x.find_all('span'):
                for z in y.find_all(text=True):
                    mono += z.strip() + ' '
        mono_results = re.findall(r'Mono County Cases: ([0-9]+) confirmed COVID-19 case \| ([0-9]+) deaths', mono)
        deaths= mono_results[0][1]
        cases= mono_results[0][0]

        return((cases, deaths, 0,0))

    def monterey(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for no_1, x in enumerate(self.soup.find_all('div')):
            for no, y in enumerate(x.find_all('p')):
                text = y.find_all(text=True)
                for z in text:
                    if len(z) > 0:
                        paragraph += str(z.strip()) + ' '

        try:
            cases = re.findall(r'Total ([0-9]+) 100', paragraph)[0]
            tests = re.findall(r'Number of tests completed: ([0-9]+)', paragraph)[0]
            deaths = re.findall(r'Fatalities ([0-9]+)', paragraph)[0]

        except:
            cases = re.findall(r'Total ([0-9]+) 100', paragraph)[0]
            tests = re.findall(r' completado: ([0-9]+)', paragraph)[0]
            deaths = re.findall(r' mortales ([0-9]+)', paragraph)[0]

        return((cases, deaths,tests, 0))

    def napa(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        # return("DOWNLOAD WEBSITE FIRST. THEN BEAUTIFUL SOUP")
        paragraph = ''
        for x in self.soup.find_all('table'):
            for y in x.find_all('tr'):
                for z in y.find_all('td'):
                    for a in z.find_all(text=True):
                        string_ = str(a.strip()).replace('\n','').replace('=20','')
                        paragraph += string_.replace('         ', '')

        info_cases = re.findall(r'Napa County Residents   ([0-9]+)   ([0-9]+)   ([0-9]+)', paragraph)
        cases = info_cases[0][0]
        deaths = info_cases[0][1]
        recovered = info_cases[0][2]

        tests = re.findall(r'TOTAL   ([0-9]+)', paragraph)
        tests = tests[0]

        return((cases, deaths, tests, recovered))

    def nevada(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return("DOWNLOAD WEBSITE FIRST. THEN BEAUTIFUL SOUP")

        paragraph = ''
        for x in self.soup.find_all('table'):
            for y in x.find_all('tr'):
                for z in y.find_all('td'):
                    for a in z.find_all(text=True):
                        paragraph = str(a.strip())


        cases = re.findall(r'Positive Tests Travel-related ([0-9]+) Community \
                             Acquired ([0-9]+) Known Person-to-person ([0-9]+) \
                             Mode of Transmission Under Investigation \
                             ([0-9]+)',paragraph)

        deaths= re.findall(r'Deaths ([0-9]+)', paragraph)
        deaths = deaths[0]


        return((cases, deaths, 0, 0))



    def orange(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('div', class_="col-md-6 col-sm-6 col-xs-12"):
            for y, z in zip(x.find_all('h2'), x.find_all('h1')):
                paragraph += y.find(text=True) +' ' + z.find(text=True) +' '

        cases = re.findall(r'Cumulative Cases to Date ([0-9]+)', paragraph)[0]
        deaths = re.findall(r'Cumulative Deaths to Date ([0-9]+)', paragraph)[0]
        # tests = info['test']

        return((cases, deaths, 0, 0))




    def placer(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''

        for x in self.soup.find_all('table'):
            for no, y in enumerate(x.find_all('td')):

                paragraph += y.find(text=True) + ' '
        # print(paragraph)

        cases = re.findall(r'Lab Confirmed Cases \(includes those who have died\) ([0-9]+)', paragraph)[0]
        deaths = re.findall(r'Deaths ([0-9]+)', paragraph)[0]

        return((cases, deaths, 0,0))


    def pasadena(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        info={}
        key=[]
        for x in self.soup.find_all('aside'):
            table = x.find('table')
            rows = table.find_all('tr')

            for no, y in enumerate(rows):
                count = 0
                for a in y.find_all('th'):
                    key.append(a.find(text=True))

                for b in y.find_all('td'):
                    info[key[count]]=b.find(text=True)
                    count+=1
        # Dictionary --> {'Cases': '9', 'Deaths': '0'}
        return((int(info['Cases']), int(info['Deaths']), 0, 0))

    def plumas(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph =''
        for x in self.soup.find_all('table'):
            y = x.find('tbody')
            # print(y)
            for no, a in enumerate(y.find_all('td')):
                text = a.find(text=True)
                if text:
                    paragraph += y.find_all('td')[no].find(text=True) + ' '
        # print(paragraph)
        # COVID-19 DASHBOARD DATA LAST UPDATED: Wednesday, April 1, 2020, at 5:00 PM Disclaimer:
        # Data may not be updated on Saturdays and Sundays.
        # Positive Test Results 1 People Tested 64 Pending Test Results 16 Negative Test Results 47
        # State of CA 6,932 150 U.S. 186,101  3,603
        results = re.findall(r'Positive Test Results ([0-9]+) People Tested ([0-9]+)', paragraph)
        cases = results[0][0]
        tests = results[0][1]

        return((cases, 0, tests, 0))

    def riverside(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return('VERIFY. Website blocks scrapes, has an image, or has no info.')
        info = []
        for x in self.soup.find_all('div', class_="dc_content"):
            for y in x.find_all('p'):
                if 'strong' in str(y):
                    for no, z in enumerate(y.find_all(text=True)):
                        if len(z) > 1:
                            info.append(z.strip())

        cases = re.search(r'[0-9]+', info[1]).group()
        deaths = re.search(r'[0-9]+', info[9]).group()
        return((cases, deaths, 0,0))

    def san_benito(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return('VERIFY. Website blocks scrapes, has an image, or has no info.')

    def san_bernardino(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('div', class_= "et_pb_text_inner"):
            for z, y in zip(x.find_all('h2'), x.find_all('span')):
                paragraph += z.find(text=True) + ' '+ y.find(text=True) + ' '
        # print(paragraph)
        # COVID-19 CASES IN 254 COVID-19 ASSOCIATED DEATHS IN 6
        # Dictionary --> {'COVID-19 CASES IN': '54', 'COVID-19 ASSOCIATED DEATH IN': '2'}
        cases = re.findall(r'CASES IN ([0-9]+)', paragraph)[0]
        deaths = re.findall(r'DEATHS IN ([0-9]+)', paragraph)[0]

        return((cases, deaths, 0, 0))

    def san_diego(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('table'):
            for no_1, y in enumerate(x.find_all('tr')):
                for z in  y.find_all('td'):
                    paragraph += z.find(text=True).strip().replace('\xa0',\
                                     '').replace('\n', '') + ' '

        cases= re.findall(r'Residents Total Positives ([0-9]+)', paragraph)[0]
        deaths= re.findall(r'Deaths ([0-9]+)', paragraph)[0]

        return((cases, deaths, 0,0))




    def san_francisco(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('div', class_='box2'):
            for y in x.find_all('p'):
                paragraph += y.find(text=True) +' '

        cases = re.findall(r'Total Positive Cases: ([0-9]+)', paragraph)[0]
        deaths = re.findall(r'Deaths: ([0-9]+)', paragraph)[0]

        return((cases, deaths, 0,0))

    def san_joaquin(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('tr'):
            for y in x.find_all('strong'):
                paragraph += y.find(text=True) + ' '

        results = re.findall(r'Confirmed COVID-19 Cases ([0-9]+) ([0-9]+)', paragraph)

        cases= results[0][0]
        deaths = results[0][1]
        return((cases, deaths, 0, 0))


    def san_luis_obispo(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return('DATA IS AVAILABLE AS A DOWNLOAD. ONCE CSV IS DOWNLOADED PROCEEED')
        path = 'https://e.infogram.com/f6d9f731-5772-4da5-b149-5e42cc1c3b89?\
                parent_url=https%3A%2F%2Fwww.emergencyslo.org%2Fen%2F\
                positive-case-details.aspx&src=embed#'
        slo = pd.read_csv('../../Downloads/data.csv', header=None)
        slo.drop(columns=[2], inplace=True)

        # Clean the dataframe using regex
        for no, y in enumerate(slo.loc[:, 1]):
            slo.loc[no, 1] = re.search(r'>[\w ]+', y).group()
            slo.loc[no, 1] = re.search(r'[\w ]+', y).group()
        for no, y in enumerate(slo.loc[:, 0]):
            slo.loc[no, 0] = re.search(r'>[0-9]+', y).group()
            slo.loc[no, 0] = re.search(r'[0-9]+', y).group()

        # access the numbers
        cases = slo.loc[0,0]
        deaths= slo.loc[5][0]
        recovered= slo.loc[2][0]

        return((cases, death, 0, recovered))


    def san_mateo(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        return("SEE WEBSITE FOR DASHBOARD")
        info = []
        for x in self.soup.find_all('table'):
            for y in x.find_all('td'):
                info.append(y.find(text=True))

        # info = ['\n', '165', 'Deaths', '5']
        cases = info[1]
        deaths = info[-1]

        return((cases, deaths, 0,0))

    def san_barbara(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        return('DOWNLOAD WEBPAGE AS A MHTML FILE AND LOAD AS SOUP')
        paragraph = ''
        # Finds text and puts it in paragraph form for REGEX
        for x in self.soup.find_all('div'):
            for y,z in zip(x.find_all('td'), x.find_all('li')):
                nums = y.find_all(text=True)
                text = z.find_all(text=True)
                paragraph += nums + ' '
                if 'As of' in str(text):
                    paragraph += text + ' '

        # Regex Magic --> COULD ORGANIZE INTO TIME SERIES WITH DATES
        # positive cases
        pos = re.findall(r'# Positive Results ([0-9]+)', paragraph)[0]

        # recovered info
        rec = re.findall(r'Recovered ([0-9]+)', paragraph)[0]

        # tested info
        tests = re.findall(r'Total Tested ([0-9]+)', paragraph)[0]


        return((pos, 0, tests, rec))

    def santa_clara(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return("SEE WEBSITE FOR DASHBOARD")
        paragraph = ''
        for x in self.soup.find_all('table'):
            for no, y in enumerate(x.find_all('td')):
                for z in y.find_all(text=True):
                    paragraph += z.replace('\n', '') + ' '

        # result string
        info = re.findall(r"Total Confirmed Cases Hospitalized Deaths ([0-9]+) ([0-9]+) ([0-9]+)", paragraph)
        # positive cases
        cases = info[0][0]

        # death info
        deaths = info[0][1]

        return((cases, death, 0,0))



    def santa_cruz(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('div', class_='Normal'):
            for y in x.find_all('td'):
                for z in y.find_all('p'):
                    paragraph += z.find(text=True).replace('\xa0', "") + ' '
        try:
            results = re.findall(r'Cases/Deathsas of 0[0-9]/[0-9]+/20 [0-9]+:[0-9]+[ap]m ([0-9]+)/ ([0-9]+)', paragraph)
        except:
            results = re.findall(r'Cases/Deathsas of 0[0-9]/[0-9]+/20 [0-9]+:[0-9]+[ap]m ([0-9]+) / ([0-9]+)', paragraph)

        cases = results[0][0]
        deaths=results[0][1]

        return((cases, deaths, 0, 0))


    def shasta(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('table'):
            for y in x.find_all('td'):
                paragraph += y.find(text=True) + ' '
        # Combines text into paragraph form to be parsed by regex
        # print(paragraph)
        # Total Confirmed Cases 7 People who tested negative 236
        # Travel Related 4 Person-to-Person Spread  2 Community Acquired  1 Deaths 1

        # REGEX
        cases = re.findall(r'Total Confirmed Cases ([0-9]+)', paragraph)[0]
        deaths =  re.findall(r'Deaths ([0-9]+)', paragraph)[0]

        return((cases, deaths, 0,0))


    def sierra(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        info = []
        for x in self.soup.find_all('table'):
            for y in x.find_all('tr'):
                for z in y.find_all(text=True):
                    if '\n' not in z:
                        info.append(z)
        # Combines text into paragraph form to be parsed by regex
        paragraph = regex_paragraph_1(info)

        # REGEX
        cases = re.search(r'# of Positive COVID-19 Cases [0-9]+', paragraph).group()
        cases = re.search(r' [0-9]+', cases).group()
        tests =  re.search(r'# of Test Administered [0-9]+', paragraph).group()
        tests =  re.search(r'[0-9]+', tests).group()

        return((cases, 0, tests, 0))


    def siskiyou(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return("DOWNLOAD WEBSITE AS A MHTML FILE AND THEN BEAUTIFUL SOUP DOWNLOAD.")
        info = []
        for x in self.soup.find_all('table'):
            for y in x.find_all('td'):
                for z in y.find_all(text=True):
                    if z != '\n':
                        info.append(z)

        # Put all strings into paragraph form for regex parsing
        paragraph = regex_paragraph_1(info[:12])

        # Regex Expressions
        cases = re.search(r'[0-9]+ POSITIVE', paragraph).group()
        cases = re.search(r'[0-9]+', cases).group()
        tests =  re.search(r'[0-9]+ TOTAL TESTS RECEIVED ', paragraph).group()
        tests =  re.search(r'[0-9]+', tests).group()
        deaths =  re.search(r'[0-9]+ DEATHS', paragraph).group()
        deaths =  re.search(r'[0-9]+', deaths).group()

        return((cases, deaths, tests, 0))



    def solano(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        # return('VISUALLY VERIFY.INFO IS IN AN IMAGE FILE.')


    def sonoma(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # return("DOWNLOAD WEBSITE AS A MHTML FILE AND THEN BEAUTIFUL SOUP DOWNLOAD.")

        info=[]
        for x in self.soup.find_all('div'):
            for y in x.find_all('p'):
                for z in y.find_all(text=True):
                    if len(z) >0:
                        info.append(z)

        # Change strings to paragraph form
        paragraph = regex_paragraph_1(info[1:11])

        # Regex expressions to find data
        cases = re.search(r'Total Cases [0-9]+', paragraph).group()
        cases = re.search(r'[0-9]+', cases).group()
        tests =  re.search(r'Tests [0-9]+', paragraph).group()
        tests =  re.search(r'[0-9]+', tests).group()
        deaths =  re.search(r'Deaths [0-9]+', paragraph).group()
        deaths =  re.search(r'[0-9]+', deaths).group()
        recovered = re.search(r'Recovered [0-9]+', paragraph).group()
        recovered = re.search(r'[0-9]+', recovered).group()

        return((cases, deaths, tests, recovered))


    def stanislaus(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        paragraph = ''
        for z in self.soup.find_all('p'):
            for b in z.find_all('strong'):
                if 'Cases' in str(b):
                    paragraph += (b.find(text=True))+ " "
                if 'Tests' in str(b):
                    paragraph += (b.find(text=True))+ " "
                if 'Deaths' in str(b):
                    paragraph += (b.find(text=True))+ " "

        for x in self.soup.find_all('div', class_='counter'):
            for y in x.find_all(text=True):
                # print(y.strip())
                if len(y) >0:
                    paragraph += y.strip()+ " "
        # print(paragraph)
        # Positive Cases Negative Tests Related Deaths  44   1279   0
        results = re.findall(r'Positive Cases Negative Tests Related Deaths  ([0-9]+)   ([0-9]+)   ([0-9])+', paragraph)
        cases = results[0][0]
        tests = int(results[0][1]) + int(results[0][0])
        deaths = results[0][2]

        return((cases, deaths, tests, 0))


    def sutter(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # print("SUTTER AND YUBA ARE REPORTED TOGETHER SOMETIMES. THIS IS SUTTER ONLY")
        paragraph = ' '
        for x in self.soup.find_all('table'):
            for y in x.find_all(text=True):
                y = y.replace('\n', "")
                if len(y) > 0:
                    paragraph += y.replace('\n', "") + ' '

        for x in self.soup.find_all('p'):
            if 'tests' in str(x):
                paragraph += x.find(text=True) + ' '

        tests = re.findall(r'reported ([0-9]+) COVID-19 tests', paragraph)
        tests = tests[0]

        results = re.findall(r'Confirmed ([0-9]+) Deaths ([0-9]+)', paragraph)
        cases = results[0][0]
        deaths = results[0][1]

        return((cases, deaths,tests,0))


    def tehama(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        return('VISUALLY VERIFY. Website blocks scrapes, has an image, or has no info.')

    def trinity(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
    def tulare(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
    def tuolumne(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        paragraph = ''
        for x in self.soup.find_all('table'):
            # print(x)
            for y, z in zip(x.find_all('th'),  x.find_all('td')):
                for a in z.find_all(text=True):
                    paragraph += a.strip() +' '

                for b in y.find_all(text=True):
                    paragraph += b.strip() +' '


        cases = re.findall(r'([0-9]+) TOTAL POSITIVE', paragraph)[0]
        tests =  re.findall(r'([0-9]+)  TOTAL TESTED', paragraph)[0]
        deaths =  re.findall(r'([0-9]+) TOTAL DEATHS', paragraph)[0]

        return((cases, deaths,tests,0))

    def ventura(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        info = []
        for x in soups[57].find_all('table'):
            for y in x.find_all('td'):
                info.append(y.find(text=True).replace(',', ''))

        paragraph = regex_paragraph_1(info)
        cases = re.findall(r'TOTAL CASES ([0-9]+)', paragraph)[0]
        deaths = re.findall(r'DEATHS ([0-9]+)', paragraph)[0]
        recovered = re.findall(r'Recovered Cases ([0-9]+)', paragraph)[0]
        tests = re.findall(r'Tested as of [A-Z][a-z]+ [0-9]+[a-z]+ ([0-9]+)', paragraph)[0]

        return((cases, deaths, tests, receovered))

    def yolo(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''

        # return('VERIFY. Website blocks scrapes, has an image, or has no info.')


    def yuba(self):
        '''
        Function that uniquely scrapes Covid Info off county or city's health page.
        See CSV for Covid Response Websites.
        Funtion returns in the following format:(cases, deaths, tests, recovered)
        implying: No. positive cases, No. deaths, total tests administered,
        and any recovered cases.
        The '0' in tuple without a variable name means information
        was not found on the website (YET...as of 3/26/2020).
        '''
        # print('AT YUBA')
        paragraph = ''
        self.corona_url = 'https://www.suttercounty.org/doc/government/depts/cao/em/coronavirus'
        souper = self.run_bs4()
        # print('RAN URL')
        for x in souper.find_all('table'):
            # print(x)
            for y in x.find_all(text=True):
                y = y.replace('\n', "")
                if len(y) > 0:
                    paragraph += y.replace('\n', "") + ' '

        for x in self.soup.find_all('p'):
            if 'tests' in str(x):
                paragraph += x.find(text=True) + ' '

        # print(paragraph)

        tests = re.findall(r'reported ([0-9]+) COVID-19 tests', paragraph)[0]
        # tests = tests[0]
        # print(tests)
        results = re.findall(r'Confirmed ([0-9]+) Deaths ([0-9]+)', paragraph)
        # print(results)
        cases = results[1][0]
        deaths = results[1][1]


        return((cases, deaths,tests,0))
