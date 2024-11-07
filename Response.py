#################### Imports ####################


from PySide6 import QtGui
from PySide6.QtCore import QEvent, QLine, QObject, QThread, Qt, Signal
from PySide6.QtGui import QAction, QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QCheckBox, QComboBox, QDialog, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListView, QListWidget, QListWidgetItem, QMenu, QPushButton, QTextEdit, QVBoxLayout, QWidget
import requests

from System import CONST, Global, deleteObject


##################### Main ######################



class Response:
	def __init__(self):
		self.response_tab_content=QWidget()
		self.response_tab_content_layout=QVBoxLayout(self.response_tab_content)
		self.response_tab_content.resize(300, 100)
		self.response_table:QVBoxLayout=ResponseController.initUI(self.response_tab_content_layout)

		self.res_filter=ResponseFilter()

		self.response_data=[]

		return


	# 기존 데이터 제거
	def clearData(self):
		self.response_data=[]
		ResponseController.clearTable()

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(str(0)+" responses")  # 응답 수 표시 라벨 변경

		return


	# 행 추가
	def addRow(self, response_time:float, response_data:requests.Response):
		self.response_data.append((response_time, response_data))  # 데이터 추가
		self.response_table.insertWidget(1, ResponseController.initRow(len(self.response_data), response_time, response_data))  # 테이블 최상단(라벨 바로 아래)에 삽입

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(str(len(self.response_data))+" responses")  # 응답 수 표시 라벨 변경

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

		### 이벤트 연결
		## 버튼 이벤트
		# 필터 버튼 클릭 시
		filter_btn.clicked.connect(lambda: ResponseController.openFilter(filter_btn, Global.res[Global.cur_project_name][Global.cur_request_name].filter_data))

		return response_table
	# 응답 테이블 행 구성
	def initRow(num:int, response_time:float, response_data:requests.Response) -> QWidget:
		new_row_widget=QWidget()
		new_row_widget.resize(30, 200)
		new_row=QHBoxLayout(new_row_widget)

		new_row.addWidget(QLabel(str(num)))  # 번호
		new_row.addWidget(QLabel(str(response_data.status_code)))  # 응답 코드
		new_row.addWidget(QLabel(str(len(response_data.content))))  # 응답 길이
		new_row.addWidget(QLabel(str(response_time)))  # 응답 소요 시간

		# 이벤트 연결
		ResponseController.rightClickListener(new_row_widget)

		return new_row_widget
	# 응답 테이블 비움
	def clearTable(project_name:str="", request_name:str=""):
		project_name=Global.cur_project_name
		request_name=Global.cur_request_name

		response_table=Global.res[project_name][request_name].response_table

		for i in range(1, response_table.count()):
			ResponseController.deleteRow(response_table.itemAt(1).widget())

		return


	### 이벤트
	## 우클릭
	# 우클릭 메뉴 표시
	def viewContextMenu(obj:QWidget, mouse_pos):
		menu=QMenu(obj, mouse_pos)
		index=int(obj.findChild(QHBoxLayout).itemAt(0).widget().text())  # 우클릭 한 오브젝트의 번호

		# 응답 팝업 열기 액션
		open_action=QAction("Open")
		open_action.triggered.connect(lambda : ResponseView(index=index))
		menu.addAction(open_action)
		# 응답 저장하기 액션
		save_action=QAction("Save")
		save_action.triggered.connect(lambda : ResponseController.saveResponse(index=index))
		menu.addAction(save_action)
		# 구분선
		menu.addAction("").setSeparator(True)
		# 비교자로 보내기 액션
		send_to_cmp_action=QAction("Send to Comparer")
		send_to_cmp_action.triggered.connect(lambda : ResponseController.sendComparer(index=index))
		menu.addAction(send_to_cmp_action)
		# 구분선
		menu.addAction("").setSeparator(True)
		# 삭제 액션
		delete_action=QAction("Delete")
		delete_action.triggered.connect(lambda : ResponseController.deleteResponse(index=index))
		menu.addAction(delete_action)

		menu.exec(mouse_pos)  # 표시

		return
	# 응답 저장하기
	def saveResponse(project_name:str="", request_name:str="", index:int=-1):
		project_name=Global.cur_project_name
		request_name=Global.cur_request_name
		saved_name, ok = QInputDialog.getText(Global.main, "", "Name:", Qt.WindowType.FramelessWindowHint)

		if ok:
			#todo# 이름 겹치는지 확인 후 알림
			file=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+saved_name+"rsv", 'a')
			file.write(Global.res[project_name][request_name].response_data[index-1][1].text)
			file.close()

		return
	# 비교자로 보내기
	def sendComparer(project_name:str="", request_name:str="", saved_name:str="",index:int=-1):
		if index!=-1:  # 응답 행(혹은 거기서 열린 팝업)에서 바로 보냄
			project_name=Global.cur_project_name
			request_name=Global.cur_request_name
		else:  # 저장 파일에서 보냄
			pass

		return
	# 삭제하기
	def deleteResponse(project_name:str="", request_name:str="", index:int=-1):
		project_name=Global.cur_project_name
		request_name=Global.cur_request_name

		ResponseController.deleteRow(Global.res[project_name][request_name].response_table.itemAt(index).widget())  # 행 삭제
		Global.res[project_name][request_name].response_data[index-1]=(-1, "deleted")  # 행 데이터 삭제

		return
	## 버튼
	# 필터 열기
	def openFilter(btn:QPushButton, filter_data:list):
		btn.clicked.connect(lambda: ResponseController.closeFilter(btn, Global.res[Global.cur_project_name][Global.cur_request_name].filter_data))
		Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.initUI(filter_data)
		Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.dialog.exec()

		return
	# 필터 닫기
	def closeFilter(btn:QPushButton, filter_data:list):
		filter_data=Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.getFilterData()
		ResponseController.applyFilter(filter_data)

		btn.clicked.connect(lambda: ResponseController.openFilter(btn, Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.filter_data))
		Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.dialog.close()

		return


	# 행 삭제
	def deleteRow(obj:QWidget):
		for i in range(obj.findChild(QHBoxLayout).count()):
			deleteObject(obj.findChild(QHBoxLayout).itemAt(0).widget())  # 번호, 응답 코드, 응답 길이, 응답 시간 라벨 삭제
			#deleteObject(response_table.itemAt(0).widget().findChild(QHBoxLayout))  # 행 레이아웃 삭제
		deleteObject(obj)  # 행 삭제

		return


	# 필터 적용
	def applyFilter(filter_data:list=[]):
		#todo#
		# True 걸린 필터 해석
		# 올라가있는 행 중 맞지 않는 행 제거
		# 새로 올라오는 행에도 필터 적용

		return


	def rightClickListener(widget) -> Signal:
		class Filter(QObject):
			clicked = Signal()

			def eventFilter(self, obj, event:QEvent):
				if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
					ResponseController.viewContextMenu(obj, event.globalPos())
					self.clicked.emit()

				return super().eventFilter(obj, event)

		click_filter = Filter(widget)
		widget.installEventFilter(click_filter)
		return click_filter.clicked



