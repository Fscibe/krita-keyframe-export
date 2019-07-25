import os
import krita
from pathlib import Path
from krita import (Extension, InfoObject)
from PyQt5.QtCore import (Qt, QSettings)
from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel,
                             QPushButton, QDialog, QLineEdit, QDialogButtonBox)


class KeyframeExporter(object):

    def export(self, exportDir, animName):
        doc = Krita.instance().activeDocument()
        if doc is not None:
            # record all frames with a keyframe
            frameCount = doc.animationLength()
            framesToExport = set([])
            root = doc.rootNode()
            for node in root.childNodes():
                if(node.animated() and node.visible()):
                    for i in range(frameCount-1):
                        if(node.hasKeyframeAtTime(i)):
                            framesToExport.add(i)

            # export keyframes
            doc.setBatchmode(True)
            for frame in framesToExport:
                doc.setCurrentTime(frame)

                fileNum = "_" + str(frame).zfill(3)
                exportPath = Path(exportDir)
                exportPath = exportPath.joinpath(animName + fileNum + ".png")

                doc.exportImage(str(exportPath), InfoObject())
            doc.setBatchmode(False)


class KeyframeExporterDialog(object):

    def __init__(self):
        self.app = krita.Krita.instance()
        self.exporter = KeyframeExporter()

        # dialog
        self.dialog = QDialog() #QDialog(self.app.activeWindow().qwindow())
        self.dialog.setWindowModality(Qt.WindowModal)
        self.dialog.setMinimumSize(400, 120)

        # controls
        self.exportDir = QLineEdit()
        self.exportDirBrowseButton = QPushButton("Browse")
        self.exportDirResetButton = QPushButton("Reset")
        self.exportDirOpenButton = QPushButton("Show")
        self.exportDirBrowseButton.clicked.connect(self.browseExportDir)
        self.exportDirResetButton.clicked.connect(self.resetExportDir)
        self.exportDirOpenButton.clicked.connect(self.openExportDir)
        self.exportDir.editingFinished.connect(self.onExportDirEditFinished)

        self.dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtonBox.accepted.connect(self.onConfirmButton)
        self.dialogButtonBox.rejected.connect(self.dialog.close)

        # layout
        self.mainLayout = QVBoxLayout(self.dialog)
        self.exportButtonsLayout = QHBoxLayout(self.dialog)
        self.addLabelledWidget("Export Dir", self.exportDir, self.mainLayout)
        self.exportButtonsLayout.addWidget(self.exportDirBrowseButton)
        self.exportButtonsLayout.addWidget(self.exportDirResetButton)
        self.exportButtonsLayout.addWidget(self.exportDirOpenButton)
        self.mainLayout.addLayout(self.exportButtonsLayout)
        self.mainLayout.addWidget(self.dialogButtonBox)

        # settings
        self.SETTINGS_EXPORT_PATH = "krita-keyframe-export/exportPath"


    def show(self):
        self.doc = self.app.activeDocument()

        # controls
        settings = QSettings()
        savedExportPath = settings.value(self.SETTINGS_EXPORT_PATH)
        if((savedExportPath is None) or (not savedExportPath)):
            self.resetExportDir()
        else:
            self.setExportDir(savedExportPath)

        # dialog
        self.dialog.setWindowTitle("Keyframe Exporter")
        self.dialog.show()
        self.dialog.activateWindow()


    def addLabelledWidget(self, text, widget, parentLayout):
        layout = QGridLayout()
        label = QLabel(text)
        label.setBuddy(widget)
        layout.addWidget(label, 0, 0)
        layout.addWidget(widget, 0, 1)
        layout.setAlignment(Qt.AlignLeft)
        parentLayout.addLayout(layout)
        return layout


    def browseExportDir(self):
        self.exportDirDialog = QFileDialog()
        self.exportDirDialog.setWindowTitle("Export Directory")
        self.exportDirDialog.setDirectory(str(self.exportPath))

        wantedPath = self.exportDirDialog.getExistingDirectory()
        if wantedPath != "":
            self.setExportDir(str(wantedPath))


    def resetExportDir(self):
        doc = Krita.activeDocument()
        if doc:
            pathString = str(Path(self.doc.fileName()).parents[0])
            self.setExportDir(pathString)


    def setExportDir(self, pathString):
        self.exportPath = Path(pathString)
        self.exportDir.setText(pathString)
        settings = QSettings()
        settings.setValue(self.SETTINGS_EXPORT_PATH, pathString)


    def onExportDirEditFinished(self):
        self.setExportDir(self.exportDir.text())


    def openExportDir(self):
        os.startfile(self.exportPath)


    def onConfirmButton(self):
        if(self.doc is not None):
            animName = os.path.splitext(os.path.basename(self.doc.fileName()))[0]
            self.exporter.export(self.exportPath, animName)
        self.dialog.hide()

		
class KeyframeExporterExtension(Extension):

    def __init__(self, parent):
        super().__init__()
        self.exporterDialog = KeyframeExporterDialog()

		
    def setup(self):
        pass

		
    def createActions(self, window):
        action = window.createAction("KeyframeExport", "Keyframe Export", "tools/scripts")
        action.triggered.connect(self.showDialog)

		
    def showDialog(self):
        self.exporterDialog.show()


# setup
debug = False
if(debug):
    # for iteration with Scripter
    exporterDialog = KeyframeExporterDialog()
    exporterDialog.show()
else:
    # register extension
    app=Krita.instance()
    Scripter.addExtension(KeyframeExporterExtension(app))
