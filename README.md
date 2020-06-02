# Easy Classes at WPI

Tool to figure out easy classes at WPI based on student course reports. Runs on Python 3.  

## Disclaimer

WPI probably does not want people scraping this data off their sites and might get annoyed if they notice this. Reminder any time you scrape this data you are sending the request both from your IP address and with your own CAS authentication token which can easily be traced back to you. They know who is sending these massive amounts of requests and they might try to take action against you.  

I'm not going to heavily maintain this project so expect certain areas to break as time goes by. This pulls all data from oscar.wpi.edu so if nearly **anything** on that site gets updated (which I expect it will very soon) then this whole program could break. It is also only set up to currently grab course reports from 2018-2019 and 2019-2020.  

## Setup

Since WPI currently has the course reports behind a login wall I will assume they don't want this data to be accesible by anyone outside of the school so I will not provide a copy of this data here or any way to obtain the data unless you are a student of WPI. To obtain a copy of the data yourself you must run data.py which will scrape all the data from the WPI site, join it into one big dataset, and add calculated easy values to the dataset. Notice: This currently functions all in memory so if this still works many years later it may break if all the data can not fit into main memory.  

Setup has a time delay built into each request to try and make it less like a rapid deluge of requests so if you want to dramatically speed the program up just remove that delay but be warned WPI may not like that and take notice of it. You could always multithread the requests to rapidly speed it up but the code currently is not fully set up for that.  

To run: `python data.py CAS_TOKEN [gradeWeight] [timeWeight]`  

Where CAS_TOKEN is your assigned cas security token (explained below), gradeWeight is the weight you want to assign to how many people say they get good grades (default is 1.0, higher means it is more important), and timeWeight is the weight you want to assign to how many hours people say the course takes them outside of class (default is 1.0, higher means it is more important). *Note you must have both a gradeWeight and a timeWeight if you want to use them.*  

To obtain your cas token go to oscar.wpi.edu, select a year and then open up your web console, go to the network tab and select a class from the drop down. At any point in this process if it asks you to log into CAS do so. Once you select a class there should be a request in your network tab, look through the request properties to find one relating to CAS, that will be your CAS authentication token, copy that down and enter it as an argument when you run the program. *Note it will change once your cas token expires and you must log back in.*  

You should now have all the data you need and should not need to run data.py again.  

## Normal Use

The program allows you to either enter a specific course (i.e. CS 1101) and get rankings on the easiest professor to take it with or enter a specific major and get rankings on the easiest classes within the major.  

To run: `python easy.py`  

From there things should be self-explanatory but either enter a course or major.  

## A final word of warning  

This program honestly isn't that useful. Course reports while useful to the professor to make decisions about how to improve the class are not the best metric to measure the easiness of a class. You will tend to notice that higher level courses for some reason tend to rank easier, specifically graduate level classes. While I cannot give a definite reason to this my guess is along the line of graduate students tend not to fill out the course reports as much and tend to expect courses to be harder so they are more willing to put up with it and rank them easier. This program works best for deciding which professor to take a certain class with as that tends to be at least semi-insightful. Lower-level classes tend to be seen as very hard because many people take them and as such many people rank them and a lot of people outside the designated major take them and might find them harder than people within the major. Use the data you find within at your own risk.
