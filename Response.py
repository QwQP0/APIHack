#################### Imports ####################


from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget
import requests

from System import Global, deleteObject


##################### Main ######################



class Response:
	def __init__(self):
		self.response_tab_content=QWidget()
		self.response_tab_content_layout=QVBoxLayout(self.response_tab_content)
		self.response_table:QVBoxLayout=ResponseController.initUI(self.response_tab_content_layout)

		self.response_data=[]

		return


	# 기존 데이터 제거
	def clearData(self):
		self.response_data=[]
		ResponseController.clearTable(self.response_table)

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(0+" responses")  # 응답 수 표시 라벨 변경

		return


	# 행 추가
	def addRow(self, response_time:float, response_data:requests.Response):
		self.response_data.append((response_time, response_data))  # 데이터 추가
		self.response_table.insertWidget(1, ResponseController.initRow(len(self.response_data), response_time, response_data))  # 테이블 최상단(라벨 바로 아래)에 삽입

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(str(self.response_data)+" responses")  # 응답 수 표시 라벨 변경

		return



class ResponseController:
	## 탭 구성
	# UI 구성
	def initUI(parent:QBoxLayout) -> QVBoxLayout:
		### 오브젝트 선언
		## 상단
		top_div=QHBoxLayout()
		filter_btn=QPushButton("#")  # 필터 버튼
		## 테이블 구역
		response_table=QVBoxLayout()
		# 테이블 라벨
		table_labels=QHBoxLayout()

		### UI 구성
		## 상단 구성
		top_div.addWidget(QLabel("0"+" responses"))  # 응답 수 표시 라벨
		top_div.addWidget(filter_btn)
		## 테이블 라벨 구성
		table_labels.addWidget(QLabel("No."))  # 번호
		table_labels.addWidget(QLabel("Response Code"))  # 응답 코드
		table_labels.addWidget(QLabel("Length"))  # 응답 길이
		table_labels.addWidget(QLabel("Response Time"))  # 응답 소요 시간
		## 탭 구성
		response_table.addLayout(table_labels)  # 테이블 라벨 조립
		parent.addLayout(top_div)
		parent.addLayout(response_table)

		return response_table
	# 응답 테이블 행 구성
	def initRow(num:int, response_time:float, response_data:requests.Response) -> QWidget:
		new_row_widget=QWidget()
		new_row=QHBoxLayout(new_row_widget)

		new_row.addWidget(QLabel(str(num)))  # 번호
		new_row.addWidget(QLabel(str(response_data.status_code)))  # 응답 코드
		new_row.addWidget(QLabel(str(len(response_data.content))))  # 응답 길이
		new_row.addWidget(QLabel(str(response_time)))  # 응답 소요 시간

		return new_row_widget
	# 응답 테이블 비움
	def clearTable(response_table:QVBoxLayout):
		for i in range(1, response_table.count()):
			for j in range(response_table.itemAt(0).widget().findChild(QHBoxLayout).count()):
				deleteObject(response_table.itemAt(0).widget().findChild(QHBoxLayout).itemAt(0).widget())  # 번호, 응답 코드, 응답 길이, 응답 시간 라벨 삭제
			#deleteObject(response_table.itemAt(0).widget().findChild(QHBoxLayout))  # 행 레이아웃 삭제
			deleteObject(response_table.itemAt(0).widget())  # 행 삭제

		return



	class Loading(QThread):
		pass



	class Filter(QWidget):
		pass



