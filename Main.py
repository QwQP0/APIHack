#################### Imports ####################

from email.policy import default
import sys

from PySide6.QtCore import QLine
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenuBar, QPushButton, QTabWidget, QVBoxLayout, QWidget
from PySide6.QtGui import QKeySequence, Qt

from Decoder import Decoder
from Comparer import Comparer
from Request import Request
from Response import Response
from SideView import SideView
from System import Global, File
from Variables import Variables

##################### Main ######################



class Main(QMainWindow):
	def __init__(self):
		super().__init__()
		## ���� ����
		# Ŭ���� ����
		self.is_tab_reinited=False  # UI �籸�� ����
		# ���� ����
		Global.main=self

		self.initUI()  # �⺻ UI ����

		self.setCentralWidget(self.main_tabs)  # ���� ���� ����

		# ȭ�� ����
		self.setWindowTitle('APIHACK')  #debug#
		self.setGeometry(480, 270, 960, 540) # ũ��, ��ġ ����  #debug#
		self.show()

	
	## ȭ�� ����
	# UI ����
	def initUI(self):
		self.initMenu()  # �޴� �� ����
		self.initTab()  # �⺻ �� ����

		return
	# �޴� �� ����
	def initMenu(self):
		# �޴� ����
		self.menubar=QMenuBar()
		self.setMenuBar(self.menubar)  # �޴� �� ����
		self.menu_list={}
		
		## ���� �޴� ����
		self.menu_list["File"]=self.menubar.addMenu("File")
		# ���� ���� �׼� ����
		self.menu_list["File"].addAction("New..", QKeySequence(Qt.CTRL | Qt.Key_N))
		self.menu_list["File"].children()[1].triggered.connect(self.createProject)  # �Լ� ����
		# ���� �ҷ����� �׼� ����
		self.menu_list["File"].addAction("Open..", QKeySequence(Qt.CTRL | Qt.Key_O))
		self.menu_list["File"].children()[2].triggered.connect(self.openProject)  # �Լ� ����
		# ���м�
		self.menu_list["File"].addAction("").setSeparator(True)
		
		return
	# �⺻ �� ����
	def initTab(self):
		# �� ���� ����
		self.main_tabs=QTabWidget()

		### Ȩ ��
		self.home_tab=QWidget()
		self.main_tabs.addTab(self.home_tab, "HOME")
		self.home_tab_content=QVBoxLayout(self.home_tab)
		## ������Ʈ ����
		# ��ư ����
		self.btn_div=QHBoxLayout()
		# ��ư
		self.crt_pj_btn=QPushButton("new project")
		self.open_pj_btn=QPushButton("open project")
		## UI ����
		self.home_tab_content.addWidget(QLabel("Start Hack With ***"))
		self.home_tab_content.addWidget(QLabel("Start new project or open existing projects"))
		self.home_tab_content.addLayout(self.btn_div)  # ��ư ���� �߰�
		self.btn_div.addWidget(self.crt_pj_btn)
		self.btn_div.addWidget(self.open_pj_btn)
		## �̺�Ʈ ����
		self.crt_pj_btn.clicked.connect(self.createProject)
		self.open_pj_btn.clicked.connect(self.openProject)

		### ���ڴ� ��
		self.decoder_tab=QWidget()
		self.main_tabs.addTab(self.decoder_tab, "Decoder")
		Global.dcd=Decoder(self.decoder_tab)

		### ���� ��
		self.comparer_tab=QWidget()
		self.main_tabs.addTab(self.comparer_tab, "Comparer")
		Global.cmp=Comparer(self.comparer_tab)

		return
	# �� �籸��(������Ʈ ����, �ҷ����� �� ����)
	def reinitTab(self):
		self.main_tabs.removeTab(0)  # Ȩ �� ����

		## ���̵� ��
		# ������Ʈ ����
		self.main_widget=QWidget()  # ���� ���� ����
		self.main_div=QHBoxLayout(self.main_widget)  # ���� ���̾ƿ�; ���� ���� �ڽ�
		Global.sdv=SideView()  # ���̵�� ����
		# UI ����
		self.main_div.addLayout(Global.sdv.side_view_content)  # ���� ���̾ƿ��� ���̵� �� �߰�
		self.main_div.addWidget(self.main_tabs)  # ���� ���̾ƿ��� �� �� �߰�
		self.setCentralWidget(self.main_widget)  # ���α׷� ���� ���� ����(���� �� �ٿ��� (���̵� ��+�� ��)�� �θ� �������� ����)

		## ��û ��
		self.request_tab=QWidget()
		self.main_tabs.insertTab(0, self.request_tab, "Request")
		Global.req=Request(self.request_tab)

		## ���� ��
		self.variables_tab=QWidget()
		self.main_tabs.insertTab(1, self.variables_tab, "Variables")
		Global.var=Variables(self.variables_tab)

		## ���� ��
		self.response_tab=QWidget()
		self.main_tabs.insertTab(2, self.response_tab, "Response")

		self.is_tab_reinited=True

		return


	# ������Ʈ, ��û ���� �ǿ� ����
	def loadProject(self, project_name:str, request_name:str=None):
		if request_name==None:
			request_name=list(Global.projects_data[project_name]["requests"].keys())[0]  # �⺻ ��û(ù ��° ��û) ���

		if Global.cur_request_name!="":  # ���� �ǿ� ����� ��û ���� ����
			# ���� ���� ����
			Global.projects_data[Global.cur_project_name]["requests"][Global.cur_request_name]=Global.req.getTabInfo()  # ��û
			Global.projects_data[Global.cur_project_name]["variables"]=Global.var.getTabInfo()  # ����
			Global.projects_data[Global.cur_project_name]["decoder"]=Global.dcd.getTabInfo()  # ���ڴ�
			File.saveProject(Global.cur_project_name)  # ������Ʈ ���� ����

			Global.res[Global.cur_project_name][Global.cur_request_name].response_tab_content.setParent(None)  # ���� ���� �� ���� �� �ٿ��� ����(���� �ƴ�)

		self.main_tabs.setCurrentIndex(0)  # ��û ������ ��ȯ

		## �ǿ� ���� ����
		Global.req.initUI(Global.projects_data[project_name]["requests"][request_name])  # ��û �ǿ� ���� ����
		Global.var.initUI(Global.projects_data[project_name]["variables"])  # ���� �ǿ� ���� ����
		Global.dcd.initUI(Global.projects_data[project_name]["decoder"])  # ���ڴ� �ǿ� ���� ����
		# ���� �ǿ� ���� ����
		try:
			Global.res[project_name][request_name].response_tab_content.setParent(self.response_tab)  # ���� �� UI ���Ƴ����
		except:  # ���� �� UI ����!
			Global.res[project_name][request_name]=Response()  # ���� ��
			Global.res[project_name][request_name].response_tab_content.setParent(self.response_tab)  # ���� �� UI ���Ƴ����

		Global.sdv.focusLabel(project_name, request_name)  # ���̶���Ʈ ����
		
		#  ���� ������Ʈ, ��û ����
		Global.cur_project_name=project_name
		Global.cur_request_name=request_name

		return


	## ������Ʈ ����
	# ������Ʈ ���� �˾�
	def createProject(self):
		print("Main.CreateProject : create project popup")
		dialog=CreateProjectDialog()

		if dialog.return_data:
			# �̸� ��ȿ �˻�
			if File.isInvalidName(dialog.return_data[1]):  # ��ȿ���� ���� �̸�
				#todo# �˸�
				return

			is_file_created=File.createProject(dialog.return_data[0], dialog.return_data[1], dialog.return_data[2])  # ���� ����

			if is_file_created:  # ���� ���� ����
				if not self.is_tab_reinited:
					self.reinitTab()  # �� �籸��
				Global.sdv.initUI(dialog.return_data[1])  # ���̵� �信 �� �߰�
				self.loadProject(dialog.return_data[1])  # ������Ʈ �ε�(������Ʈ �̸�)

		return
	# ������Ʈ �ҷ�����
	def openProject(self):
		print("Main.openProject : open project")
		path= QFileDialog.getOpenFileName(self, 'Open file', './')

		if path[0]:
			path=path[0].split('/')
			project_path='/'.join(path[:len(path)-2])
			project_name=path[-1]

			if not project_name.split('.')[-1]=="ahp":  # ������Ʈ ������ �ƴ� ��
				print("Main.openProject : not project file")
			else:
				project_name='.'.join(project_name.split('.')[:len(project_name.split('.'))-1])
				is_project_opened=File.openProject(project_path, project_name)

				if is_project_opened:  # �����ִ� ������Ʈ
					if not self.is_tab_reinited:
						self.reinitTab()  # �� �籸��
					Global.sdv.initUI(project_name)  # ���̵�信 �� �߰�
					self.loadProject(project_name)  # ������Ʈ �ε�

		return

		
