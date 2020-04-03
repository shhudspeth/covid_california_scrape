# covid_california_scrape
 A webscraper of Public Health websites in California about COVID_19.
 Returns a csv file of DAILY data in the format of
 "date,county,cases,deaths,tests,recovered.
 
 The CSV file (../data/CA_Coronovirus_Websites_by_county.csv) has all the UPDATED coronovirus websites. 
 They were scraped off the CA state public health site and then updated for Coronavirus information.

 Not all county websites are able to be scraped. These counties will should NAN files.
 In the 'California Counties Notebook', there are some work arounds for some of
 these counties. Saving a webfile of the website (see folder webpages), and
 then scraping the website with Beautiful Soup is one such workaround. I still found the specific
 soup code, so please use accordingly. I plan
 to add a workaround file after I brush up on some skills.

 Other county websites use images or dashboards to give updates on the latest
 covid data and accessing the website is your best bet.  

 Stay tuned for dashboards and graphics, but please start using the data to make
 your own.

A note on scrape_utilities.py:

To get a specific county data, load the county+website csv file.
make an instance of "CountyData". Use ".add_soup()" to run Beautiful Soup. Use ".make_data(name_of_county())" to 
get a tuple of the number of cases, deaths, tests, recovered, respectively. 

I.e. 
```
counties_and_websites = scrape_utilities.read_csv('../data/CA_Coronovirus_Websites_by_county.csv')
# counties_and_websites[39] = (San Francisco,https://www.sfdph.org/dph/alerts/coronavirus.asp)

sf = scrape_utilities.CountyData('San Francisco', counties_and_websites[39][1])
sf.name = san_francisco
sf.add_soup() # soup added and can be called by sf.soup
sf.make_data(san_francisco()) # returns (450, 7, 0,0)
sf.positive_cases  # returns 450

sf.run_bs4()  # will run beautiful soup for a new soup
sf.date_of_scrape #returns what day (not time) the scrape happened
```

To make a quick scrape without writing a dictionary, use the following code...
Note that to actually scrape, one has to have the county in lower_case with _ for a space
and there has to be a way to do it with an executable code...

```
def quick_scrape(counties_and_websites)
   for x in counties_and_websites):
       try: 
           x = scrape.utilities.CountyData(x[0], x[1])
           x.add_soup()
           func = 'x.make_data(x.' + str(x.name) +'())'
           exec(func)
           print("DATA SCRAPED for",x.name,x.scrape)
        
       except:
            print('Scrape Error', x.name)
return("Scraped County Website for Corona Information")
```
 