class ResponseFilter:
	def __init__(self, filter_data:list=[]):
		self.filter_data=filter_data

		self.last_right_clicked_obj:QWidget=None
		self.right_click_mouse_pos=None

		self.initUI()

		return


	## UI 구성
	# 기본 UI 구성
	def initUI(self, filter_data:list=[]):
		if len(filter_data)==0:
			## 오브젝트 선언
			self.dialog=QDialog()
			self.layout=QVBoxLayout()
			self.filter_list=QListWidget()
			self.add_filter_btn=QPushButton("+")

			## 오브젝트 구성
			self.dialog.setLayout(self.layout)
			# 리스트 라벨
			self.layout.addLayout(QHBoxLayout())
			self.layout.itemAt(0).addWidget(QLabel("Type"))
			self.layout.itemAt(0).addWidget(QLabel("Filter"))
			self.layout.addWidget(self.filter_list)
			self.layout.addWidget(self.add_filter_btn)

			## 이벤트 연결
			# + 버튼 클릭
			self.add_filter_btn.clicked.connect(self.addRow)
		else:
			for i in range(len(filter_data)):
				self.addRow(filter_data[i])  # 리스트에 행 삽입
					
			return
	# 행 추가
	def addRow(self, ischecked:bool=True, filter_type:str="", filter_text:str=""):
		row_item=QListWidgetItem()
		row_widget=self.Row(ischecked, filter_type, filter_text)  # 행 구성
		self.rightClickListener(row_widget).connect(self.viewContextMenu)  # 우클릭 이벤트 연결
		row_item.setSizeHint(row_widget.sizeHint())  # 크기 설정(필수)
		self.filter_list.insertItem(self.filter_list.count()-1, row_item)
		self.filter_list.setItemWidget(row_item, row_widget)

		return


	### 이벤트
	## 우클릭
	# 우클릭 메뉴 표시
	def viewContextMenu(self):
		menu=QMenu(self.last_right_clicked_obj, self.right_click_mouse_pos)
		
		# 행 삭제
		delete_filter_action=QAction("Delete")
		delete_filter_action.triggered.connect(self.deleteRow)
		menu.addAction(delete_filter_action)
		
		menu.exec(self.right_click_mouse_pos)  # 표시

		return
	# 행 삭제
	def deleteRow(self, event, index:int=-1):
		if index==-1:
			item_widget=self.last_right_clicked_obj
			row, index=self.getListItem(item_widget)
		else:
			item_widget=self.filter_list.itemWidget(self.filter_list.item(index))
			row=self.filter_list.item(index)

		
		# 오브젝트 삭제
		deleteObject(item_widget.findChild(QHBoxLayout).itemAt(0).widget())  # 체크박스
		deleteObject(item_widget.findChild(QHBoxLayout).itemAt(0).widget())  # 드롭다운
		deleteObject(item_widget.findChild(QHBoxLayout).itemAt(0).widget())  # 입력 칸
		#deleteObject(item_widget.findChild(QHBoxLayout))
		deleteObject(item_widget)
		self.filter_list.takeItem(index)  # 리스트에서 제거

		return


	# 리스트 위젯 기반 아이템과 인덱스 반환
	def getListItem(self, item_widget:QWidget) -> tuple:
		for i in range(self.filter_list.count()):
			item=self.filter_list.item(i)
			print(item, self.filter_list.itemWidget(item), item_widget)
			if self.filter_list.itemWidget(item)==item_widget:
				return item, i

		return
	# 필터 데이터 반환
	def getFilterData(self):
		return_data=[]

		for i in range(self.filter_list):
			row=self.filter_list.itemWidget(self.filter_list.item(i)).findChild(QHBoxLayout)
			return_data.append([row.itemAt(0).widget().isChecked(), row.itemAt(1).widget().currentText(), row.itemAt(2).widget().text()])

		return return_data


	def rightClickListener(self, widget) -> Signal:
		class Filter(QObject):
			clicked = Signal()

			def eventFilter(self, obj, event:QEvent):
				if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
					Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.right_click_mouse_pos=event.globalPos()
					Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.last_right_clicked_obj=obj
					self.clicked.emit()

				return super().eventFilter(obj, event)

		click_filter = Filter(widget)
		widget.installEventFilter(click_filter)
		return click_filter.clicked



	class Row(QWidget):
		def __init__(self, ischecked:bool, filter_type:str, filter_text:str):
			super().__init__()

			## 오브젝트 선언
			row=QHBoxLayout()
			type_dropdown=QComboBox()
			filter_if=QLineEdit(filter_text)

			## 오브젝트 구성
			row.addWidget(QCheckBox())
			row.addWidget(type_dropdown)
			row.addWidget(filter_if)

			## 기타 설정
			# 체크박스 체크 상태 설정
			row.itemAt(0).widget().setChecked(ischecked)
			# 드롭다운 텍스트 설정
			for crtype in CONST.RESPONSE_FILTER_TYPE:
				tmp=crtype.name.split('_')  # _ 제거
				for i in range(len(tmp)):
					tmp[i]=tmp[i].lower().capitalize()  # 앞글자 대문자로
				type_dropdown.addItem(' '.join(tmp))  # 공백 추가
			if filter_type=="":
				type_dropdown.setCurrentIndex(0)  # 첫 번쨰 요소로 설정
			else:
				type_dropdown.setCurrentIndex(type_dropdown.findText(filter_type))
	
			## 이벤트 연결
			type_dropdown.currentIndexChanged.connect(lambda: filter_if.setText(""))  # 타입 변경 시 조건 칸 비움

			self.setLayout(row)
	
			return





# 응답 내용 팝업
class ResponseView:
	def __init__(self, project_name:str="", request_name:str="", saved_name:str="", index:int=-1):
		self.project_name=project_name
		self.request_name=request_name
		self.saved_name=saved_name
		self.index=index

		self.initUI()  # UI 구성

		if index==-1:  # 저장된 파일 열기
			project_path=Global.projects_data[project_name]["last_path"]

			saved_data=open(project_path+'/'+project_name+'/saved/'+saved_name+".rsv")  # 파일 열기
			self.contents.setPlainText(saved_data.read())
			saved_data.close()  # 파일 닫기
		else:
			if project_name=="":
				self.contents.setPlainText(Global.res[Global.cur_project_name][Global.cur_request_name].response_data[index-1][1].text)
			else:
				self.contents.setPlainText(Global.res[project_name][request_name].response_data[index-1][1].text)
				# -> Response클래스->응답 데이터 리스트->응답 데이터

		return


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
		self.comparer_btn.clicked.connect(lambda : ResponseController.sendComparer(self.project_name, self.request_name, self.saved_name, self.index))
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



