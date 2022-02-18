# Get badges located in badge.csv and outputs a badge.json file

import requests
import csv
import json
import urllib3

siteBadges = []


def getSiteBadges():
    # Calls API to get first 10000 badges
    print('getting badges')
    url = f"https://{uniteFQDN}/Services.WebApi/api/v2/RtlsBadges?criteria=%7B%0A%0A%20%20%22Pattern%22%3A%20%22null%22%2C%0A%20%20%22Index%22%3A%200%2C%0A%20%20%22BatchCount%22%3A%2010000%0A%7D"
    siteGetBadges = requests.get(url, auth=(uniteUsername, unitePassword), verify=False)
    siteJsonBadges = siteGetBadges.json()
    # TODO find limits on if this will break with large badge data / how will it affect processing time
    j = int(siteJsonBadges['TotalCount'])
    while j > 0:
        siteBadges.append(siteJsonBadges['Result'][j - 1]['BadgeId'])
        j -= 1


def extractData():
    # Reads file provided in appsettings and sends each row to be get the staffID from Unite Web API
    with open(badgeCSV) as badgeData:
        csvReader = csv.reader(badgeData, delimiter=',')
        for entry in csvReader:
            if entry[0] in siteBadges:
                print(f"Badge {entry[0]} already exists in system")
                entry.append("Badge already exists in system")
                writeFailedBadges(entry)
            else:
                getStaffID(entry)


def addBadgeIDOnly():
    # reads the skipped badges file and attempts to process each badge ID into the system without a user
    with open(f"{badgeCSV}") as badgeData:
        csvReader = csv.reader(badgeData, delimiter=',')
        for entry in csvReader:
            if entry[0] in siteBadges:
                entry.append("Badge already exists in system")
                print(f"Badge {entry[0]} already exists in system")
                writeFailedBadges(entry)
            else:
                writeBadgeNoStaff(entry)


def writeBadgeWithStaff(i):
    # Has badge, staff, staffID data.  Sends to RTLSBadges API with staffID and badgeID
    # TODO is module ID important, siteID is always 1 ( I think )
    url = f"https://{uniteFQDN}/Services.WebApi/api/v2/RtlsBadges"
    payload = {
        "ModuleId": 0,
        "UserId": i[2],
        "BadgeId": str(i[0]),
        "SiteId": 1
    }
    myPost = requests.post(url, auth=(uniteUsername, unitePassword), verify=False, data=payload)
    if myPost.status_code != 201:
        i.append(f"{myPost.status_code} Error adding badge in API")
        writeFailedBadges(i)
    else:
        print(f"Adding badge {i[0]} to user {i[1]} with userID {i[2]} ")


def writeBadgeNoStaff(i):
    # Reads the  badges file, however this only adds badges(first column) to system, no staffID
    # TODO is module ID important, siteID is always 1 ( I think )
    url = f"https://{uniteFQDN}/Services.WebApi/api/v2/RtlsBadges"
    payload = {
        "ModuleId": 0,
        "BadgeId": str(i[0]),
        "SiteId": 1
    }
    myPost = requests.post(url, auth=(uniteUsername, unitePassword), verify=False, data=payload)
    if myPost.status_code == 201:
        print(f"Adding {i[0]} badge with no userID")
    else:
        i.append(f"{myPost.status_code} Error adding badge in API")
        writeFailedBadges(i)


def writeFailedBadges(data):
    # If the Skipped badges fail for any reason they are written here.  Most common reason is duplicate badgeID or bad username / password
    with open('FailedBadges.csv', 'a', newline='') as newFile:
        writer = csv.writer(newFile)
        writer.writerow(data)