##################### Dialog ####################

class CreateProjectDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.return_data=None
		
		self.initUI()

		self.exec()

		return
		

	# UI �ʱ� ����
	def initUI(self):
		## ������Ʈ ����
		self.this=QVBoxLayout()
		# ����
		self.pjpath_if_div=QVBoxLayout()
		self.pjname_if_div=QVBoxLayout()
		self.tgurl_if_div=QVBoxLayout()
		self.btn_div=QHBoxLayout()
		# �Է� ĭ
		self.pjpath_if=QLineEdit(Global.default_project_path)
		self.pjname_if=QLineEdit(File.setNameAuto("", "", 'p'))
		self.tgurl_if=QLineEdit()
		# ��ư
		self.file_exp_btn=QPushButton("\\")
		self.crt_btn=QPushButton("new project")
		self.cancel_btn=QPushButton("cancel")
		# ��
		self.error_text=QLabel()
		
		## ������Ʈ ����
		# ������Ʈ ��� �Է� ����
		self.pjpath_if_div.addWidget(QLabel("Project Path"))
		self.pjpath_if_div.addLayout(QHBoxLayout())
		self.pjpath_if_div.children()[0].addWidget(self.pjpath_if)
		self.pjpath_if_div.children()[0].addWidget(self.file_exp_btn)
		# ������Ʈ �̸� �Է� ����
		self.pjname_if_div.addWidget(QLabel("Project Name"))
		self.pjname_if_div.addWidget(self.pjname_if)
		self.pjname_if_div.addWidget(self.error_text)
		# Ÿ�� URL �Է� ����
		self.tgurl_if_div.addWidget(QLabel("Target Base URL"))
		self.tgurl_if_div.addWidget(self.tgurl_if)
		# ��ư ����
		self.btn_div.addWidget(self.crt_btn)
		self.btn_div.addWidget(self.cancel_btn)
		# ��ü â
		self.this.addLayout(self.pjpath_if_div)
		self.this.addLayout(self.pjname_if_div)
		self.this.addLayout(self.tgurl_if_div)
		self.this.addLayout(self.btn_div)
		self.setLayout(self.this)
		
		## �̺�Ʈ ����
		# ��ư
		self.crt_btn.clicked.connect(self.onclickCreate)
		self.cancel_btn.clicked.connect(self.onclickCancel)
		self.file_exp_btn.clicked.connect(lambda :self.pjpath_if.setText(QFileDialog.getExistingDirectory(parent=self, caption="Set Directory")))
		# -> �⺻ ���� ��� ����
		#todo# -> �Ű������� Global.default_project_path �ֱ�
		# �ؽ�Ʈ ����
		self.pjpath_if.textChanged.connect(lambda :self.pjname_if.setText(File.setNameAuto("", self.pjpath_if.text(), 'p')))
		self.pjname_if.textChanged.connect(self.checkInvaildName)

		## ��Ÿ ����
		self.error_text.setStyleSheet("color:#c33")
		self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

		return
		

	### �̺�Ʈ
	## ��ư Ŭ�� �̺�Ʈ
	# create ��ư Ŭ��
	def onclickCreate(self):
		self.return_data=[self.pjpath_if.text(), self.pjname_if.text(), self.tgurl_if.text()]
		self.close()

		return True
	# cancel ��ư Ŭ��
	def onclickCancel(self):
		self.close()

		return False
	## �ؽ�Ʈ ����
	# ������Ʈ �̸� ���� ��
	def checkInvaildName(self):
		if File.isInvalidName(self.pjname_if.text(), self.pjpath_if.text(), 'p'):
			self.error_text.setText("Invalid name")  #todo# �������� ���� ����
			self.crt_btn.setDisabled(True)  # ��ư ��Ȱ��ȭ
		else:
			self.error_text.setText("")
			self.crt_btn.setDisabled(False)

		return
		
		










#debug#
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Main()

	File.openProject("E:/__apihack test", "My project")
	Global.main.reinitTab()
	Global.sdv.initUI("My project")
	Global.main.loadProject("My project")

	File.openProject("E:/__apihack test", "My project(1)")
	Global.sdv.initUI("My project(1)")
	Global.main.loadProject("My project(1)")

	sys.exit(app.exec())
#debug#