# 응답 내용 팝업
class ResponseView():
	def __init__(self, project_name:str=None, request_name:str=None, saved_name:str=None, index:int=-1):
		self.initUI()  # UI 구성

		if index==-1:  # 저장된 파일 열기
			project_path=Global.projects_data[project_name]["last_path"]

			saved_data=open(project_path+'/'+project_name+'/saved/'+saved_name+".rsv")  # 파일 열기
			self.contents.setPlainText(saved_data.read())
			saved_data.close()  # 파일 닫기
		else:
			self.contents.setPlainText(Global.res[project_name][request_name].response_data[index][1].text)
			# -> Response클래스->응답 데이터 리스트->응답 데이터


	def initUI(self) -> None:
		## 오브젝트 선언
		self.dialog=QWidget()
		self.window=QVBoxLayout()
		# 헤더
		self.header_div=QHBoxLayout()
		self.switch=QHBoxLayout()
		self.raw_switch=QPushButton("raw")
		self.pretty_switch=QPushButton("pretty")
		self.comparer_btn=QPushButton("Comparer")
		self.close_btn=QPushButton("X")
		# 바디
		self.body_div=QHBoxLayout()
		self.contents=QTextEdit()

		## 오브젝트 구성
		# 스위치 조립
		self.switch.addWidget(self.raw_switch)
		self.switch.addWidget(self.pretty_switch)
		self.header_div.addLayout(self.switch)  # 헤더 그룹에 스위치 추가
		self.header_div.addWidget(self.comparer_btn)
		self.header_div.addWidget(self.close_btn)
		self.body_div.addWidget(self.contents)
		# 화면 구성
		self.window.addLayout(self.header_div)
		self.window.addLayout(self.body_div)
		self.dialog.setLayout(self.window)
		self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
		self.dialog.setFixedSize(1280, 720)  # 화면 크기

		## 이벤트 연결
		# 스위치 연결
		self.raw_switch.clicked.connect(self.switching_raw)
		self.pretty_switch.clicked.connect(self.switching_pretty)
		# 비교자로 보내기 버튼 연결
		#todo# 비교자로 보내기
		# 닫기 버튼 연결
		self.close_btn.clicked.connect(self.dialog.close)
		# 드래그 이벤트 연결
		self.dialog.mousePressEvent=self.mousePressEvent
		self.dialog.mouseMoveEvent=self.mouseMoveEvent
		self.dialog.mouseReleaseEvent=self.mouseReleaseEvent

		## 기타 설정
		# 스위치 설정
		self.raw_switch.setCheckable(True)
		self.raw_switch.setChecked(True)  # raw 상태로 기본 설정
		self.pretty_switch.setCheckable(True)
		# 텍스트 영역 설정
		self.contents.setReadOnly(True)  # 읽기 전용
			
		## 실행
		self.dialog.show()
		self.dialog.destroyed.connect(lambda : print("close"))  # 닫을 때 close 출력

		return



	### 이벤트
	## raw-pretty 스위치
	# raw로 전환
	def switching_raw(self) -> None:
		if self.raw_switch.isChecked():
			return

		# 포커스 변경
		self.raw_switch.setChecked(True)
		self.pretty_switch.setChecked(False)
		
		self.contents.setPlainText(self.contents.toPlainText())  # 텍스트 입력

		return
	# pretty로 전환
	def switching_pretty(self) -> None:
		if self.pretty_switch.isChecked():
			return

		# 포커스 변경
		self.raw_switch.setChecked(False)
		self.pretty_switch.setChecked(True)

		self.contents.setPlainText(self.contents.toPlainText())  # 텍스트 입력

		return
	## 창 드래그
	# 마우스 클릭
	def mousePressEvent(self, event: QMouseEvent) -> None:
		self.mouse_start_postion=event.globalPos()  # 클릭 위치 저장
		self.widget_position=self.dialog.pos()  # 창 위치 저장

		return
	# 마우스 이동
	def mouseMoveEvent(self, event: QMouseEvent) -> None:
		if self.mouse_start_postion!=None:  # 클릭 되어있을 때
			# 계속 드래그
			self.dialog.move(self.widget_position.x()+event.globalPos().x()-self.mouse_start_postion.x(), \
			self.widget_position.y()+event.globalPos().y()-self.mouse_start_postion.y())

		return
	# 마우스 놓음
	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		self.mouse_start_postion=None
		
		return

