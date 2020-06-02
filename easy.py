#Lower easier number is better

import json
import re

#Class for handling all search utilities
class Search:
    
    #Initialize the class by loading in all the data and profs
    def __init__(self):
        f = open("allClassesEasy.json", "r")
        self.allData = json.load(f)
        f.close()

        f = open("allProf.json", "r")
        self.allProf = json.load(f)
        f.close()

    #Quick average function, takes a list, always rounds to two decimal places. (We don't need to be that precise)
    def avg(self, arg):
        return round((sum(arg) / len(arg)), 2)

    #Replaces all profID with the actual prof names. Takes input in format of [(profID, num), ...]
    def profIDReplace(self, classList):
        results = []
        for pair in classList:
            newPair = (self.allProf[pair[0]], pair[1])
            results.append(newPair)
        return results
    
    #Gets all the sections of the class and averages out their easy number by professor and ranks them
    def classSearch(self, entry):
        #Key: profID, value: list of easy ratings from taught classes
        classByProf = {}
        #For every individual section of the course
        for indiv in self.allData[entry]:
            profID = indiv["profID"]
            #If the prof is in the dictionary just add more data, else start the data
            if profID in classByProf:
                classByProf[profID] += [indiv["easy"]]
            else:
                classByProf[profID] = [indiv["easy"]]
        
        #Average out every profs easy scores
        for prof in classByProf:
            classByProf[prof] = self.avg(classByProf[prof])

        #Get all the items from the dictionary in a list and sort them by the easy score
        results = list(classByProf.items())
        results.sort(key = lambda x: x[1])
        results = self.profIDReplace(results)
        return results

    #Gets all classes in a major and ranks them by average easy divided by class
    def majorSearchByClass(self, entry):
        results = []
        majorClasses = []
        #Finds every key (class) with that major in its name
        for key in self.allData:
            if entry in key:
                majorClasses.append(key)

        #For every key get the class ratings by prof and then just save the average of those easy ratings
        for key in majorClasses:
            classByProf = self.classSearch(key)
            temp = []
            for item in classByProf:
                temp.append(item[1])
            results.append((key, self.avg(temp)))
        #Return the sorted results
        results.sort(key = lambda x: x[1])
        return results
        

    #Gets all classes in a major and ranks them by easy divided by class and professor
    def majorSearchByProf(self, entry):
        results = []
        majorClasses = []
        #Finds every key (class) with that major in its names
        for key in self.allData:
            if entry in key:
                majorClasses.append(key)

        #For every key get the class ratings by prof, map them to have the course name in the tuple and then add it to the results
        for key in majorClasses:
            results += list(map(lambda x: (key, x[0], x[1]), self.classSearch(key)))
        #Lastly return the sorted results
        results.sort(key = lambda x: x[2])
        return results


#TODO: Add in error handling if a class or major doesn't exist
if __name__ == "__main__":
    searchUtil = Search()
    classSearchString = "^[a-zA-z]{2}[a-zA-z]? [0-9]{3}[0-9xX]?$"
    majorSearchString = "^[a-zA-z]{2}[a-zA-z]?$"

    #Input loop
    while True:
        entry = input("Enter in either a class (i.e. CS 1101) or a major (i.e. ME) or type quit\n")
        #If a class
        if re.search(classSearchString, entry):
            results = searchUtil.classSearch(entry)
            print("Easiest class by professor (Lower number is better)")
            for item in results:
                print(item[0], item[1], sep="\t")
            print()
        #If a major
        elif re.search(majorSearchString, entry):
            results = searchUtil.majorSearchByClass(entry.upper())
            print("Easiest classes in major by average rating (Lower number is better)")
            for item in results:
                print(item[0], item[1], sep="\t")

            print("\n****************************************************************************************\n")
            results = searchUtil.majorSearchByProf(entry.upper())
            print("Easiest classes in major by class and professor (Lower number is better)")
            for item in results:
                print(item[0], item[1], item[2], sep="\t\t")
            print()
        #If not valid
        elif entry == "quit":
            break
        else:
            print("Please enter a valid option\n")