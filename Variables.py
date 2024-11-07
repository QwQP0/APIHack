#################### Imports ####################



from collections import deque
from math import e
import re
import time
from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListView, QMenu, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from System import CONST, File, Global, deleteObject



##################### Main ######################



class Variables:
	def __init__(self, parent):
		self.variables_tab_content=QVBoxLayout(parent)
		self.right_click_mouse_pos=None
		self.last_right_clicked_object:QHBoxLayout=None

		self.initUI()

		return

	
	## 데이터 관리
	# 저장을 위한 탭 정보 불러오기
	def getTabInfo(self) -> dict:
		variables_data={}
		
		for i in range(1, self.var_table.count()-1):
			row:QHBoxLayout=self.var_table.itemAt(i).widget().findChild(QHBoxLayout)
			variables_data[row.itemAt(2).widget().text()]=(row.itemAt(3).widget().currentText(), row.itemAt(4).widget().text())  # QLineEdit, QComboBox, QLabel

		return variables_data


	# UI 구성
	def initUI(self, variables_data:list=None):
		if variables_data==None:  # 기본 UI 구성
			## 오브젝트 선언
			# 테이블 라벨
			self.var_table=QVBoxLayout()
			table_labels=QHBoxLayout()
			# 행 추가 버튼
			addrow_btn=QPushButton("+")
		
			## 오브젝트 구성
			# 테이블 라벨 구성
			table_labels.addWidget(QLabel("*"))  # 체크박스
			table_labels.addWidget(QLabel("No."))  # 번호
			table_labels.addWidget(QLabel("Name"))  # 이름
			table_labels.addWidget(QLabel("Type"))  # 타입
			table_labels.addWidget(QLabel("Range"))  # 범위
			# 테이블 구성
			self.var_table.addLayout(table_labels)
			self.var_table.addWidget(addrow_btn)
			# 탭 구성
			self.variables_tab_content.addLayout(self.var_table)

			## 이벤트 연결
			addrow_btn.clicked.connect(self.addRow)
		else:  # 프로젝트 데이터 기반 UI 구성
			# 변수 테이블 행 전체 삭제
			for i in range(1, self.var_table.count()-1):  # 라벨, 버튼 제외
				for j in range(self.var_table.itemAt(1).widget().findChild(QHBoxLayout).count()):
					deleteObject(self.var_table.itemAt(1).widget().findChild(QHBoxLayout).itemAt(0).widget())  # 체크박스, 번호, 이름, 타입, 범위 오브젝트 삭제
				#deleteObject(self.var_table.itemAt(1).widget().findChild(QHBoxLayout))  # 행 레이아웃 삭제
				deleteObject(self.var_table.itemAt(1).widget())  # 행 위젯 삭제

			# 변수 정보 불러옴
			var_list=list(variables_data.keys())  # 변수 이름 불러옴
			
			for var_name in var_list:
				self.addRow(False, var_name, variables_data[var_name][0], variables_data[var_name][1])  # 행 추가

		return


	### 이벤트
	## 우클릭 이벤트
	# 우클릭 메뉴
	def viewContextMenu(self):
		menu=QMenu(self.last_right_clicked_object, self.right_click_mouse_pos)

		# 변수 복제
		duplicate_action=QAction("Duplicate")
		duplicate_action.triggered.connect(self.duplicate)
		menu.addAction(duplicate_action)
		# 변수 삭제
		delete_action=QAction("Delete")
		delete_action.triggered.connect(self.delete)
		menu.addAction(delete_action)

		menu.exec(self.right_click_mouse_pos)

		return
	# 행 복제
	def duplicate(self):
		var_index=int(self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(1).widget().text())
		var_name=self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(2).widget().text()
		new_var_name=File.setNameAuto(var_name, Global.cur_project_name, 'v')

		Global.projects_data[Global.cur_project_name]["variables"][new_var_name]=Global.projects_data[Global.cur_project_name]["variables"][var_name]
		# -> 변수 데이터 복제
		self.addRow(False, new_var_name, Global.projects_data[Global.cur_project_name]["variables"][new_var_name][0],\
		   Global.projects_data[Global.cur_project_name]["variables"][new_var_name][1], var_index+1)  # 선택한 행 아래에 행 추가

		self.setIndexLabel()  # 행 번호 재정비

		return
	# 행 삭제
	def delete(self):
		var_index=int(self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(1).widget().text())
		var_name=self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(2).widget().text()

		try:  # 변수 데이터가 있으면 변수 데이터 지움
			del Global.projects_data[Global.cur_project_name]["variables"][var_name]  # 변수 데이터 삭제
		except:
			pass

		# 행 삭제
		for j in range(self.var_table.itemAt(var_index).widget().findChild(QHBoxLayout).count()):
			deleteObject(self.var_table.itemAt(var_index).widget().findChild(QHBoxLayout).itemAt(0).widget())  # 체크박스, 번호, 이름, 타입, 범위 오브젝트 삭제
		#deleteObject(self.var_table.itemAt(var_index).widget().findChild(QHBoxLayout))  # 행 레이아웃 삭제
		deleteObject(self.var_table.itemAt(var_index).widget())  # 행 위젯 삭제

		self.setIndexLabel()  # 행 번호 재정비

		return
	## 버튼 클릭 이벤트
	# 새 행 추가
	def addRow(self, clicked:bool, var_name:str="", var_type:str="", var_range:str="", index:int=-1):
		if index==-1:
			index=self.var_table.count()-1

		# 오브젝트 선언
		new_row_widget=QWidget()
		new_row=QHBoxLayout(new_row_widget)  # 테이블 행
		var_name_field=QLineEdit(var_name)
		type_dropdown=QComboBox()  # 변수 타입 드롭다운
		range_btn=QPushButton(var_range)  # 변수 범위 칸

		# 행 구성
		new_row.addWidget(QCheckBox())  # 체크박스 추가
		new_row.addWidget(QLabel(str(self.var_table.count()-2+1)))  # 행 번호 추가, -2: 테이블 라벨, + 버튼 제외, +1: 번호 1부터 시작
		new_row.addWidget(var_name_field)  # 변수 이름 칸 추가
		new_row.addWidget(type_dropdown)  # 변수 타입 칸 추가
		new_row.addWidget(range_btn)  # 변수 범위 칸 추가

		## 기타 설정
		# 이름 칸
		if var_name_field.text()=="":
			var_name_field.setText(File.setNameAuto("", Global.cur_project_name, 'v'))
		# 드롭다운
		for cvtype in CONST.VARIABLES_TYPE:  # 타입 드롭다운에 항목 추가
			type_dropdown.addItem(cvtype.name.capitalize())  # 추가
		if var_type!="":
			type_dropdown.setCurrentIndex(type_dropdown.findText(var_type))  # 드롭다운에 값 적용
		else:
			type_dropdown.setCurrentIndex(type_dropdown.findText(CONST.VARIABLES_TYPE.CONST.name.lower().capitalize()))  # 드롭다운에 값 적용

		## 이벤트 연결
		# 변수 이름 변경
		var_name_field.textChanged.connect(lambda :self.onChangeVarName(var_name_field))
		# 드롭다운 이벤트
		type_dropdown.currentTextChanged.connect(lambda : range_btn.setText(""))  # 드롭다운 변경 시 범위 칸 제거
		# 범위 칸 클릭 시 이벤트
		range_btn.clicked.connect(lambda : self.SetVarRangeDialog(int(new_row.itemAt(1).widget().text())))
		# -> 변수 범위 설정 대화창에 변수 이름, 타입, 범위 넘김
		# 우클릭 이벤트
		self.rightClickListener(new_row_widget).connect(self.viewContextMenu)

		self.var_table.insertWidget(index, new_row_widget)  # 행 삽입

		return
	# 변수 이름 변경 시
	def onChangeVarName(self, obj:QLineEdit):
		if obj.text()=="" or len(obj.text().split(' '))==0:  # 빈 칸이거나 공백
			obj.setStyleSheet("background-color:#fcc")
		else:
			obj.setStyleSheet()

		return


	# 행 번호 재입력(행 삽입, 삭제 시)
	def setIndexLabel(self):
		for i in range(1, self.var_table.count()-1):
			self.var_table.itemAt(i).widget().findChild(QHBoxLayout).itemAt(1).widget().setText(str(i))  # 행 위젯->행 레이아웃->행 번호 라벨

		return


	# 우클릭 감지
	def rightClickListener(self, widget) -> Signal:
		class Filter(QObject):
			clicked = Signal()

			def eventFilter(self, obj, event:QEvent):
				if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
					Global.var.right_click_mouse_pos=event.globalPos()
					Global.var.last_right_clicked_object=obj
					self.clicked.emit()

				return super().eventFilter(obj, event)

		click_filter = Filter(widget)
		widget.installEventFilter(click_filter)
		return click_filter.clicked



	class SetVarRangeDialog():
		def __init__(self, index:int):
			self.var_table_row=Global.var.var_table.itemAt(index).widget().findChild(QHBoxLayout)
			self.var_name=self.var_table_row.itemAt(2).widget().text()
			self.var_type=CONST.VARIABLES_TYPE[self.var_table_row.itemAt(3).widget().currentText().upper()]
			self.var_range=self.var_table_row.itemAt(4).widget().text()

			self.initUI()

			return


		# UI 구성
		def initUI(self):
			## 오브젝트 선언
			self.dialog=QDialog()
			self.dialog_contents=QVBoxLayout(self.dialog)
			btn_div=QHBoxLayout()
			cancel_btn=QPushButton("Cancel")
			ok_btn=QPushButton("OK")

			data=VarParser.rangeStrToData(self.var_range, self.var_type)  # 데이터 변환

			if self.var_type==CONST.VARIABLES_TYPE.CONST:  # 고정값
				## 오브젝트 선언
				range_field=QLineEdit(data[0])
				## 화면 구성
				self.dialog_contents.addWidget(QLabel("Set Value"))
				self.dialog_contents.addWidget(range_field)
			elif self.var_type==CONST.VARIABLES_TYPE.NUMBER:  # 숫자
				## 오브젝트 선언
				s_num_field=QLineEdit(str(data[0]))
				e_num_field=QLineEdit(str(data[1]))
				d_num_field=QLineEdit(str(data[2]))
				## 화면 구성
				self.dialog_contents.addWidget(QLabel("Start Number"))
				self.dialog_contents.addWidget(s_num_field)
				self.dialog_contents.addWidget(QLabel("End Number"))
				self.dialog_contents.addWidget(e_num_field)
				self.dialog_contents.addWidget(QLabel("Gap"))
				self.dialog_contents.addWidget(d_num_field)
			elif self.var_type==CONST.VARIABLES_TYPE.LIST:  # 리스트
				## 오브젝트 선언
				s_index_field=QLineEdit(str(data[0]))
				e_index_field=QLineEdit(str(data[1]))
				list_div=QHBoxLayout()
				list_table=QTableWidget()
				list_btn_div=QVBoxLayout()
				upload_btn=QPushButton("^")
				insert_btn=QPushButton("+")
				delete_btn=QPushButton("-")
				delete_all_btn=QPushButton("X")
				## 화면 구성
				self.dialog_contents.addWidget(QLabel("Start Index"))
				self.dialog_contents.addWidget(s_index_field)
				self.dialog_contents.addWidget(QLabel("End Index"))
				self.dialog_contents.addWidget(e_index_field)
				list_div.addWidget(list_table)  # 테이블
				list_btn_div.addWidget(upload_btn)
				list_btn_div.addWidget(insert_btn)
				list_btn_div.addWidget(delete_btn)
				list_btn_div.addWidget(delete_all_btn)
				list_div.addLayout(list_btn_div)  # 버튼 집합
				self.dialog_contents.addLayout(list_div)
				## 이벤트 설정
				upload_btn.clicked.connect(lambda: self.uploadList(list_table))
				insert_btn.clicked.connect(lambda: self.insertRowList(list_table))
				delete_btn.clicked.connect(lambda: self.deleteRowList(list_table))
				delete_all_btn.clicked.connect(lambda: self.deleteAllRowList(list_table))
				## 기타 설정
				# 테이블 설정
				list_table.setColumnCount(1)
				list_table.setHorizontalHeaderLabels(["Value"])
				list_table.setRowCount(len(data[2]))
				# 테이블 값 설정
				for i in range(len(data[2])):
					list_table.setItem(i, 0, QTableWidgetItem(data[2][i]))
			elif self.var_type==CONST.VARIABLES_TYPE.STRING:
				pass

			## 화면 구성
			btn_div.addWidget(cancel_btn)
			btn_div.addWidget(ok_btn)
			self.dialog_contents.addLayout(btn_div)

			## 이벤트 연결
			cancel_btn.clicked.connect(self.dialog.close)
			ok_btn.clicked.connect(self.onClickOK)

			## 팝업 보이기
			self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
			self.dialog.resize(640, 360)
			self.dialog.exec()

			return
		# 대화창에서 데이터 가져옴
		def getDialogContents(self) -> list:
			return_data=[]

			if self.var_type==CONST.VARIABLES_TYPE.CONST:
				return_data.append(self.dialog_contents.itemAt(1).widget().text())  # 고정값 : QLineEdit
			elif self.var_type==CONST.VARIABLES_TYPE.NUMBER:
				return_data.append(self.dialog_contents.itemAt(1).widget().text())  # 시작 값 : QLineEdit
				return_data.append(self.dialog_contents.itemAt(3).widget().text())  # 끝 값 : QLineEdit
				return_data.append(self.dialog_contents.itemAt(5).widget().text())  # 간격 값 : QLineEdit
			elif self.var_type==CONST.VARIABLES_TYPE.LIST:
				return_data.append(self.dialog_contents.itemAt(1).widget().text())  # 시작 인덱스 : QLineEdit
				return_data.append(self.dialog_contents.itemAt(3).widget().text())  # 끝 인덱스 : QLineEdit
				return_data.append(self.getTableData(self.dialog_contents.itemAt(4).itemAt(0).widget()))
				# -> 테이블 : QTableWidget (dialog_contents->QHBoxLayout->QTableWidget)
			elif self.var_type==CONST.VARIABLES_TYPE.STRING:
				pass

			return return_data
		# 테이블에서 데이터 가져옴
		def getTableData(self, table:QTableWidget) -> list:
			return_data=[]

			for i in range(table.rowCount()):
				return_data.append(table.item(i, 0).text())

			return return_data


		### 이벤트
		## 버튼 클릭 이벤트
		# 리스트 변수 업로드 버튼
		def uploadList(self, table:QTableWidget):
			path=QFileDialog.getOpenFileName(self.dialog, 'Open file', './', 'text files (*.txt)')[0]

			if path:
				try:
					file=open(path, 'r', encoding='UTF-8')
					lines=file.readlines()
				except:
					file=open(path, 'r', encoding='CP949')
					lines=file.readlines()
				pos=table.rowCount()

				if table.currentRow()!=-1:
					pos=table.currentRow()+1

				for i in range(len(lines)):
					table.insertRow(pos+i)  # 행 추가
					table.setItem(pos+i, 0, QTableWidgetItem())
					table.item(pos+i, 0).setText(lines[i][:len(lines[i])-1])  # 텍스트 설정(끝 공백 제거)

			return
		# 리스트 변수 행 추가 버튼
		def insertRowList(self, table:QTableWidget):
			if table.currentRow()==-1:
				table.insertRow(table.rowCount())
				table.setItem(table.rowCount()-1, 0, QTableWidgetItem())
			else:
				table.insertRow(table.currentRow())
				table.setItem(table.currentRow()-1, 0, QTableWidgetItem())
			table.selectRow(table.currentRow())

			return
		# 리스트 변수 행 삭제
		def deleteRowList(self, table:QTableWidget):
			if table.currentRow()==-1:
				table.removeRow(table.rowCount())
			else:
				table.removeRow(table.currentRow())
			table.selectRow(table.currentRow())
			
			return
		# 리스트 변수 행 전체 삭제
		def deleteAllRowList(self, table:QTableWidget):
			table.setRowCount(0)

			return
		# 확인 버튼
		def onClickOK(self):
			var_range_data:list=self.getDialogContents()

			self.var_table_row.itemAt(4).widget().setText(VarParser.dataToRangeStr(var_range_data, self.var_type))  # 범위 텍스트 설정

			self.dialog.close()  # 종료

			return



