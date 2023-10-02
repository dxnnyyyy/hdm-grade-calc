'''HdM Grade Calculator'''
from getpass import getpass
import mechanicalsoup

URL = "https://vw-online.hdm-stuttgart.de/qisserver/rds?state=user&type=0&topitem="
# Browser
browser = mechanicalsoup.StatefulBrowser(soup_config={"features": "html.parser"})

try:
    browser.open(URL)
    browser.select_form()
except:
    print("Sorry, the HdM SB Funktionen are currently not available.")
    exit()

username = input("Input your username: ")
password = getpass("Input your password: ")

browser["asdf"] = username
browser["fdsa"] = password

browser.submit_selected()

try:
    pruefungsverwaltung = browser.find_link(link_text="Prüfungsverwaltung")
    browser.follow_link(pruefungsverwaltung)
except mechanicalsoup.utils.LinkNotFoundError:
    print("There was an error during login, try again.")
    exit()

try:
    notenspiegel = browser.find_link(link_text="Notenspiegel")
    browser.follow_link(notenspiegel)
except mechanicalsoup.utils.LinkNotFoundError:
    print("There was an error while navigating to the Notenspiegel page, try again.")
    exit()

tableData = browser.page.find_all("td", {"class": "tabelle1"})

dataCounter = 1
tmpList = []
finalGradeList = []

for data in tableData:
    if dataCounter < 12:
        tmpList.append(data.string.strip())
        dataCounter += 1
    elif dataCounter == 12:
        finalGradeList.append({"lectureNumber": tmpList[0],
                               "lectureName": tmpList[2], 
                               "semester": tmpList[4],
                               "grade": tmpList[5],
                               "status": tmpList[6],
                               "ects": tmpList[7],
                               "sws": tmpList[8],
                               "trys": tmpList[10]})
        tmpList = []
        dataCounter = 1

sumGradeTimeEcts = 0
sumEcts = 0
notGradedLecture = 0

for grade in finalGradeList:
    sumEcts += int(grade["ects"])

    if grade["status"] == "angemeldet":
        notGradedLecture += 1

    if not grade["grade"]:
        sumGradeTimeEcts += int(grade["ects"]) * 1
    else :
        strGrade = grade["grade"].replace(",", ".")
        sumGradeTimeEcts += int(grade["ects"]) * float(strGrade)


print()
print("############## hdm notenspiegel ##############")
print()
print("Bisher bewertete ECTS:                   ", sumEcts)
print("Fehlende ECTS:                           ", 210 - sumEcts)
print("Fehlende ECTS (ohne BA):                 ", 198 - sumEcts)
print("Angemeldete Prüfung:                     ", notGradedLecture)
print("Durchschnitts Note (ohne Gewichtung):    ", round(sumGradeTimeEcts / sumEcts, 2))
print()

browser.close()
