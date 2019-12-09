import requests
import json
import plotly
import plotly.graph_objs as go
from secret_data import *
from bs4 import BeautifulSoup
from selenium import webdriver
import sqlite3
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

baseurl = "https://www.glassdoor.com/Job/jobs.htm"
params = {"suggestCount":0,"suggestChosen":"false","clickSource":"earchBtn","typedKeyword":"Data+Scientist","sc.keyword":"Data+Analyst","locT":"S","locId":"527","jobType":"","includeNoSalaryJobs":"false"}
url = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=Data+Analyst&sc.keyword=Data+Scientist&locT=S&locId=527&jobType="
baseurl_next_page = "https://www.glassdoor.com"
header = {'User-Agent': 'SI_CLASS'}


DBNAME = 'posted_jobs.db'








class posted_job():
    def __init__(self, employer_name="",job_name="", location="",salary=[0,0]):
        self.employer_name = employer_name
        self.job_name = job_name
        self.location = location
        self.salary = salary    

    def __str__(self):  
        return "{} {} {} {}".format(self.employer_name, self.job_name, self.location, self.salary)





def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_" + "_".join(res)

def fetch_cache_with_params(baseurl,params):

    unique_ident = params_unique_combination(baseurl,params)

    ## first, look in the cache t'v':'20193111'o see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

def fetch_cache_without_params(url):

    unique_ident = url

    ## first, look in the cache t'v':'20193111'o see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url,headers=header)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

def process_raw_and_store():
    page_text = fetch_cache_without_params(url)
    page_soup = BeautifulSoup(page_text,'html.parser') 
    browser = webdriver.Chrome(executable_path="chromedriver.exe")
    browser.get(url)

    job_list = []
    company_dict = {}
    next_page_url = "Not None"
    while(next_page_url != None):
        ## get job information
        jobs = page_soup.find_all("div", {"class": "jobContainer"})
        jobs_button = browser.find_elements_by_class_name("jobContainer")
        print(len(jobs))
        print("\n")

        for i in range(len(jobs)):## get each job information
            job = jobs[i]
            job_title = job.find_all("a")
            employer_name = job_title[0].text
            job_name = job_title[1].text
            try:
                job_loc = job.find("div", {"class": "jobInfoItem empLoc"}).text
            except:
                job_loc = "unknown"
            job_salary = job.find("span", {"class": "salaryText"})
            if job_salary != None:
                job_salary = job_salary.text
                job_salary_pair = job_salary.split('-')
                job_salary_pair[0] = int(job_salary_pair[0].strip()[1:-1])
                job_salary_pair[1] = int(job_salary_pair[1].strip()[1:-1])
                job_salary = job_salary_pair
            else:
                job_salary = [0,0]
            job_list.append(posted_job(employer_name, job_name, job_loc, job_salary))
            

            ## get the information of company of the job
            job_button = jobs_button[i]
            try:
                close_button = browser.find_element_by_id("prefix__icon-close-1")
                close_button_2 = close_button.find_element_by_tag_name("path")
                close_button_2.click()
            except:
                pass
            job_button_2 = job_button.find_element_by_tag_name("a")
            job_button_2.click()
            time.sleep(1) 
            try:
                close_button = browser.find_element_by_id("prefix__icon-close-1")
                close_button_2 = close_button.find_element_by_tag_name("path")
                close_button_2.click()
            except:
                pass
            try:
                scrollableTabs = browser.find_element_by_class_name("scrollableTabs")
                company = scrollableTabs.find_elements_by_tag_name("div")[1]
                button = company.find_element_by_tag_name("span")
                button.click()
                 
            except:
                print("{}: {} bla".format(employer_name, job_name))
            time.sleep(1)
            html = browser.page_source
            results = BeautifulSoup(html,'html.parser') 
            print("{}: {}".format(employer_name, job_name))
            try:
                info_row = results.find("div",{"class":"info row"})
                info_entities = info_row.find_all("div",{"class":"infoEntity"})
            except:
                info_entities = []
                print("no data point")
            company_info_dict = {}
            for info_entity in info_entities:
                try:
                    label = info_entity.find("label").text
                    value = info_entity.find("span").text
                    company_info_dict[label] = value
                except:
                    pass
                
            if employer_name not in company_dict:
                company_dict[employer_name] = company_info_dict









        next_page = page_soup.find("div", {"class": "pagingControls cell middle"})
        if next_page == None:
            break
        else:
            next_page = next_page.find("li", {"class": "next"})
        if next_page == None:
            break
        else:
            next_page_url = next_page.find("a")
        if next_page_url == None:
            break
        else:
            next_page_url = baseurl_next_page + next_page_url['href']
            page_text = fetch_cache_without_params(next_page_url)
            page_soup = BeautifulSoup(page_text,'html.parser') 
            browser.get(next_page_url)

    ######################  Above is to fetch all the data needed  ################################ 
    ######################  Next is to store them in the database   ################################        
    sqlite3.connect(DBNAME)
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    company_list_fixed = []
    for key,value in company_dict.items():## make sure every company attribute has a value or is unknown
        if "Headquarters" not in value:
            value["Headquarters"]="unknown"
        if "Founded" not in value:
            value["Founded"]="unknown"
        if "Industry" not in value:
            value["Industry"]="unknown"
        if "Type" not in value:
            value["Type"]="unknown"
        if "Sector" not in value:
            value["Sector"]="unknown"
        company_list_fixed.append([key,value["Headquarters"],value["Founded"],value["Industry"],value["Type"],value["Sector"]])

    for company_fixed in company_list_fixed:
        print("{}|{}|{}|{}|{}|{}".format(company_fixed[0],company_fixed[1],company_fixed[2],company_fixed[3],company_fixed[4],company_fixed[5]))
    # try:
    cur.execute("drop table if exists 'Jobs'")
    cur.execute("drop table if exists 'Companies'")
    cur.execute('''CREATE TABLE Companies(
        [id] INTEGER PRIMARY KEY,
        [CompanyName] text, 
        [Headquarters] text,
        [Founded] integer,
        [Industry] text,
        [Type] text, 
        [Sector] text
        )''')           
    cur.execute('''CREATE TABLE Jobs(
        [id] INTEGER PRIMARY KEY,
        [EmployerId] integer, 
        [JobName] text,
        [Location] text,
        [MinSalary] integer,
        [MaxSalary] integer,
        foreign key (EmployerId) references Companies (id)
        )''')
    for company_fixed in company_list_fixed:
        insertion = (None, company_fixed[0],company_fixed[1],company_fixed[2],company_fixed[3],company_fixed[4],company_fixed[5])
        statement = 'INSERT INTO "Companies" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
    conn.commit()        

    company_id_dict = {}
    company_id = 1
    for company in company_list_fixed:
        company_id_dict[company[0]] = company_id
        company_id = company_id + 1

    for job in job_list:
        try:
            insertion = (None, company_id_dict[job.employer_name], job.job_name, job.location, job.salary[0],job.salary[1])
            statement = 'INSERT INTO "Jobs" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)
        except:
            ("Error in insertion")
    conn.commit()
    # except:
        # print("Something wrong with database")



    return job_list

