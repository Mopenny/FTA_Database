#FTA Database Code

import os
import json
import csv
import numpy as np
import pylatex
import operator
import matplotlib.pyplot as plt

from pylatex import Document, Section, Subsection, Command, Figure
from pylatex.utils import italic, NoEscape
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from calculation import Calculation

#Create LaTeX document
def createDocument(filename, documentResults):
    doc = Document('full')
    imageFilename = os.path.join(os.path.dirname(__file__), 'plots/Beni_Anliker.png')
    with doc.create(Section('Leistungstest Feuerwehr Derendingen 2017', numbering=False)):
        with doc.create(Subsection('Persönliche Daten', numbering=False)):
            doc.append('Name ')
            doc.append('\nAlter ')
            doc.append('\nGrösse ')

            doc.append(italic('\nitalic text. '))

        with doc.create(Subsection('Aktuelle Testresultate', numbering=False)):
            doc.append('Standweitsprung: ' + documentResults['slj'])
            doc.append('\nGesamtpunktzahl Leistungstest: ' + documentResults['totalScore']  + ' von 125 Punkten = ' + documentResults['numberToLabel'])

        with doc.create(Subsection('Längsschnittvergleich', numbering=False)):
            with doc.create(Figure(position = 'h!')) as diagram:
                diagram.add_image(imageFilename, width = '350px')
                diagram.add_caption('Beurteilung: 1 = Ungenügend, 2 = Genügend, 3 = Gut, 4 = Sehr gut, 5 = Hervorragend')

    #doc.generate_pdf(clean_tex=False)
    #doc.generate_tex()
    print(doc.dumps())

#Import data from csvfile
def dataImport(filename):
    data = []
    with open(filename, 'rU') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=',')
        for row in datareader:
            row['id'] = row['surname'] + row['name'] + row['dateOfBirth']
            row['slj'] = round(float(row['slj']), 2)
            row['ssp'] = round(float(row['ssp']), 2)
            data.append(row)
    data.sort(key=operator.itemgetter('id'))
    return data


#Calculate per Person
def calculate(personalData):
    calculation = Calculation()
    result = {
        'years': []
    }
    personalData.sort(key=operator.itemgetter('year'))
    personalData = personalData[-3:]
    for data in personalData:
        age = calculation.calcAge(data['testDate'], data['dateOfBirth'])
        print('\n\n' + data['name'] + ' ' + data['surname'] + ' ' + str(age))
        bmi = calculation.calcBmi(data['weight'], data['height'])
        wtoh = calculation.calcWToH(data['waist'], data['height'])
        ols = calculation.calcOls(data['olsR'], data['olsL'])
        scorePerO = calculation.calcScorePer(data['gender'], age, data['perO'], 'perO')
        scorePerI = calculation.calcScorePer(data['gender'], age, data['perI'], 'perI')
        scoreTable = [
            ('Standweitsprung', str(data['slj']) + ' m', calculation.calcScoreSlj(data['gender'], age, data['slj'])),
            ('Medizinballstoss', str(data['ssp']) + ' m', calculation.calcScoreSsp(data['gender'], age, data['ssp'])),
            ('Einbeinstand', str(ols) + ' s', calculation.calcScoreOls(data['gender'], age, ols)),
            ('Globaler Rumpfkrafttest', data['tms'] + ' s', calculation.calcScoreTms(data['gender'], age, data['tms'])),
            ('Progressiver Ausdauerlauf', data['perO'] + ' min:s', scorePerO) if scorePerI == 0 else ('20m Pendellauf', data['perI'] + ' min:s', scorePerI)
        ]

        #Berechnung Gesamtpunktzahl, Bewertung der Gesamtpunktzahl und Umrechnung der einzelnen Disziplinen für das Spider Diagramm
        totalScore = 0
        spiderScores = []
        spiderScoreLabels = []
        for score in scoreTable:
            totalScore = totalScore + score[2]
            if score[2] < 7:
                spiderScores.append(1)
            elif score[2] < 13:
                spiderScores.append(2)
            elif score[2] < 16:
                spiderScores.append(3)
            elif score[2] < 20:
                spiderScores.append(4)
            else:
                spiderScores.append(5)
            spiderScoreLabels.append(score[0])
        numberToLabel = calculation.numberToLabel(totalScore)

        result['id'] = data['id']
        result['name'] =  data['name'] + ' ' + data['surname']
        result['age'] =  str(age) + ' Jahre'
        result['heigth'] = data['height'] + ' cm'
        result['weight'] = data['weight'] + ' kg'
        result['bmi'] = str(bmi) + ' kg/m^2'
        result['wtoh'] = wtoh
        result['scoreTable'] = scoreTable
        result['totalScore'] = totalScore
        result['numberToLabel'] = numberToLabel
        result['years'].append({
            'year': data['year'],
            'spiderScoreLabels': spiderScoreLabels,
            'spiderScores': spiderScores
        })
    return result

    #return dict with results

#Create plot for person
def savePlot(data):
    pass

#Hauptfunktion
def main():

    importedData = dataImport('TestData.csv')
    testResults = {
        'slj': '25',
        'age': '23',
        'totalScore': '101',
        'numberToLabel': 'Hervorragend',
    }
    results = []
    personalData = []
    currentId = importedData[0]['id']
    for row in importedData:
        if(row['id'] != currentId):
            formattedData = calculate(personalData)
            results.append(formattedData)
            personalData = []
            currentId = row['id']
        row['year'] = row['testDate'][-4:]
        personalData.append(row)


    print(results)

    #createDocument(None,testResults)

    for person in results:
        #Plotting Radar/Spider diagram
        N = 5
        penta = radar_factory(N, frame='polygon')

        fig, axe = plt.subplots(figsize=(9, 9), nrows=1, ncols=1, subplot_kw=dict(projection='radar'))

        #for ax in axes:
        colors = ['g', 'b', 'y']
        for year, color in zip(person['years'], colors):
            axe.plot(penta, year['spiderScores'], color=color)
            axe.fill(penta, year['spiderScores'], facecolor=color, alpha=0.25)
            axe.set_varlabels(year['spiderScoreLabels'])
        axe.set_rgrids([1, 2, 3, 4, 5])

        #add legend relative to top-left plot
        y = []
        for year in person['years']:
            y.append(year['year'])
        legend = axe.legend(tuple(y), loc=(0.9, .95), labelspacing=0.1, fontsize='small')
        fig.text(0.5, 0.965, '', horizontalalignment='center', color='black', weight='bold', size='large')
        plt.savefig('plots/' + person['id'] + '.png')



#Creation of the Rader/Spider diagram
def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts


if __name__ == "__main__":
    main()
