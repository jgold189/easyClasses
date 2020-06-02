import sys
import re
import requests
import json
import time
import random
from bs4 import BeautifulSoup

#Utility class that contains all the info and does all the work
class classesData:
    #URL for class page and individual class data, doesn't change with year
    classURL = "https://oscar.wpi.edu/cgi-bin/oscar/1.3/byC.cgi"
    indivURL = "https://oscar.wpi.edu/cgi-bin/oscar/1.3/byPandC.cgi"

    #Initialize all the headers and urls with the year and cookie
    def __init__(self, year, cookie):
        self.cookie = cookie
        self.year = year

        self.yearURL = "https://oscar.wpi.edu/oscar/" + year + ".html"

        self.yearHeaders = {"Host": "oscar.wpi.edu", 
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0", 
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
        "Accept-Language": "en-US,en;q=0.5", 
        "Accept-Encoding": "gzip, deflate, br", 
        "DNT": "1", 
        "Connection": "keep-alive", 
        "Referer": "https://oscar.wpi.edu/", 
        "Cookie": cookie, 
        "Upgrade-Insecure-Requests": "1"}

        self.classHeaders = {"Host": "oscar.wpi.edu",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": self.yearURL,
        "Cookie": cookie}

        self.indivHeaders = {"Host": "oscar.wpi.edu",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": self.yearURL,
        "Cookie": cookie}


    #Driver function that calls everything else
    def getAllInfo(self):
        self.getYearInfo()
        self.getClassInfo()

    #Gets all the info about the year and all the classes and professors during that year
    def getYearInfo(self):
        r = requests.get(self.yearURL, headers = self.yearHeaders)
        f = open((year + "Index.html"), "w")
        f.write(r.text)
        f.close()
        soup = BeautifulSoup(r.text, 'html.parser')
        i = 0
        isProf = True
        profs = {}
        classes = {}
        #Look through all the options in the html
        for option in soup.find_all("option"):
            #Skip the first option because it isn't needed
            if i == 0:
                i += 1
            #The options are switching from professors to classes
            elif option["value"] == '0':
                isProf = False
            #Add to either the prof or class dictionary
            else:
                if isProf:
                    profs[option["value"]] = option.text
                else:
                    classes[option["value"]] = option.text
        #Save the files out
        fProf = open((year + "Prof.json"), "w")
        json.dump(profs, fProf, indent = 4)
        fProf.close()
        fClass = open((year + "OnlyClasses.json"), "w")
        json.dump(classes, fClass, indent = 4)
        fClass.close()
        #Save the data in the object
        self.profs = profs
        self.classes = classes

    #Gets all the actual info about the indivdual classes
    def getClassInfo(self):
        random.seed()
        results = {}
        #Loops through every class
        for key in self.classes.keys():
            print(key)
            classPayload = {"courseNumber": key, "year": self.year}
            r = requests.get(self.classURL, params=classPayload, headers=self.classHeaders)
            tempArray = []
            #Loops through all the actual class sessions of that course
            for item in r.text[:-1].split("\n"):
                itemSplit = item.split(";")
                indivPayload = {"pidm_id": itemSplit[0], "courseNumber": itemSplit[3], "term": itemSplit[5]}
                r2 = requests.get(self.indivURL, params=indivPayload, headers=self.indivHeaders)
                if r2.status_code != 200:
                    print("ERROR: ", r2.status_code)
                    return 1
                #Append the array with the results converted to a dictionary
                tempArray.append(self.resultsToDictionary(r2.text))
                #Sleep for a random amount of time <1 second to hopefully fool onlookers. Any longer and the program might just take forever
                time.sleep(random.random())
            #Add all the class information to the full results
            results[key] = tempArray
        #Save these results to a file
        fout = open((year + "Classes.json"), "w")
        json.dump(results, fout, indent = 4)
        fout.close()

    #Converts the text response to a dictionary and unscrambles
    def resultsToDictionary(self, r):
        #Split on semicolons
        tarray = r.split(";")
        #Manually assign everything to where it belongs, the actual statistics are passed through the unscrambler
        fullResults = {"profID": tarray[0], "prof": tarray[1], "courseName": tarray[2], "courseID": tarray[3], "numStudents": tarray[4], "courseType": tarray[5], "courseYearTerm": tarray[6], "courseRatings": self.unscramble(tarray[7])}
        return fullResults

    #Unscrambles the statistics the same way the website does
    def unscramble(self, text):
        #Multiple regexes that just replace some items
        text = re.sub(r'w', "0", text)
        text = re.sub(r'b', ".", text)
        text = re.sub(r'[rstvxzcdfghjklmnpq]', "", text)
        text = re.sub(r'[aeiouy]', ",", text)
        #Strip out the newline at the end
        text = text.rstrip()
        #And if the string ends with a trailing comma then just cut it off
        if text[-1] == ",":
            text = text[0:-1]
        return text
        