class VarParser:
	def __init__(self, var_data:dict, link:str, header:str, payload:str):
		self.var_data=var_data
		self.link=link
		self.header=header
		self.payload=payload
		return


	### 변수 추출, 순회
	# 변수 순회자
	def varToText(self) -> tuple: # type: ignore
		var_names=[]
		
		## 변수/비변수 분리
		# 링크
		link_sep_data=self.separateVar(self.link)
		var_names.extend(link_sep_data[1])
		# 헤더
		header_sep_data=self.separateVar(self.header)  
		var_names.extend(header_sep_data[1])
		# 페이로드
		payload_sep_data=self.separateVar(self.payload)
		var_names.extend(payload_sep_data[1])

		var_names=list(set(var_names))  # 집합으로 변환 후 다시 리스트로 변환(사용되는 변수에서 중복되는 변수 이름 제외)

		self.var_order=self.setVarOrder(var_names)  # 변수 순회 순서 결정

		iterator=self.stackVars()  # 순회자
		for var_value in iterator:  # 순회
			new_link=self.rebuildText(link_sep_data, var_value)
			new_header=self.rebuildText(header_sep_data, var_value)
			new_payload=self.rebuildText(payload_sep_data, var_value)
			yield new_link, new_header, new_payload
	# 변수 순회 순서 결정(link 에 따라)
	def setVarOrder(self, var_names:list) -> list:
		var_names=deque(var_names)
		defined_var=set()
		var_order=[]

		while len(var_names):
			var_name=var_names.popleft()
			links=self.getLinks(var_name)  # 링크 탐색

			for i in range(len(links)):
				if not links[i] in defined_var:  # 링크된 변수가 아직 설정되지 않음
					var_names.append(links[i])
					var_names.append(var_name)
					break
			else:
				var_order.append(var_name)  # 순서에 삽입
				defined_var.add(var_name)

		return var_order
	## 변수 연계
	# 다른 변수와 연계되어 있는지 검사
	def getLinks(self, var_name:str) -> list:
		var_values=self.var_data[var_name]  # 변수 정보 불러옴/  이름 : 타입/값/고정값

		sep_data=self.separateVar(var_values[1])  # 변수 범위에 다른 변수가 연계되어 있는지 검사

		return sep_data[1]
	## 텍스트 관리
	# 변수/비변수 분리
	def separateVar(self, text:str) -> list:
		def addNormal(char:str=""):
			if len(return_data[2])==0 or return_data[0][-1]!=CONST.VARIABLES_SPLIT_TYPE.NORMAL:  # 일반 문자 입력중이 아님
				return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.NORMAL)
				return_data[2].append("")  # 일반 문자 입력 시작
				return_data[4].append(len(func_stack))
			return_data[2][-1]+=char

		return_data=[[], [], [], [], []]  # 현황, 변수 이름, 비변수, 함수 이름, 함수 중첩 수
		func_stack=[]
		is_var=False
		is_func=False
		is_param=False

		## 링크
		i=0
		while i<len(text):
			if text[i]=='{':
				if i+3<len(text):
					if text[i:i+3]=="{{$":  # 변수 이름 시작
						i+=2
						return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.VAR)
						return_data[1].append("")  # 변수 입력 중
						return_data[4].append(len(func_stack))
						is_var=True
					elif text[i:i+3]=="{{@":  # 함수 이름 시작
						i+=2
						return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.FUNC_OPEN)
						return_data[3].append("")  # 함수 입력 중
						return_data[4].append(len(func_stack))
						is_func=True
					else:  # 일반 문자 {
						addNormal("{")
				else:  # 일반 문자 {
					addNormal("{")
			elif text[i]=='}':
				if i+1<len(text):
					if text[i+1]=='}':  # 변수, 함수 이름 끝
						if is_var:  # 변수 입력 중
							is_var=False

							i+=1
						elif is_func and is_param:  # 함수 파라미터 입력 중
							is_func=False
							is_param=False
							return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.FUNC_CLOSE)  # 함수 닫음
							func_stack.pop()
							return_data[4].append(len(func_stack))

							i+=1
						else:  # 일반 문자 }}
							addNormal("}}")
					else:  # 일반 문자 }
						addNormal("}")
				else:  # 일반 문자 }
					addNormal("}")
			elif text[i]=='/':
				if is_var:
					return_data[1][-1]+="/"
				elif is_func:  # 함수 입력중
					if is_param:  # 파라미터 입력중(일반 문자)
						addNormal("/")
					else:
						# 함수 이름 입력 끝
						func_stack.append(return_data[3][-1])  # 스택에 추가
						is_param=True
				else:
					addNormal("/")
			else:
				if is_var:
					return_data[1][-1]+=text[i]
				elif is_func:  # 함수 입력중
					if is_param:  # 파라미터 입력중(일반 문자)
						addNormal(text[i])
					else:
						return_data[3][-1]+=text[i]
				else:
					addNormal(text[i])

			i+=1

		if is_var or is_func:  # 변수, 함수 입력이 끝나지 않음
			return "error"  #todo#

		#print("VarParser.separateVar : data -", return_data)  #log#
		return return_data
	# 변수와 텍스트 재조립
	def rebuildText(self, sep_data:list, var_value:dict) -> str:
		res=""
		pointer=[0, 0, 0]
		func_stack=[]
		param=[]

		for i in range(len(sep_data[0])):
			if sep_data[0][i]==CONST.VARIABLES_SPLIT_TYPE.FUNC_OPEN:
				func_stack.append(sep_data[3][pointer[2]])
				pointer[2]+=1
				param.append("")
			elif sep_data[0][i]==CONST.VARIABLES_SPLIT_TYPE.FUNC_CLOSE:
				value=getattr(VarFunctions, func_stack.pop().upper())(param.pop())  # 함수 계산

				if len(func_stack)!=0:  # 파라미터 입력 중
					param[-1]+=value
				else:
					res+=value
			elif sep_data[0][i]==CONST.VARIABLES_SPLIT_TYPE.NORMAL:
				if len(func_stack)!=0:  # 파라미터 입력 중
					param[-1]+=sep_data[2][pointer[1]]
					pointer[1]+=1
				else:
					res+=sep_data[2][pointer[1]]
					pointer[1]+=1
			elif sep_data[0][i]==CONST.VARIABLES_SPLIT_TYPE.VAR:
				if len(func_stack)!=0:  # 파라미터 입력 중
					param[-1]+=str(var_value[sep_data[1][pointer[0]]])
					pointer[0]+=1
				else:
					res+=str(var_value[sep_data[1][pointer[0]]])
					pointer[0]+=1

		#print("VarParser.rebuildText : text -", res)  #log#
		return res
	## 순회
	# 전체 변수 순회(백트래킹)
	def stackVars(self) -> dict:  # type: ignore
		var_value={}
		var_iterator_stack=[]

		while True:
			print(var_value, len(var_iterator_stack))

			if len(var_value)==len(self.var_order):  # 세트 완성
				yield var_value

				try:
					var_value.pop(self.var_order[-1])
				except:
					return
			else:  # 세트 미완성
				if len(var_value)==len(var_iterator_stack):  # 다음 순회자 넣을 차례
					var_iterator_stack.append(self.traverseVar(self.var_order[len(var_iterator_stack)], var_value))
				else:  # 다음 변수 넣을 차례
					try:
						nxt=next(var_iterator_stack[-1])
						var_value[self.var_order[len(var_iterator_stack)-1]]=nxt
					except:
						try:
							var_iterator_stack.pop()
							var_value.pop(self.var_order[len(var_iterator_stack)-1])
						except:
							return
						
		return
	# 단일 변수 순회
	def traverseVar(self, var_name:str, var_value:dict) -> str: # type: ignore
		# 변수나 함수가 포함된 변수 데이터를 상수로 변환
		def fixVarValue(value:str):
			while True:
				sep_var=self.separateVar(value)

				if len(sep_var[1])==0 and len(sep_var[3])==0:  # 값이 비어있거나 상수만 있을 때
					return value
				else:
					value=self.rebuildText(sep_var, var_value)

			return

		var_type, var_range=self.var_data[var_name]
		var_type=CONST.VARIABLES_TYPE[var_type.upper()]
		var_range=VarParser.rangeStrToData(var_range, var_type)

		if var_type==CONST.VARIABLES_TYPE.CONST:  # 고정값
			yield fixVarValue(var_range[0])
		elif var_type==CONST.VARIABLES_TYPE.NUMBER:  # 실수
			s=fixVarValue(var_range[0])
			e=fixVarValue(var_range[1])
			d=fixVarValue(var_range[2])

			if s=="" or e=="" or d=="":  # 빈 입력
				yield 0
			else:
				try:
					s=float(s)
					e=float(e)
					d=float(d)
					
					if d==0 and s!=e:  # 반복문이 끝나지 않음
						raise ValueError()
					if (e-s)*d<0:  # 반복문이 끝나지 않음
						raise ValueError()

					while (e-s)*d>=0:
						yield s
						s+=d
				except:
					return "error"  #todo#
		elif var_type==CONST.VARIABLES_TYPE.LIST:  # 리스트
			s=fixVarValue(var_range[0])
			e=fixVarValue(var_range[1])

			if s=="" and e=="":
				s=1
				e=len(var_range[2])
			else:
				try:
					s=int(float(s))
					e=int(float(e))
				except:
					return "error"  #todo#
			for i in range(s-1, e):
				yield fixVarValue(var_range[2][i])
		elif var_type==CONST.VARIABLES_TYPE.STRING:  # 문자열
			pass
	## 데이터
	# 텍스트에서 데이터로
	def rangeStrToData(var_range:str, data_type) -> list:
		# 기존 데이터 없음
		if var_range=="":
			if data_type==CONST.VARIABLES_TYPE.CONST:
				return [""]
			if data_type==CONST.VARIABLES_TYPE.NUMBER:
				return ["", "", ""]
			if data_type==CONST.VARIABLES_TYPE.LIST:
				return ["", "", []]
			if data_type==CONST.VARIABLES_TYPE.STRING:
				return

		return_data=[]

		if data_type==CONST.VARIABLES_TYPE.CONST:
			return_data.append(var_range)
		elif data_type==CONST.VARIABLES_TYPE.NUMBER:
			return_data.extend(re.split(', ' , var_range))  # s, e, d
		elif data_type==CONST.VARIABLES_TYPE.LIST:
			var_range=var_range[:len(var_range)-1]  # 뒤쪽 대괄호 제거

			if var_range[0]=='[':  # 범위 지정 없음
				data=re.split(', ' , var_range[1:])  # 앞쪽 대괄호 제거 후 리스트화

				return_data=["", "", data]
			else:
				data=re.split(', ' , var_range)  # 리스트화
				s=data[0]
				e=data[1]

				data=data[2:]
				data[0]=data[0][1:]  # 앞쪽 대괄호 제거

				return_data=[s, e, data]  # ["...", "...", [...]]
		elif data_type==CONST.VARIABLES_TYPE.STRING:
			pass

		return return_data
	# 데이터에서 텍스트로
	def dataToRangeStr(data:list, data_type:CONST.VARIABLES_TYPE) -> str:
		if data_type==CONST.VARIABLES_TYPE.CONST:  # [str]
			return data[0]
		elif data_type==CONST.VARIABLES_TYPE.NUMBER:  # [str, str, str]
			return f"{data[0]}, {data[1]}, {data[2]}"
		elif data_type==CONST.VARIABLES_TYPE.LIST:  # [str, str, list]
			list_str="["
			for i in range(len(data[2])-1):
				list_str+=data[2][i]
				list_str+=", "
			list_str+=data[2][-1]
			list_str+=']'

			if data[0]=="":
				if data[1]=="":
					return list_str  # 시작, 끝 미지정시 리스트만
				else:
					return f"1, {data[1]}, {list_str}"  # 시작 기본값 1
			else:
				if data[1]=="":
					return f"{data[0]}, {str(len(data[2]))}, {list_str}"  # 끝 기본값 리스트 길이
				else:
					return f"{data[0]}, {data[1]}, {list_str}"
		elif data_type==CONST.VARIABLES_TYPE.STRING:
			pass

		return



