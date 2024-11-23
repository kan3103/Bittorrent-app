# Form implementation generated from reading ui file 'download.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

import os
from PyQt6 import QtCore, QtGui, QtWidgets
import socket
import bencodepy
import request
import files

class DownloadThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()

    def __init__(self, progress, status, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.progress = progress
        self.status = status

    def run(self):
        for i in range(10):
            if not self.is_running:
                self.progress_updated.emit(0)
                self.finished.emit()
                return
            self.progress.setValue((i + 1) * 10)
            QtCore.QThread.sleep(1)  
        self.status.setText("Done")
        self.finished.emit() 


    def stop(self):
        self.is_running = False

class TableTorrrent(QtWidgets.QTableWidget):
    def __init__(self, parent=None,bool=False):
        super(TableTorrrent, self).__init__(parent)
        if bool:
            self.setColumnCount(7)
            self.setHorizontalHeaderLabels(["ID","Choose","Name", "Size", "Done", "Status", "Peers"])
            self.setColumnWidth(1, 50)
            self.setColumnWidth(2, 107)
            self.setColumnWidth(3, 90)
            self.setColumnWidth(4, 200)
            self.setColumnWidth(5, 90)
            self.setColumnWidth(6, 90)
            self.setColumnWidth(0, 70)
        else:
            self.setColumnCount(3)
            self.setHorizontalHeaderLabels(["Name","Size", "Status"])
            self.setColumnWidth(0, 150)
            self.setColumnWidth(1, 107)
            self.setColumnWidth(2, 90)
    def add_row_to_table(self, filename, size, status, progress,id):
        row_position = self.rowCount()
        self.insertRow(row_position)

        item_id = QtWidgets.QTableWidgetItem("TRT" + str(id))
        item_filename = QtWidgets.QTableWidgetItem(filename)
        item_size = QtWidgets.QTableWidgetItem(size)
        item_status = QtWidgets.QTableWidgetItem(status)

        item_id.setFlags(item_id.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        item_filename.setFlags(item_filename.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        item_size.setFlags(item_size.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        item_status.setFlags(item_status.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)

        
        self.setItem(row_position, 0, item_id)
        self.setItem(row_position, 2, item_filename)
        self.setItem(row_position, 3, item_size)
        self.setItem(row_position, 5, item_status)

        progress_widget = QtWidgets.QProgressBar()
        progress_widget.setValue(progress)
        self.setCellWidget(row_position, 4, progress_widget)
        
        checkBox = QtWidgets.QCheckBox()
        self.setCellWidget(row_position, 1, checkBox)
        
        return progress_widget,item_status
    def add_file_to_table(self, filename, size, status):
        row_position = self.rowCount()
        self.insertRow(row_position)

        item_filename = QtWidgets.QTableWidgetItem(filename)
        item_size = QtWidgets.QTableWidgetItem(str(size))
        item_status = QtWidgets.QTableWidgetItem(status)

        item_filename.setFlags(item_filename.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        item_size.setFlags(item_size.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
        item_status.setFlags(item_status.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
    
        self.setItem(row_position, 0, item_filename)
        self.setItem(row_position, 1, item_size)
        self.setItem(row_position, 2, item_status)
        

class Ui_MainWindow(object):
    local_ip = ""
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        
        self.id = 1
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.textfile = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.textfile.setGeometry(QtCore.QRect(400, 40, 256, 21))
        self.textfile.setObjectName("textfile")

        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.clicked.connect(self.open_file_dialog)
        self.pushButton.setGeometry(QtCore.QRect(670, 40, 100, 21))
        self.pushButton.setObjectName("pushButton")
        
        
        self.tableWidget = TableTorrrent(parent=self.centralwidget,bool=True)
        self.tableWidget.setGeometry(QtCore.QRect(50, 120, 721, 192))
        
        self.tableWidget.cellClicked.connect(self.cell_clicked)
        
        self.infofile = files.Torrent_file()
        
        
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 40, 47, 21))
        self.label.setObjectName("label")
        
        self.textBrowser_2 = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.textBrowser_2.setGeometry(QtCore.QRect(100, 40, 151, 21))
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(260, 40, 47, 21))
        self.label_2.setObjectName("label_2")
        self.textBrowser_3 = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.textBrowser_3.setGeometry(QtCore.QRect(290, 40, 91, 21))
        self.textBrowser_3.setObjectName("textBrowser_3")
        
        
        self.tableFile = TableTorrrent(parent=self.centralwidget,bool=False)
        self.tableFile.setGeometry(QtCore.QRect(50, 340, 721, 192))
        # self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        # self.pushButton_2.setGeometry(QtCore.QRect(690, 150, 75, 23))
        # self.pushButton_2.setObjectName("pushButton_2")
        # self.label_8 = QtWidgets.QLabel(parent=self.centralwidget)
        # self.label_8.setGeometry(QtCore.QRect(80, 340, 71, 16))
        # self.label_8.setObjectName("label_8")
        # self.textBrowser_8 = QtWidgets.QTextBrowser(parent=self.centralwidget)
        # self.textBrowser_8.setGeometry(QtCore.QRect(170, 340, 111, 21))
        # self.textBrowser_8.setObjectName("textBrowser_8")
        # self.listWidget = QtWidgets.QListWidget(parent=self.centralwidget)
        # self.listWidget.setGeometry(QtCore.QRect(90, 390, 661, 111))
        # self.listWidget.setObjectName("listWidget")
        # self.progressBar_2 = QtWidgets.QProgressBar(parent=self.centralwidget)
        # self.progressBar_2.setGeometry(QtCore.QRect(180, 420, 461, 23))
        # self.progressBar_2.setProperty("value", 24)
        # self.progressBar_2.setObjectName("progressBar_2")
        # self.label_9 = QtWidgets.QLabel(parent=self.centralwidget)
        # self.label_9.setGeometry(QtCore.QRect(100, 400, 47, 14))
        # self.label_9.setObjectName("label_9")
        # self.label_10 = QtWidgets.QLabel(parent=self.centralwidget)
        # self.label_10.setGeometry(QtCore.QRect(680, 400, 47, 14))
        # self.label_10.setObjectName("label_10")
        # self.label_11 = QtWidgets.QLabel(parent=self.centralwidget)
        # self.label_11.setGeometry(QtCore.QRect(350, 400, 47, 14))
        # self.label_11.setObjectName("label_11")
        
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(610, 90, 75, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(690, 90, 75, 23))
        self.pushButton_4.setObjectName("pushButton_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionCreate_torrent = QtGui.QAction(parent=MainWindow)
        self.actionCreate_torrent.setObjectName("actionCreate_torrent")
        self.actionClose = QtGui.QAction(parent=MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.menuFile.addAction(self.actionCreate_torrent)
        self.menuFile.addAction(self.actionClose)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        
    def update_progress(self,value,progress):
        progress.setValue(value)

    def cell_clicked(self, row, column):
        print(f"Clicked cell at row {row}, column {column}")

        widget = self.tableWidget.cellWidget(row, column)
        id = self.tableWidget.item(row, 0).text()
        tablefile = self.infofile.get(id)
        self.tableFile.setRowCount(0)
        for file in tablefile["files"]:
            self.tableFile.add_file_to_table(file['name'], file['size'], file['status'])
        if widget:
            if isinstance(widget, QtWidgets.QCheckBox):
                print(f"Checkbox clicked, isChecked: {widget.isChecked()}")
            elif isinstance(widget, QtWidgets.QProgressBar):
                print(f"ProgressBar clicked, value: {widget.value()}")
        else:
            item = self.tableWidget.item(row, column)
            if item:
                print(f"Cell text: {item.text()}")
                
    def open_file_dialog(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Choose a file to upload", "", "All Files (*.*)")
            
        if file_path:
            self.textfile.setText(file_path)
            # Đọc file .torrent
            try:
                with open(file_path, 'rb') as f:
                    torrent_data = bencodepy.decode(f.read())
            except Exception as e:
                print(f"Plese choose a torrent file")
                return
            
            
            
            url = torrent_data[b'announce'].decode()
            info_bencoded = bencodepy.encode(torrent_data[b'info'])
            info_hash=request.hash_info(info_bencoded)     
            if self.infofile.check(info_hash): # check torrent trùng
                print("Torrent is already in the list")  
                return
            try:    
                response = request.send_started_request(url, info_hash,self.local_ip, 6881)
                if response[0] == 200:
                    file_name = os.path.basename(file_path)
                    progress,status=self.tableWidget.add_row_to_table(file_name, "100MB", "Downloading", 0,id=self.id)
                    
                    self.infofile.add("TRT"+str(self.id),torrent_data) # Thêm file torrent vào list
                    
                    self.download_thread = DownloadThread(progress,status)
                    self.id += 1
                    self.download_thread.start()
            except Exception as e:
                print(f"Error: {e}")

    def get_local_ip(self):
        try:
            hostname = "8.8.8.8"  
            port = 80
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect((hostname, port))
                self.local_ip = s.getsockname()[0]
            self.textBrowser_2.setText(self.local_ip)
        except Exception as e:
            print(f"Error: {e}")
            
    
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Dowload torrent"))
        self.label.setText(_translate("MainWindow", "Your IP"))
        self.label_2.setText(_translate("MainWindow", "Port"))
        # self.pushButton_2.setText(_translate("MainWindow", "Upload "))
        # self.label_8.setText(_translate("MainWindow", "Tracker url"))
        # self.label_9.setText(_translate("MainWindow", "Name"))
        # self.label_10.setText(_translate("MainWindow", "Size"))
        # self.label_11.setText(_translate("MainWindow", "Done"))
        self.pushButton_3.setText(_translate("MainWindow", "Pause"))
        self.pushButton_4.setText(_translate("MainWindow", "Cancel"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionCreate_torrent.setText(_translate("MainWindow", "Create torrent"))
        self.actionClose.setText(_translate("MainWindow", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.get_local_ip()
    MainWindow.show()
    sys.exit(app.exec())
