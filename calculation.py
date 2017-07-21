import datetime
import dateutil
import json

#Calculate age, BMI, WtoH, OLS and the scores for each discipline

class Calculation(object):

    def __init__(self):
        self.defaultParam = 1

        #Import a json File, in our case the ValueTables
        with open('valueTable.json', 'r') as json_file:
            self.valueTable = json.load(json_file)

    def calcAge(self, testDate, dateOfBirth):
        testDate = datetime.datetime.strptime(testDate, '%d.%m.%Y')
        birthday = datetime.datetime.strptime(dateOfBirth, '%d.%m.%Y')

        # Get the difference between the test date and the birthday
        age = dateutil.relativedelta.relativedelta(testDate, birthday)
        age = age.years
        return age

    def calcBmi(self, weight, height):
        bmi = weight/((height/100)**2)
        return bmi

    def calcWToH(self, waist, height):
        wtoh = waist/height
        return wtoh

    def calcOls(self, olsR, olsL):
        ols = float(olsR) + float(olsL)
        return ols

    def getValueTable(self, gender, age):
        param = ''
        if gender == 'm':
            param = param + 'male'
        elif gender == 'w':
            param = param + 'female'
        else:
            # throw error
            pass

        if age <= 30:
            param = param + '1830'
        elif age > 30 and age <= 45:
            param = param + '3145'
        elif age > 45 and age <= 60:
            param = param + '4660'
        else:
            # throw error
            pass
        return self.valueTable[param]

    def calcScoreSlj(self, gender, age, slj):
        point = 0
        vt = self.getValueTable(gender, age)
        for value in vt:
            if float(slj) >= float(value['slj']):
                point = value['point']
        return point

    def calcScoreSsp(self, gender, age, ssp):
        point = 0
        vt = self.getValueTable(gender, age)
        for value in vt:
            if float(ssp) >= float(value['ssp']):
                point = value['point']
        return point

    def calcScoreOls(self, gender, age, ols):
        point = 0
        vt = self.getValueTable(gender, age)
        for value in vt:
            if float(ols) >= float(value['ols']):
                point = value['point']
        return point

    def calcScoreTms(self, gender, age, tms):
        point = 0
        vt = self.getValueTable(gender, age)
        for value in vt:
            if float(tms) >= float(value['tms']):
                point = value['point']
        return point

    def calcScorePer(self, gender, age, per, location):
        point = 0
        if per == '':
            return 0
        vt = self.getValueTable(gender, age)
        duration = datetime.datetime.strptime(per, '%H:%M:%S')
        delta = datetime.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)
        durationInSeconds = delta.total_seconds()
        for value in vt:
            if durationInSeconds >= float(value[location]):
                point = value['point']
        return point

    def numberToLabel(self, totalScore):
        ts = ''
        if totalScore <= 34:
            ts = 'Ungenuegend'
        elif totalScore >= 35 and totalScore <= 64:
            ts = 'Genuegend'
        elif totalScore >= 65 and totalScore <= 79:
            ts = 'Gut'
        elif totalScore >= 80 and totalScore <= 99:
            ts = 'Sehr gut'
        elif totalScore >= 100:
            ts = 'Hervorragend'
        return ts



        #print(param)
        #print(self.valueTable[param])