class VarFunctions:
	# 사칙 연산 계산
	def EXP(text:str) -> str:
		num=""
		split=[]

		for i in range(len(text)):
			if text[i]=='/' or text[i]=='*' or text[i]=='+' or text[i]=='-':
				if num!="":
					split.append(num)
					num=""
				split.append(text[i])
			else:
				num+=text[i]
		if num!="":
			split.append(num)
			num=""

		#print("VarFunctions.EXP : cal1 -", split)  #log#

		# 중첩된 +, - 확인
		new_split=[]
		i=0
		while i<len(split):
			if split[i]=='+' or split[i]=='-':
				if i==len(split)-1:  # 끝부분에 +, - 있음
					return str(0)  # 오류#todo#
				else:
					if split[i]=='+':
						ispos=True
					else:
						ispos=False

					while True:
						i+=1

						if i==len(split):  # 넘침
							return str(0)  # 오류#todo#

						if split[i]=="+":
							pass
						elif split[i]=="-":
							ispos=not ispos
						elif split[i]=="*" or split[i]=="/":
							return str(0)  # 오류#todo#
						else:
							if ispos:
								new_split.append('+')
							else:
								new_split.append('-')
							new_split.append(split[i])

							break
			else:
				new_split.append(split[i])

			i+=1

		split=new_split[:]

		#print("VarFunctions.EXP : cal2 -", split)  #log#

		# *, / 계산
		new_split=[]
		i=0
		while i<len(split):
			if split[i]=='*' or split[i]=='/':
				if i!=0 or i!=len(split)-1:  # 끝에 있는거 아님
					if split[i-1]!='*' and split[i-1]!='/' and split[i-1]!='+' and split[i-1]!='-':  # 앞에 기호 없음
						if split[i+1]!='*' and split[i+1]!='/':  # 뒤에 *, / 없음
							# 계산
							if split[i+1]=='-':
								try:
									if split[i]=='*':
										if split[i-1]=="":  # 앞에서 계산해서 이미 넘어감
											new_split.append(str(float(new_split.pop())*float(split[i+2])*-1))
										else:
											new_split.append(str(float(split[i-1])*float(split[i+2])*-1))
									else:
										if split[i-1]=="":  # 앞에서 계산해서 이미 넘어감
											new_split.append(str(float(new_split.pop())/float(split[i+2])*-1))
										else:
											new_split.append(str(float(split[i-1])/float(split[i+2])*-1))
									split[i+2]=""  # 마킹(이미 계산함)
									i+=2
								except:  # 숫자로 변환할 수 없음
									return str(0)  # 오류#todo#
							elif split[i+1]=='+':
								try:
									if split[i]=='*':
										if split[i-1]=="":  # 앞에서 계산해서 이미 넘어감
											new_split.append(str(float(new_split.pop())*float(split[i+2])))
										else:
											new_split.append(str(float(split[i-1])*float(split[i+2])))
									else:
										if split[i-1]=="":  # 앞에서 계산해서 이미 넘어감
											new_split.append(str(float(new_split.pop())/float(split[i+2])))
										else:
											new_split.append(str(float(split[i-1])/float(split[i+2])))

									split[i+2]=""  # 마킹(이미 계산함)
									i+=2
								except:  # 숫자로 변환할 수 없음
									return str(0)  # 오류#todo#
							else:
								try:
									if split[i]=='*':
										if split[i-1]=="":  # 앞에서 계산해서 이미 넘어감
											new_split.append(str(float(new_split.pop())*float(split[i+1])))
										else:
											new_split.append(str(float(split[i-1])*float(split[i+1])))
									else:
										if split[i-1]=="":  # 앞에서 계산해서 이미 넘어감
											new_split.append(str(float(new_split.pop())/float(split[i+1])))
										else:
											new_split.append(str(float(split[i-1])/float(split[i+1])))

									split[i+1]=""  # 마킹(이미 계산함)
									i+=1
								except:  # 숫자로 변환할 수 없음
									return str(0)  # 오류#todo#
						else:
							return str(0)  # 오류#todo#
					else:
						return str(0)  # 오류#todo#
				else:
					return str(0)  # 오류#todo#
			else:
				new_split.append(split[i])
				split[i]=""

			i+=1

		split=new_split[:]

		#print("VarFunctions.EXP : cal3 -", split)  #log#

		# +, - 계산
		res=float(split[0])
		i=0

		for i in range(1, len(split), 2):
			try:
				if split[i]=='+':
					res+=float(split[i+1])
				else:  # -
					res-=float(split[i+1])
			except:
				return str(0)  # 오류#todo#

		# 정수 변환?
		if res==int(res):
			res=int(res)

		#print("VarFunctions.EXP : result -", res)  #log#

		return str(res)
	# 16진수 변환
	def HEX(text:str) -> str:
		try:
			return str(hex(int(text)))
		except:
			return str(0)  # 오류#todo#

		return