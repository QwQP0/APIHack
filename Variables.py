#################### Imports ####################



from collections import deque
from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton, QVBoxLayout, QWidget

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
			variables_data[row.itemAt(2).widget().text()]=(row.itemAt(3).widget().text(), row.itemAt(4).widget().text())

		return variables_data


	# UI 구성
	def initUI(self, variables_data:dict=None):
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
	def addRow(self, clicked:bool, var_name:str="", var_type:str=CONST.VARIABLES_TYPE.CONST.name, var_range:str="", index:int=-1):
		if index==-1:
			index=self.var_table.count()-1

		# 오브젝트 선언
		new_row_widget=QWidget()
		new_row=QHBoxLayout(new_row_widget)  # 테이블 행
		type_dropdown=QComboBox()  # 변수 타입 드롭다운
		range_field=QLabel(var_range)  # 변수 범위 칸

		# 행 구성
		new_row.addWidget(QCheckBox())  # 체크박스 추가
		new_row.addWidget(QLabel(str(self.var_table.count()-2+1)))  # 행 번호 추가, -2: 테이블 라벨, + 버튼 제외, +1: 번호 1부터 시작
		new_row.addWidget(QLineEdit(File.setNameAuto(var_name)))  # 변수 이름 칸 추가
		new_row.addWidget(type_dropdown)  # 변수 타입 칸 추가
		new_row.addWidget(range_field)  # 변수 범위 칸 추가

		# 드롭다운
		for type in CONST.VARIABLES_TYPE:  # 타입 드롭다운에 항목 추가
			type_dropdown.addItem(type.name.capitalize())  # 추가
		type_dropdown.setCurrentIndex(type_dropdown.findText(var_type))  # 드롭다운에 값 적용

		## 이벤트 연결
		# 드롭다운 이벤트
		#todo#
		# 범위 칸 클릭 시 이벤트
		self.rightClickListener(new_row_widget).connect(self.viewContextMenu)

		self.var_table.insertWidget(index, new_row_widget)  # 행 삽입

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
		link_vars, link_non_vars=self.separateVar(self.link)
		var_names.extend(link_vars)
		# 헤더
		header_vars, header_non_vars=self.separateVar(self.header)  
		var_names.extend(header_vars)
		# 페이로드
		payload_vars, payload_non_vars=self.separateVar(self.payload)
		var_names.extend(payload_vars)

		var_names=list(set(var_names))  # 집합으로 변환 후 다시 리스트로 변환(사용되는 변수에서 중복되는 변수 이름 제외)

		var_order=self.setVarOrder(var_names)  # 변수 순회 순서 결정

		iterator=self.stackVars(var_order)  # 순회자
		for var_value in iterator:  # 순회
			var_values={}

			for i in range(len(var_value)):
				var_values[var_order[i]]=var_value[i]

			new_link=self.rebuildText(link_vars, link_non_vars, var_values)
			new_header=self.rebuildText(header_vars, header_non_vars, var_values)
			new_payload=self.rebuildText(payload_vars, payload_non_vars, var_values)
			yield new_link, new_header, new_payload
	# 변수 순회 순서 결정(link 에 따라)
	def setVarOrder(self, var_names:list) -> list:
		var_names=deque(var_names)
		defined_var=set()
		var_order=[]

		while len(var_names):
			var_name=var_names.popleft()
			links=self.getLinks(var_name)  # 링크 탐색

			if len(links)==0:  # 링크 없음
				var_order.append(var_name)  # 순서에 삽입
				defined_var.add(var_name)
			else:
				isbreaked=False
				for i in range(len(links)):
					if not links[i] in defined_var:  # 링크된 변수가 아직 설정되지 않음
						isbreaked=True
						break

				if isbreaked:
					var_names.append(var_name)
				else:
					var_order.append(var_name)  # 순서에 삽입
					defined_var.add(var_name)

		return var_order
	# 다른 변수와 연계되어 있는지 검사
	def getLinks(self, var_name:str) -> list:
		var_values=self.var_data[var_name]  # 변수 정보 불러옴/  이름 : 타입/값/고정값

		links, tmp=self.separateVar(var_values[1])  # 변수 범위에 다른 변수가 연계되어 있는지 검사

		return links
	## 텍스트 관리
	# 변수/비변수 분리
	def separateVar(self, text:str) -> tuple:
		var_names=[]  # 변수
		var_name=""  # 변수 이름 저장용
		non_var=[]  # 비변수
		non_var_s=0  # 비변수 시작점(마지막으로 인식된 변수의 끝 점+1)

		## 링크
		i=0
		while i<len(text):
			if text[i]=='{':
				if i+3<len(text) and text[i:i+3]=="{{$":  # 변수 이름 시작
					i+=3
					var_name=text[i]
			elif text[i]=='}':
				if i+1<len(text) and text[i+1]=='}':  # 변수 이름 끝
					if var_name!="":
						non_var.append(text[non_var_s:(i+1)-5-len(var_name)+1])  # (변수 이름이 끝나는 인덱스)-(괄호, $ 제외)-(변수 이름 길이 제외)+(보정)
						# -> 비변수 저장
						var_names.append(var_name)  # 변수 이름 전달
						var_name=""  # 초기화
						non_var_s=(i+1)+1  # 변수 이름 } 끝부분 + 다음 인덱스
						# -> 다음 시작점 저장
			else:
				if var_name!="":  # 변수 이름 입력중
					var_name+=text[i]

			i+=1

		if non_var_s!=len(text):
			non_var.append(text[non_var_s:])

		return var_names, non_var
	# 변수와 텍스트 재조립
	def rebuildText(self, var_names:list, non_vars:list, var_value:dict) -> str:
		res=""

		for i in range(len(var_names)):
			res+=non_vars[i]
			res+=str(var_value[var_names[i]])

		if len(non_vars)>len(var_names):
			res+=non_vars[-1]

		return res
	## 순회
	# 전체 변수 순회(백트래킹)
	def stackVars(self, var_order:list) -> list: # type: ignore
		var_value_stack=[]
		var_iterator_stack=[]

		while True:
			print(var_order,var_value_stack, var_iterator_stack)

			if len(var_value_stack)!=len(var_iterator_stack):  # 순회자만 넣고 변수는 아직 안넣음
				try:
					var_value_stack.append(next(var_iterator_stack[-1]))  # 다음 변수 기입
				except:  # 다음 변수 없음! -> 변수 순회 종료
					try:
						var_value_stack.pop()  # 이 변수 스택을 통한 경로 없음
						var_iterator_stack.pop()  # 순회가 끝난 스택
					except:
						return
			else:  # 다음 순회자 넣을 차례
				if len(var_value_stack)!=len(var_order):  # 세트 미완성
					var_name=var_order[len(var_value_stack)]  # 현재 순회할 변수의 정보 불러옴
					var_iterator_stack.append(self.traverseVar(var_name))  # 변수 순회자 추가
				
					var_value_stack.append(next(var_iterator_stack[-1]))  # 첫 변수 등록
				else:  # 세트 완성
					yield var_value_stack  # 세트 반환

					try:
						var_value_stack.pop()  # 백트랙
					except:
						return
	# 단일 변수 순회
	def traverseVar(self, var_name:str) -> str: # type: ignore
		var_info=self.var_data[var_name]
		 
		#todo# 링크 시 가공하기
		if var_info[0]=="Const":  # 고정값
			yield var_info[1]
		if var_info[0]=="Number":  # 실수
			yield "error"
		elif var_info[0]=="List":  # 리스트
			for ret in var_info[1].split(','):    
				yield ret
		elif var_info[0]=="String":  # 문자열
			yield "error"