def getStaffID(entry):
    # Gets Badge and StaffName, sends name to webAPI and adds StaffName to list. If it cannot find a staff name, or has multiple results from API
    # it will add to a csv file
    badgeToEnter = []
    if entry[1] != "":
        for i in entry:
            badgeToEnter.append(i)
        StaffName = entry[1]
        staffPayLoad = f"https://{uniteFQDN}/Services.WebApi/api/v2/StaffSearch?criteria=%7B%0A%20%20%22Pattern%22%3A%20%22{StaffName}%22%2C%0A%20%20%22UserIds%22%3A%20%5B%5D%2C%0A%20%20%22DeviceAddressIds%22%3A%20%5B%5D%2C%0A%20%20%22OrganizationId%22%3A%20null%2C%0A%20%20%22UserSortOrder%22%3A%200%2C%0A%20%20%22UserSortDirection%22%3A%200%2C%0A%20%20%22DeviceSortOrder%22%3A%200%2C%0A%20%20%22DeviceSortDirection%22%3A%200%2C%0A%20%20%22IncludeUsers%22%3A%20true%2C%0A%20%20%22IncludeDevices%22%3A%20true%2C%0A%20%20%22ExtraSearchableFields%22%3A%20%5B%0A%20%20%20%20%7B%0A%20%20%20%20%20%20%22UserId%22%3A%201%2C%0A%20%20%20%20%20%20%22SearchableValue%22%3A%20%22extra%22%2C%0A%20%20%20%20%20%20%22MatchingField%22%3A%2099%2C%0A%20%20%20%20%20%20%22SearchCondition%22%3A%200%0A%20%20%20%20%7D%0A%20%20%5D%2C%0A%20%20%22IgnoreMatchingFields%22%3A%20%5B%0A%20%20%20%2099%0A%20%20%5D%2C%0A%20%20%22Index%22%3A%200%2C%0A%20%20%22BatchCount%22%3A%2050%0A%7D"
        newData = requests.get(staffPayLoad, auth=(uniteUsername, unitePassword), verify=False)
        if newData.status_code == 200:
            json_data = newData.json()
            i = 0
            # Do not add badges with staff ID if multiple results for staff name (JohnDoe)
            for users in json_data['Users']:
                i += 1
            if i > 1 or i == 0:
                print("Multiple Results for Staff Name or does not exist")
                entry.append("Multiple Results for Staff Name or does not exist")
                writeFailedBadges(entry)
            else:

                # Do not add badge if user already has a badge
                staffBadgeData = json_data['Users'][0]['User']['RtlsBadges']
                if len(staffBadgeData) == 0 and i == 1:
                    staffID = json_data['Users'][0]['User']['Id']
                    badgeToEnter.append(staffID)
                    writeBadgeWithStaff(badgeToEnter)
                else:
                    entry.append("Staff has badge associated already")
                    writeFailedBadges(entry)

    else:
        entry.append("No Staff Name associated to badge")
        writeFailedBadges(entry)


def main():
    print("##################################################################################################")
    print("###  This program was written by Christian Baier 2Feb2022.  This will import badges from a csv ###")
    print("###  file into Unite.  The format of the data must be in the following format:                 ###")
    print("###  <BadgeID>, <StaffName>                                                                    ###")
    print("###  1111, John Doe                                                                            ###")
    print("###  2222,                                                                                     ###")
    print("###  3333, John                                                                                ###")
    print("###  As with any change to a system, you must take a SQL backup prior to continuing            ###")
    print("##################################################################################################")

    # Get user input to go next
    # Use this to fix SSL warnings
    urllib3.disable_warnings()
    nextTask = "NO"
    while nextTask != "YES":
        nextTask = (input("Did you take a SQL backup of Unite? NO or YES  ")).upper()
    nextTask = "NO"
    while nextTask != "YES":
        nextTask = input("Did you Fill out the appsettings.json file? NO or YES  ").upper()
        try:
            with open("appsettings.json", 'r') as appsettings:
                paramData = json.load(appsettings)
                print(paramData)
                global uniteFQDN
                global badgeCSV
                global uniteUsername
                global unitePassword
                uniteFQDN = paramData["UniteFQDN"]
                badgeCSV = paramData["BadgeCSVFile"]
                uniteUsername = paramData["UniteUserName(admin)"]
                unitePassword = paramData["UnitePassword"]
                badgesOnly = paramData["BadgesOnly"]
                if paramData["BadgesOnly"].upper() == "TRUE":
                    badgesOnly = True
                if paramData["BadgesOnly"].upper() == "FALSE":
                    badgesOnly = False
                else:
                    print("Invalid input for BadgesOnly")
                    raise ValueError
        except:
            print("Application settings cannot be read")
            nextTask = "NO"
    # first get site badges into list: siteBadges
    getSiteBadges()
    if not badgesOnly:
        extractData()
    if badgesOnly:
        addBadgeIDOnly()


if __name__ == "__main__":
    main()
