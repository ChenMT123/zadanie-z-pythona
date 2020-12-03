import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
import numpy as np
from scipy import signal
import pandas as pd
import pyqtgraph as pg
from scipy.fft import fft
from PyQt5 import QtGui
from PyQt5 import QtCore

class Generator():

    def setLinSpace(self, min, max, step):
        self.t =np.linspace(min, max, step)

    def Sine(self):
        self.data= self.A * np.sin(2 * np.pi * self.f * self.t)

    def Square(self):
        self.data= self.A*signal.square(2 * np.pi * self.f * self.t)

    def Sawtooth(self):
        self.data= self.A*signal.sawtooth(2 * np.pi * self.f * self.t)

    def Triangle(self):
        self.data= self.A*signal.sawtooth(2 * np.pi * self.f * self.t, 0.5)

    def WhiteNoise(self):
        self.data= self.A*(np.random.rand(len(self.t))-0.5)*2



class App(QWidget):
    def __init__(self):
        self.generator = Generator()
        super().__init__()


        self.left = 100
        self.top= 100
        self.width=  2000
        self.height= 1000
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.title='Generator'
        self.setWindowTitle(self.title)
        self.Init_UI()
        self.setLayout(self.layout)






        save = QAction('save',self)
        save.triggered.connect(lambda: self.SaveCsv())

        self.menuBar = QMenuBar(self)
        self.layout.setMenuBar(self.menuBar)

        calculateMenu = self.menuBar.addMenu('File')
        calculateMenu.addAction(save)



        self.show()
    def Init_UI(self):
        self.layout = QGridLayout()
        self.datalay= QGridLayout()
        self.setWindowIcon(QtGui.QIcon('cheems.png'))

        self.table = QTableWidget(self)
        self.layout.addWidget(self.table,0,1 )
        self.table.setFixedWidth(200)

        self.zakres = QDoubleSpinBox(self)
        self.datalay.addWidget(self.zakres, 0,1)
        self.zakrestyt = QLabel(self)
        self.zakrestyt.setText('Zakres')
        self.datalay.addWidget(self.zakrestyt, 0, 0)
        self.zakres.setValue(10)

        self.step = QSpinBox(self)
        self.datalay.addWidget(self.step, 1,1)
        self.step.setMaximum(99999999)
        self.steptyt = QLabel(self)
        self.steptyt.setText('Ilość kroków')
        self.datalay.addWidget(self.steptyt, 1,0)
        self.step.setValue(8000)

        self.Amplituda = QDoubleSpinBox(self)
        self.datalay.addWidget(self.Amplituda, 2,1)
        self.Amplituda.setRange(0, 1)
        self.Amplitudatyt = QLabel(self)
        self.Amplitudatyt.setText('Amplituda')
        self.datalay.addWidget(self.Amplitudatyt, 2,0)
        self.Amplituda.setValue(0.5)
        self.Amplituda.valueChanged.connect(lambda: self.Compile(self.cb.currentText()))

        self.freq = QDoubleSpinBox(self)
        self.datalay.addWidget(self.freq, 3,1)
        self.freq.setRange(0, 20000)
        self.freqtyt = QLabel(self)
        self.datalay.addWidget(self.freqtyt, 3,0)
        self.freqtyt.setText('Częstotliwość')
        self.freq.setValue(440)
        self.freq.valueChanged.connect(lambda: self.Compile(self.cb.currentText()))

        self.cb= QComboBox()
        self.cb.addItem('Sine')
        self.cb.addItem('Square')
        self.cb.addItem('Triangle')
        self.cb.addItem('Sawtooth')
        self.cb.addItem('WhiteNoise')
        self.cb.currentIndexChanged.connect(lambda: self.Compile(self.cb.currentText()))
        self.datalay.addWidget(self.cb,4,0,1,2)

        self.layout.addLayout(self.datalay,0,0)
        self.signal= pg.PlotWidget()
        self.signal.setLabel('left', text='<font size =20> A </font>')
        self.signal.setLabel('bottom', text='<font size =20> time [s] </font>')
        self.layout.addWidget(self.signal,0,2)

        self.fourier=pg.PlotWidget()
        self.fourier.setLabel('left', text='<font size=20> A </font>')
        self.fourier.setLabel('bottom', text='<font size=20> Hz </font>')
        self.layout.addWidget(self.fourier,0,3)
        self.Compile(self.cb.currentText())


    def Set_Table(self):
        self.table.setRowCount(len(self.generator.t))
        self.table.setColumnCount(2)
        for i in range(0,len(self.generator.t)):
            item0=QTableWidgetItem(str(self.generator.t[i]))
            item1=QTableWidgetItem(str(self.generator.data[i]))
            self.table.setItem(i,0, item0)
            self.table.setItem(i,1,item1)


    def Set_Graphs(self):
        x=self.generator.t
        y=self.generator.data
        self.signal.clear()
        self.signal.plot(x,y)
        self.signal.setYRange(-self.Amplituda.value(),self.Amplituda.value())
        self.signal.setXRange(0, 100/1000)
        N = len(self.generator.t)
        dt = self.generator.t[1] - self.generator.t[0]
        yf = 2.0 / N * np.abs(fft(self.generator.data)[0:N // 2])
        xf = np.fft.fftfreq(N, d=dt)[0:N // 2]
        self.fourier.clear()
        self.fourier.plot(xf,yf)
        self.fourier.setXRange(0,self.freq.value()+200)





    def Compile(self, a):
        self.generator.A=self.Amplituda.value()
        self.generator.f=self.freq.value()
        func=getattr(self.generator, a)
        self.generator.setLinSpace(0,self.zakres.value(),self.step.value())
        func()
        self.Set_Table()
        self.Set_Graphs()

    def SaveCsv(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "save", "Wave.csv","CSV File(*csv)", options=options)
        save = {"t": self.generator.t, "y": self.generator.data}
        dataframe = pd.DataFrame(save)
        dataframe.to_csv(fileName, index=False, sep="\t")



app = QApplication(sys.argv)
ex = App()
app.exec()