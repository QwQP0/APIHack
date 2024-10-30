#################### Imports ####################

import sys

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
		## 변수 선언
		# 클래스 변수
		self.is_tab_reinited=False  # UI 재구성 여부
		# 전역 변수
		Global.main=self

		self.initUI()  # 기본 UI 구성

		self.setCentralWidget(self.main_tabs)  # 메인 위젯 설정

		# 화면 설정
		self.setWindowTitle('APIHACK')  #debug#
		self.setGeometry(960, 540, 480, 270) # 크기, 위치 설정  #debug#
		self.show()

	
	## 화면 구성
	# UI 구성
	def initUI(self):
		self.initMenu()  # 메뉴 바 구성
		self.initTab()  # 기본 탭 구성

		return
	# 메뉴 바 구성
	def initMenu(self):
		# 메뉴 구성
		self.menubar=QMenuBar()
		self.setMenuBar(self.menubar)  # 메뉴 바 설정
		self.menu_list={}
		
		## 파일 메뉴 구성
		self.menu_list["File"]=self.menubar.addMenu("File")
		# 파일 생성 액션 구성
		self.menu_list["File"].addAction("New..", QKeySequence(Qt.CTRL | Qt.Key_N))
		self.menu_list["File"].children()[1].triggered.connect(self.createProject)  # 함수 연결
		# 파일 불러오기 액션 구성
		self.menu_list["File"].addAction("Open..", QKeySequence(Qt.CTRL | Qt.Key_O))
		self.menu_list["File"].children()[2].triggered.connect(self.openProject)  # 함수 연결
		# 구분선
		self.menu_list["File"].addAction("").setSeparator(True)
		# 파일 저장 액션 구성
		self.menu_list["File"].addAction("Save", QKeySequence(Qt.CTRL | Qt.Key_S))
		self.menu_list["File"].children()[4].triggered.connect(self.saveCurProject)  # 함수 연결
		
		return
	# 기본 탭 구성
	def initTab(self):
		# 탭 위젯 선언
		self.main_tabs=QTabWidget()

		### 홈 탭
		self.home_tab=QWidget()
		self.main_tabs.addTab(self.home_tab, "HOME")
		self.home_tab_content=QVBoxLayout(self.home_tab)
		## 오브젝트 선언
		# 버튼 구역
		self.btn_div=QHBoxLayout()
		# 버튼
		self.crt_pj_btn=QPushButton("new project")
		self.open_pj_btn=QPushButton("open project")
		## UI 구성
		self.home_tab_content.addWidget(QLabel("Start Hack With ***"))
		self.home_tab_content.addWidget(QLabel("Start new project or open existing projects"))
		self.home_tab_content.addLayout(self.btn_div)  # 버튼 구역 추가
		self.btn_div.addWidget(self.crt_pj_btn)
		self.btn_div.addWidget(self.open_pj_btn)
		## 이벤트 연결
		self.crt_pj_btn.clicked.connect(self.createProject)
		self.open_pj_btn.clicked.connect(self.openProject)

		### 디코더 탭
		self.decoder_tab=QWidget()
		self.main_tabs.addTab(self.decoder_tab, "Decoder")
		Global.dcd=Decoder(self.decoder_tab)

		### 비교자 탭
		self.comparer_tab=QWidget()
		self.main_tabs.addTab(self.comparer_tab, "Comparer")
		Global.cmp=Comparer(self.comparer_tab)

		return
	# 탭 재구성(프로젝트 생성, 불러오기 시 수행)
	def reinitTab(self):
		self.main_tabs.removeTab(0)  # 홈 탭 제거

		## 사이드 뷰
		# 오브젝트 선언
		self.main_widget=QWidget()  # 메인 위젯 선언
		self.main_div=QHBoxLayout(self.main_widget)  # 메인 레이아웃; 메인 위젯 자식
		Global.sdv=SideView()  # 사이드뷰 선언
		# UI 援ъ꽦
		self.main_div.addLayout(Global.sdv.side_view_content)  # 메인 레이아웃에 사이드 뷰 추가
		self.main_div.addWidget(self.main_tabs)  # 메인 레이아웃에 탭 바 추가
		self.setCentralWidget(self.main_widget)  # 프로그램 메인 위젯 설정(기존 탭 바에서 (사이드 뷰+탭 바)의 부모 위젯으로 설정)

		## 요청 탭
		self.request_tab=QWidget()
		self.main_tabs.insertTab(0, self.request_tab, "Request")
		Global.req=Request(self.request_tab)

		## 변수 탭
		self.variables_tab=QWidget()
		self.main_tabs.insertTab(1, self.variables_tab, "Variables")
		Global.var=Variables(self.variables_tab)

		## 응답 탭
		self.response_tab=QWidget()
		self.main_tabs.insertTab(2, self.response_tab, "Response")

		return


	# 프로젝트, 요청 정보 탭에 적용
	def loadProject(self, project_name:str, request_name:str=None):
		if request_name==None:
			request_name=list(Global.projects_data[project_name]["requests"].keys())[0]  # 기본 요청(첫 번째 요청) 사용

		if Global.cur_request_name!="":  # 현재 탭에 적용된 요청 정보 있음
			# 현재 정보 저장
			Global.projects_data[Global.cur_project_name]["requests"][Global.cur_request_name]=Global.req.getTabInfo()  # 요청
			Global.projects_data[Global.cur_project_name]["variables"]=Global.var.getTabInfo()  # 변수
			Global.projects_data[Global.cur_project_name]["decoder"]=Global.dcd.getTabInfo()  # 디코더
			File.saveProject(Global.cur_project_name)  # 프로젝트 파일 저장

			Global.res[Global.cur_project_name][Global.cur_request_name].response_tab_content.setParent(None)  # 기존 응답 탭 위젯 탭 바에서 제외(삭제 아님)

		self.main_tabs.setCurrentIndex(0)  # 요청 탭으로 전환

		## 탭에 내용 적용
		Global.req.initUI(Global.projects_data[project_name]["requests"][request_name])  # 요청 탭에 내용 적용
		Global.var.initUI(Global.projects_data[project_name]["variables"])  # 변수 탭에 내용 적용
		Global.dcd.initUI(Global.projects_data[project_name]["decoder"])  # 디코더 탭에 내용 적용
		# 응답 탭에 내용 적용
		try:
			Global.res[project_name][request_name].response_tab_content.setParent(self.response_tab)  # 응답 탭 UI 갈아끼우기
		except:  # 응답 탭 UI 없음!
			Global.res[project_name][request_name]=Response()  # ?앹꽦
			Global.res[project_name][request_name].response_tab_content.setParent(self.response_tab)  # 응답 탭 UI 갈아끼우기

		Global.sdv.focusLabel(project_name, request_name)  # 하이라이트 적용
		
		#  현재 프로젝트, 요청 변경
		Global.cur_project_name=project_name
		Global.cur_request_name=request_name

		return


	## 프로젝트 관리
	# 프로젝트 생성 팝업
	def createProject(self):
		print("Main.CreateProject : create project popup")
		dialog=CreateProjectDialog()

		if dialog.return_data:
			is_file_created=File.createProject(dialog.return_data[0], dialog.return_data[1], dialog.return_data[2])  # 파일 생성

			if is_file_created:  # 파일 생성 성공
				if not self.is_tab_reinited:
					self.reinitTab()  # 탭 재구성
				Global.sdv.initUI(dialog.return_data[1])  # 사이드 뷰에 라벨 추가
				self.loadProject(dialog.return_data[1])  # 프로젝트 로드(프로젝트 이름)

		return
	# 프로젝트 불러오기
	def openProject(self):
		print("Main.openProject : open project")
		path= QFileDialog.getOpenFileName(self, 'Open file', './')

		if path[0]:
			path=path[0].split('/')
			project_path='/'.join(path[:len(path)-2])
			project_name=path[-1]

			if not project_name.split('.')[-1]=="ahp":  # 프로젝트 파일이 아닐 때
				print("Main.openProject : not project file")
			else:
				project_name='.'.join(project_name.split('.')[:len(project_name.split('.'))-1])
				is_project_opened=File.openProject(project_path, project_name)

				if is_project_opened:  # 열려있는 프로젝트
					if not self.is_tab_reinited:
						self.reinitTab()  # 탭 재구성
					Global.sdv.initUI(project_name)  # 사이드뷰에 라벨 추가
					self.loadProject(project_name)  # 프로젝트 로드

		return

		
