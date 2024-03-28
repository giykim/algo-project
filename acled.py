import requests

def getAcled():
    agreeUrl = "https://api.acleddata.com/acled/read?terms=accept"
    url2 = "https://api.acleddata.com/acled/read.csv/?key=tHgpcI60XvD8v014T1DP&email=hth8@duke.edu"
    #tHgpcI60XvD8v014T1DP
    x = requests.get(url=url2)
    dataList = list(x.text.split("\n"))
    print(dataList)

    '''
    import csv
    filename = "acledData1.csv"
    with open(filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        for element in dataList:
            writer.writerow(element.split(',')) 
    '''
def main():
    acledData = getAcled()

    print(acledData)

if __name__ == "__main__":
    main()    