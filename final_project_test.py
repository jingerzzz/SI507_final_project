import unittest
from final_project import *




class TestDataSource(unittest.TestCase):
    def test_data_source(self):
        url = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=Data+Analyst&sc.keyword=Data+Scientist&locT=S&locId=527&jobType="
        resp = requests.get(url,headers=header)
        page_text = resp.text
        page_soup = BeautifulSoup(page_text,'html.parser') 
        jobs = page_soup.find_all("div", {"class": "jobContainer"})
        self.assertNotEqual(jobs,None)

class TestDatabase(unittest.TestCase):

    def test_job_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT * FROM Jobs'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertGreater(len(result_list), 100)

        sql = '''
            SELECT EmployerId FROM Jobs
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertGreater(len(result_list), 100)
        
        sql = '''
            SELECT JobName FROM Jobs
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertGreater(len(result_list), 100)

        conn.close()

    def test_company_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT * FROM Companies'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertGreater(len(result_list), 50)

        sql = '''
            SELECT CompanyName FROM Companies
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertGreater(len(result_list), 50)
        
        sql = '''
            SELECT Founded FROM Companies
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertGreater(len(result_list), 50)

        conn.close()

    def test_headers(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = "select * from Jobs"
        q1 = cur.execute(sql)
        names = list(map(lambda x: x[0], q1.description))
        headers = ["id","EmployerId","JobName","Location","MinSalary","MaxSalary"]
        self.assertEqual(headers, names)

        sql = "select * from Companies"
        q1 = cur.execute(sql)
        names = list(map(lambda x: x[0], q1.description))
        headers = ["id","CompanyName","Headquarters","Founded","Industry","Type","Sector"]
        self.assertEqual(headers, names)

        conn.close()

class TestJobSearch(unittest.TestCase):

    def test_search(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary\
                                from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Jobs.MinSalary < {} and Jobs.MaxSalary >{}".format(60,60))
        result_list = q1.fetchall()
        self.assertGreater(len(result_list), 10)

        q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary\
                                from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Jobs.MinSalary < {} and Jobs.MaxSalary >{}".format(100,100))
        result_list = q1.fetchall()
        self.assertGreater(len(result_list), 10)
        
        q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Companies.Founded, Jobs.MinSalary, Jobs.MaxSalary\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Founded >{} and Companies.Founded != 'unknown'".format(2000))
        result_list = q1.fetchall()
        self.assertGreater(len(result_list), 10)

        q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary, Companies.Industry\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Industry = 'IT Services'")
        result_list = q1.fetchall()
        self.assertGreater(len(result_list), 10)

        q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary, Companies.Type\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Type = 'Company - Private'")
        result_list = q1.fetchall()
        self.assertGreater(len(result_list), 10)
        
        q1 = cur.execute("select Jobs.JobName, Companies.CompanyName, Jobs.Location, Jobs.MinSalary, Jobs.MaxSalary, Companies.Sector\
                                        from Jobs left join Companies\
                                            where Jobs.EmployerId = Companies.id and Companies.Sector = 'Business Services' ") 
        result_list = q1.fetchall()
        self.assertGreater(len(result_list), 10)

        conn.close()


unittest.main()