##################### Dialog ####################

class CreateProjectDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.return_data=None
		
		self.initUI()
		self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

		self.exec()

		return
		

	# UI 초기 설정
	def initUI(self):
		self.pjpath_if_div=QVBoxLayout()
		self.pjname_if_div=QVBoxLayout()
		self.tgurl_if_div=QVBoxLayout()
		self.btn_div=QHBoxLayout()
			
		# 프로젝트 경로 입력 칸
		self.pjpath_if_div.addWidget(QLabel("Project Path"))
		self.pjpath_if_div.addLayout(QHBoxLayout())
		self.pjpath_if=QLineEdit(Global.default_project_path)
		self.pjpath_if.textChanged.connect(lambda :self.pjname_if.setText(File.setNameAuto("", self.pjpath_if.text(), 'p')))
		self.file_exp_btn=QPushButton("\\")
		self.file_exp_btn.clicked.connect(lambda :self.pjpath_if.setText(QFileDialog.getExistingDirectory(parent=self, caption="Set Directory")))
		# -> 기본 파일 경로 설정
		#todo# -> getOpenFileUrl 매개변수로 Global.default_project_path 넣기
		self.pjpath_if_div.children()[0].addWidget(self.pjpath_if)
		self.pjpath_if_div.children()[0].addWidget(self.file_exp_btn)
		
		# 프로젝트 이름 입력 칸
		self.pjname_if_div.addWidget(QLabel("Project Name"))
		self.pjname_if=QLineEdit(File.setNameAuto("", "", 'p'))
		self.pjname_if_div.addWidget(self.pjname_if)
		
		# 타겟 URL 입력 칸
		self.tgurl_if_div.addWidget(QLabel("Target Base URL"))
		self.tgurl_if=QLineEdit()
		self.tgurl_if_div.addWidget(self.tgurl_if)
		 
		# 버튼 그룹
		self.cancel_btn=QPushButton("cancel")
		self.crt_btn=QPushButton("new project")
		self.cancel_btn.clicked.connect(self.onclickCancel)
		self.crt_btn.clicked.connect(self.onclickCreate)
		self.btn_div.addWidget(self.cancel_btn)
		self.btn_div.addWidget(self.crt_btn)
		 
		# 전체 창
		self.this=QVBoxLayout()
		self.this.addLayout(self.pjpath_if_div)
		self.this.addLayout(self.pjname_if_div)
		self.this.addLayout(self.tgurl_if_div)
		self.this.addLayout(self.btn_div)
		self.setLayout(self.this)

		return
		

	## 버튼 클릭 이벤트
	# cancel 버튼 클릭
	def onclickCancel(self):
		self.close()
		return False
	# create 버튼 클릭
	def onclickCreate(self):
		self.return_data=[self.pjpath_if.text(), self.pjname_if.text(), self.tgurl_if.text()]
		self.close()
		return True










##debug#
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Main()
	sys.exit(app.exec())