def data_presentation():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    help_text = load_help_text()

    response = ''
    while True:
        response = input('Select a mode (filter/graph): ')
        if response == 'exit':
            print("bye!")
            break

        elif response == 'help':
            print(help_text)
            continue

        elif response == "filter":
            attribute = input('Select an attribute to filter (salary/founded year/industry/type/sector):')

            if attribute == "salary":
                value = input('Input your expecting salary (one integer):')
                try:
                    value = int(value)
                except:
                    print("Something wrong with the value.")
                    continue
                q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Jobs.MinSalary < {} and Jobs.MaxSalary >{}".format(value,value))
                list_data(q1)

            elif attribute == "founded year":
                value = input('Input the founded year which companies you want to see were founded after:')
                try:
                    value = int(value)
                except:
                    print("Something wrong with the value.")
                    continue
                q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Companies.Founded, Jobs.MinSalary, Jobs.MaxSalary\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Founded >{} and Companies.Founded != 'unknown'".format(value))
                list_data(q1)

            elif attribute == "industry":
                value = input('Input the Insdustry of the companies you are looking for:')
                q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary, Companies.Industry\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Industry = '{}'".format(value))
                list_data(q1)

            elif attribute == "type":
                value = input('Input the Insdustry of the companies you are looking for:')
                q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary, Companies.Type\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Type = '{}'".format(value))
                list_data(q1)

            elif attribute == "sector":
                value = input('Input the Insdustry of the companies you are looking for:')
                q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary, Companies.Sector\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Sector = '{}'".format(value)) 
                list_data(q1)           
            

            elif attribute == "exit":
                print("bye!")
                break

            elif attribute == "help":
                print(help_text)


            else:
                print("Input the attribute again!")

        elif response == "graph":
            selection = input('Select 1-3:')            
            if selection == '1':
                q1 = cur.execute("select  Companies.CompanyName,count(Jobs.JobName) as count\
                                    from Jobs left join Companies\
                                        where Jobs.EmployerId = Companies.id\
                                            group by Companies.CompanyName\
                                                order by count desc\
                                                    limit 15")
                plot_data(q1)
            elif selection == '2':
                q1 = cur.execute("select  Companies.Industry,count(Jobs.JobName) as count\
                                    from Jobs left join Companies\
                                        where Jobs.EmployerId = Companies.id\
                                            group by Companies.Industry\
                                                order by count desc\
                                                    limit 15")
                plot_data(q1)
            elif selection == '3':
                q1 = cur.execute("select  Companies.Type,count(Jobs.JobName) as count\
                                    from Jobs left join Companies\
                                        where Jobs.EmployerId = Companies.id\
                                            group by Companies.Type\
                                                order by count desc\
                                                    limit 15")
                plot_data(q1)
            elif selection == "exit":
                print("bye!")
                break
            elif selection == "help":
                print(help_text) 
            else:
                print("Input the selection again!")

        else:
            print("Command is unrecognized. Please input again!")
    
def list_data(q1):
    names = list(map(lambda x: x[0], q1.description))
    values = []
    try:
        value_list = q1.fetchall()
        length = len(value_list[0])
        for i in range(length):
            values.append([])
        for value in value_list:
            for j in range(length):
                values[j].append(value[j])
    except:
        pass
    fig = go.Figure(data=[go.Table(header=dict(values=names),
                                cells=dict(values=values))
                                ])
    fig.write_html('list.html',auto_open=True)

def plot_data(q1):
    names = list(map(lambda x: x[0], q1.description))
    values = q1.fetchall()
    df = pd.DataFrame(values,columns=names)

    fig = px.bar(df, x=names[0], y=names[1])
    fig.write_html('plot.html',auto_open=True)

def load_help_text():
    with open('help.txt') as f:
        return f.read()

if __name__ == "__main__":
    CACHE_FNAME = 'fetch_cache.json'
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()

# if there was no file, no worries. There will be soon!
    except:
        CACHE_DICTION = {}


    # job_list = process_raw_and_store()
    data_presentation()
  