#TODO: TEST THIS
#Utility class to join together all files and update the entries with an easy value
#This class could be simplified and joined together with the previous one but I already wrote the code in a different format so I am being lazy and just putting it here. Maybe I will one day rework it
#Joins and updates are also done the quick way in memory so if the data files actually grow big enough this won't work. Won't be a problem for a while though
class joinUpdate:
    
    #Set the year and weights which will all be used later
    def __init__(self, years, gradeWeight, timeWeight):
        self.years = years
        self.gradeWeight = gradeWeight
        self.timeWeight = timeWeight

    #Simple driver to call the functions
    def joinAndUpdate(self):
        self.classJoinUpdate()
        self.profJoin()

    #Joins all the years together into one big data set and updates them all with easy scores
    def classJoinUpdate(self):
        classFileString = "Classes.json"
        #Features per question
        FPQ = 9
        allDataSplit = []
        allData = {}

        #For every year open up the data file and put it into the split data array
        for year in self.years:
            f = open(year + classFileString, "r")
            fileJson = json.load(f)
            f.close()
            allDataSplit.append(fileJson)

        #For every set of data in the split data, if the course is in the new dictionary then just tack it on, otherwise set it new
        for yearData in allDataSplit:
            for course in yearData:
                if course in allData:
                    allData[course] += yearData[course]
                else:
                    allData[course] = yearData[course]
        

        #For every course find the needed info to compute and add an easy value
        for course in allData:
            for indiv in allData[course]:
                #Split up all the ratings
                ratings = indiv["courseRatings"].split(",")

                #Find the time avg value hidden in the data using the FPQ
                timeAvg = float(ratings[FPQ+(FPQ*18)-1])

                #Get all the grade ratings and convert them all into ints
                gradeAvg = list(map(int, ratings[(1+(FPQ*17)):(5+(FPQ*17))]))
                #Compute the average grade if possible
                if sum(gradeAvg) == 0:
                    gradeAvg = 0
                else:
                    gradeAvg = (gradeAvg[0] + (gradeAvg[1] * 2) + (gradeAvg[2] * 3) + (gradeAvg[3] * 4)) / sum(gradeAvg)

                #compute the easy value if possible, if either component is 0 then this won't be a valid easy number and should be marked as such
                if gradeAvg == 0 or timeAvg == 0:
                    easy = -1
                else:
                    easy = round((self.gradeWeight * gradeAvg) * (self.timeWeight * timeAvg), 2)

                indiv["easy"] = easy

        #Save it out
        fout = open("allClassesEasy.json", "w")
        json.dump(allData, fout, indent = 4)
        fout.close()

    #Joins all the years together into one big list of professors
    def profJoin(self):
        profFileString = "Prof.json"
        allDataSplit = []
        allData = {}

        #Same as with classes above
        for year in self.years:
            f = open(year + profFileString, "r")
            fileJson = json.load(f)
            f.close()
            allDataSplit.append(fileJson)

        #For every set of data in the split data, if the prof is not in the new dictionary then set it new
        for yearData in allDataSplit:
            for prof in yearData:
                if prof not in allData:
                    allData[prof] = yearData[prof]

        #Save it out
        fout = open("allProf.json", "w")
        json.dump(allData, fout, indent = 4)
        fout.close()


if __name__ == "__main__":
    #All the years to get info from
    COOKIE = "MOD_AUTH_CAS_S="
    if len(sys.argv) < 2:
        print("Need to enter your CAS auth string")
        sys.exit(1)
    elif len(sys.argv) == 4:
        COOKIE += sys.argv[1]
        gradeWeight = float(sys.argv[2])
        timeWeight = float(sys.argv[3])
    else:
        COOKIE += sys.argv[1]
        gradeWeight = 1
        timeWeight = 1

    years = ["2018-2019", "2019-2020"]
    for year in years:
        print(year)
        #Create an object with that year and cookie and then get its info
        classesData(year, COOKIE).getAllInfo()
    
    #Create an object with the years and weights and then have it join and update
    joinUpdate(years, gradeWeight, timeWeight).joinAndUpdate()