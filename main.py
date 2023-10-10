"""HdM Grade Calculator"""
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
bachelor = input(
    "What do you expect of your bachelorthesis? (or leave it empty by hitting enter. Caution: avg grade might vary) "
)

bachelor = bachelor.replace(",", ".")


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

table = browser.page.find("table", {"cellspacing": 0})
tableData = table.find_all("tr")

hauptstudiumIndex = 0

for data in tableData[1:]:
    if data.find("th") and data.find("th").get_text() == "Hauptstudium":
        hauptstudiumIndex = tableData.index(data)


grundstudiumGrades = []
hauptstudiumGrades = []

for data in tableData[2:hauptstudiumIndex]:
    grundstudiumGrades.append(
        {
            "lectureNumber": data.find_all("td", {"class": "tabelle1"})[
                0
            ].string.strip(),
            "lectureName": data.find_all("td", {"class": "tabelle1"})[2].string.strip(),
            "semester": data.find_all("td", {"class": "tabelle1"})[4].string.strip(),
            "grade": data.find_all("td", {"class": "tabelle1"})[5].string.strip(),
            "status": data.find_all("td", {"class": "tabelle1"})[6].string.strip(),
            "ects": data.find_all("td", {"class": "tabelle1"})[7].string.strip(),
            "sws": data.find_all("td", {"class": "tabelle1"})[8].string.strip(),
            "trys": data.find_all("td", {"class": "tabelle1"})[10].string.strip(),
        }
    )

for data in tableData[hauptstudiumIndex + 1 :]:
    hauptstudiumGrades.append(
        {
            "lectureNumber": data.find_all("td", {"class": "tabelle1"})[
                0
            ].string.strip(),
            "lectureName": data.find_all("td", {"class": "tabelle1"})[2].string.strip(),
            "semester": data.find_all("td", {"class": "tabelle1"})[4].string.strip(),
            "grade": data.find_all("td", {"class": "tabelle1"})[5].string.strip(),
            "status": data.find_all("td", {"class": "tabelle1"})[6].string.strip(),
            "ects": data.find_all("td", {"class": "tabelle1"})[7].string.strip(),
            "sws": data.find_all("td", {"class": "tabelle1"})[8].string.strip(),
            "trys": data.find_all("td", {"class": "tabelle1"})[10].string.strip(),
        }
    )


grundstudiumSumGradeTimeEcts = 0
grundstudiumSumEcts = 0

hauptstudiumSumGradeTimeEcts = 0
hauptstudiumSumEcts = 0

notGradedLecture = 0

for grade in grundstudiumGrades:
    grundstudiumSumEcts += int(grade["ects"])

    if grade["status"] == "angemeldet":
        notGradedLecture += 1

    if not grade["grade"]:
        grundstudiumSumGradeTimeEcts += int(grade["ects"]) * 1
    else:
        strGrade = grade["grade"].replace(",", ".")
        grundstudiumSumGradeTimeEcts += int(grade["ects"]) * float(strGrade)

for grade in hauptstudiumGrades:
    hauptstudiumSumEcts += int(grade["ects"])

    if grade["status"] == "angemeldet":
        notGradedLecture += 1

    if not grade["grade"]:
        hauptstudiumSumGradeTimeEcts += int(grade["ects"]) * 1
    else:
        strGrade = grade["grade"].replace(",", ".")
        hauptstudiumSumGradeTimeEcts += int(grade["ects"]) * float(strGrade)


sumEcts = grundstudiumSumEcts + hauptstudiumSumEcts
sumGradeTimeEcts = grundstudiumSumGradeTimeEcts + hauptstudiumSumGradeTimeEcts


avgGrund = grundstudiumSumGradeTimeEcts / grundstudiumSumEcts
avgHaupt = hauptstudiumSumGradeTimeEcts / hauptstudiumSumEcts

bachelorGrade = 0


print()
print("############## hdm notenspiegel ##############")
print()
print("Bisher bewertete ECTS:                   ", sumEcts)
print("Fehlende ECTS:                           ", 210 - sumEcts)
print("Fehlende ECTS (ohne BA):                 ", 198 - sumEcts)
print("Angemeldete Prüfung:                     ", notGradedLecture)
print("Durchschnitts Note Grundstudium:         ", round(avgGrund, 2))
print("Durchschnitts Note Hauptstudium:         ", round(avgHaupt, 2))

if bachelor:
    print(
        "Durchschnitts Note MIT BA Schätzung:     ",
        round(avgGrund * 0.15 + (avgHaupt) * 0.7 + float(bachelor) * 0.15, 2),
    )
else:
    print(
        "Durchschnitts Note OHNE BA Schätzung:    ",
        round(avgGrund * 0.15 + (avgHaupt) * 0.7, 2),
    )
print()

browser.close()
