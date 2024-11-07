#################### Imports ####################


import base64
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout

from System import CONST, deleteObject




##################### Main ######################



class Decoder:
	def __init__(self, parent):
		## 변수
		# 오브젝트
		self.decoder_tab_content=QVBoxLayout(parent)
		# 클래스 변수
		self.prevent_recursion=False  # inputChanged 함수 내의 decode 함수에서 발생하는 입력 칸 텍스트 변경에 의한 재귀 방지 변수
		self.enable_index=1  # 활성화 시작 인덱스(입력 구역 번호 라벨 기준)
		self.error_index=-1  # 오류 시작 인덱스(입력 구역 번호 라벨 기준)

		self.initUI()  # 기본 UI 구성

		return
		
	
	## 데이터 관리
	# 저장을 위한 탭 정보 불러오기
	def getTabInfo(self) -> dict:
		inputs=[]
		functions=[]

		for i in range(self.decoder_tab_content.count()):  # 시퀀스 데이터 저장
			div=self.decoder_tab_content.itemAt(i)  # QHBoxLayout

			if i%2==0:  # 입력 구역 데이터
				inputs.append(div.itemAt(1).widget().toPlainText())
			else:  # 기능 구역 데이터
				functions.append((div.itemAt(1).widget().currentText(), div.itemAt(3).widget().currentText()))  # 튜플로 저장

		decoder_data={}
		decoder_data["inputs"]=inputs
		decoder_data["functions"]=functions
		decoder_data["enable_index"]=self.enable_index
		decoder_data["error_index"]=self.error_index

		return decoder_data


	## 탭 구성
	# UI 구성
	def initUI(self, decoder_data:dict=None):
		if decoder_data==None:  # 기본 UI 구성
			self.initInput(1)  # 입력 구역 추가
			self.initFunction(2)  # 기능 구역 추가
			self.initInput(2)  # 입력 구역 추가
		else:  # 프로젝트 데이터 기반 UI 구성
			for i in range(self.decoder_tab_content.count()):  # 현재 시퀀스 전체 삭제
				div=self.decoder_tab_content.itemAt(0)  # QHBoxLayout

				if i%2==0:  # 입력 구역 데이터
					self.deleteInput(div)
				else:  # 기능 구역 데이터
					self.deleteFunction(div)

			## UI 재구성
			# 시퀀스 추가
			for i in range(len(decoder_data["functions"])):
				self.initInput(i+1, decoder_data["inputs"][i])
				self.initFunction(i+1, decoder_data["functions"][i])
			self.initInput(len(decoder_data["inputs"]), decoder_data["inputs"][-1])
			
			self.enable_index=decoder_data["enable_index"]  # 비활성화 설정
			self.error_index=decoder_data["error_index"]  # 오류 지점 설정
			self.setState()  # 상태 표시

		return
	# 입력 구역 추가
	def initInput(self, index:int, text:str=""):
		input_div=QHBoxLayout()
		btn_div=QVBoxLayout()
		delete_btn=QPushButton("X")  # x 버튼
		insert_btn=QPushButton("+")  # + 버튼

		## 입력 구역 조립
		input_div.addWidget(QLabel(str(index)))  # 번호 라벨 추가
		input_div.addWidget(QTextEdit(text))  # 입력 칸 추가
		input_div.addLayout(btn_div)
		btn_div.addWidget(delete_btn)  # x 버튼 추가  
		btn_div.addWidget(insert_btn)  # + 버튼 추가
			
		## 이벤트 연결
		input_div.itemAt(1).widget().textChanged.connect(lambda : self.onChangeInput(int(input_div.itemAt(0).widget().text())))  # 입력 내용 변경 시
		delete_btn.clicked.connect(lambda :self.onClickDelete(int(input_div.itemAt(0).widget().text())))  # x 버튼 클릭; 라벨의 번호 넘기기
		insert_btn.clicked.connect(lambda :self.onClickInsert(int(input_div.itemAt(0).widget().text())))  # + 버튼 클릭; 라벨의 번호 넘기기

		if index==1:
			deleteObject(delete_btn)

		self.decoder_tab_content.insertLayout((index-1)*2, input_div)  # 시퀀스에 삽입

		return
	# 기능 구역 추가
	def initFunction(self, index:int, data:tuple=CONST.DECODER_DEFAULT_FUNCTION):
		function_div=QHBoxLayout()

		# 모드 드롭다운 추가
		function_mode=QComboBox()
		for mode in CONST.DECODER_MODE:
			function_mode.addItem(mode.name)  # 추가
		# 방식 드롭다운 추가
		function_type=QComboBox()
		for crypt in CONST.DECODER_TYPE:
			function_type.addItem(crypt.name)  # 추가

		# 값 설정
		function_mode.setCurrentText(data[0])
		function_type.setCurrentText(data[1])

		# 이벤트 연결

		function_mode.currentTextChanged.connect(lambda : self.onChangeFunction(int(function_div.itemAt(0).widget().text())))  # 모드 드롭다운 변경 시; 번호 라벨 넘김
		function_type.currentTextChanged.connect(lambda : self.onChangeFunction(int(function_div.itemAt(0).widget().text())))  # 방식 드롭다운 변경 시; 번호 라벨 넘김

		# 기능 구역 구성
		function_div.addWidget(QLabel(str(index)))  # 상태 표시용 라벨  #todo#번호 숨기기
		function_div.addWidget(function_mode)
		function_div.addWidget(QLabel(" to "))
		function_div.addWidget(function_type)

		self.decoder_tab_content.insertLayout(index*2-3, function_div)

		return


	## UI 변환
	# 순서 리셋(생성, 삭제 시 라벨 번호 꼬이므로)
	def setIndexLabel(self):
		for i in range(self.decoder_tab_content.count()):
			self.decoder_tab_content.itemAt(i).itemAt(0).widget().setText(str((i+3)//2))  # 번호 라벨 재설정

		return
	# 상태 표시
	def setState(self):
		for i in range(self.decoder_tab_content.count()):
			if i<(self.enable_index-1)*2:  # 비활성화
				self.decoder_tab_content.itemAt(i).itemAt(0).widget().setStyleSheet("background-color:#ddd")
			elif self.error_index>0 and i>=(self.error_index-1)*2:  # 오류
				self.decoder_tab_content.itemAt(i).itemAt(0).widget().setStyleSheet("background-color:#fdd")
			else:
				self.decoder_tab_content.itemAt(i).itemAt(0).widget().setStyleSheet("")

		return
	

	### 이벤트
	## 버튼 클릭 이벤트
	# 과정 추가(+ 버튼)
	def onClickInsert(self, index:int):
		self.initFunction(index+1)  # 기능 구역 추가
		self.initInput(index+1)  # 입력 구역 추가

		self.setIndexLabel()  # 번호 라벨 재설정

		if index<self.enable_index:
			self.onChangeInput(index)
		else:
			self.onChangeInput(self.enable_index)
		
		return
	# 과정 삭제(x 버튼)
	def onClickDelete(self, index:int):
		## 오브젝트 삭제
		self.deleteInput(self.decoder_tab_content.itemAt((index-1)*2))  # 입력 구역 삭제
		self.deleteFunction(self.decoder_tab_content.itemAt(index*2-3))  # 기능 구역 삭제

		self.setIndexLabel()  # 번호 라벨 재설정

		if index<self.enable_index:
			self.onChangeInput(index)
		else:
			self.onChangeInput(self.enable_index)
		
		return
	## 시퀀스 변동이벤트
	# 기능 구역 변동 시
	def onChangeFunction(self, index:int):
		self.prevent_recursion=True  # decode함수에서 텍스트 변경 시 발생하는 inputChanged로의 재귀 방지

		self.decode(index)  # 변환
		self.enable_index=index-1  # 비활성화 지점 변경
		self.setState()  # 라벨 상태 변경

		self.prevent_recursion=False

		return
	# 입력 구역 변동 시
	def onChangeInput(self, index:int):
		if not self.prevent_recursion:
			self.prevent_recursion=True  # decode함수에서 텍스트 변경 시 발생하는 inputChanged로의 재귀 방지

			self.decode(index)  # 변환
			self.enable_index=index  # 비활성화 지점 변경
			self.setState()  # 라벨 상태 변경

		self.prevent_recursion=False

		return


	## 오브젝트 삭제
	# 입력 구역 삭제
	def deleteInput(self, obj):
		deleteObject(obj.itemAt(0).widget())  # 번호 라벨 삭제
		deleteObject(obj.itemAt(0).widget())  # 입력 칸 삭제
		deleteObject(obj.itemAt(0).itemAt(0).widget())  # x 버튼 삭제
		try:
			deleteObject(obj.itemAt(0).itemAt(0).widget())  # + 버튼 삭제
		except:  # 첫 번째 입력 구역일 때
			pass
		deleteObject(obj.itemAt(0))  # 버튼 구역 삭제
		deleteObject(obj)  # 입력 구역 삭제

		return
	# 기능 구역 삭제
	def deleteFunction(self, obj):
		deleteObject(obj.itemAt(0).widget())  # 상태 라벨 삭제
		deleteObject(obj.itemAt(0).widget())  # 모드 드롭다운 삭제
		deleteObject(obj.itemAt(0).widget())  # 라벨 삭제
		deleteObject(obj.itemAt(0).widget())  # 방식 드롭다운 삭제
		deleteObject(obj)  # 기능 구역 삭제

		return


	## 변환
	# 활성화된 시퀀스 변환 후 입력 칸 변경
	def decode(self, index):
		text=self.decoder_tab_content.itemAt((index-1)*2).itemAt(1).widget().toPlainText()

		for i in range(index*2, self.decoder_tab_content.count(), 2):  # 활성화 된 입력 구역에서 두 번째 입력 구역부터
			try:
				func_div=self.decoder_tab_content.itemAt(i-1)  # 기능 구역
				text=getattr(self.Transformer, func_div.itemAt(1).widget().currentText()+"To"+func_div.itemAt(3).widget().currentText())(text)  # 변환
				self.decoder_tab_content.itemAt(i).itemAt(1).widget().setPlainText(text)  # 변환된 텍스트 입력
			except:  # 변환이 불가능함
				self.error_index=i//2+1
				return

		self.error_index=-1

		return
	# 변환 함수 집합
	class Transformer:
		def ENCODEToBASE_64(strr:str):
			return base64.b64encode(strr.encode("UTF-8")).decode("UTF-8")
		def DECODEToBASE_64(strr:str):
			return base64.b64decode(strr.encode("UTF-8")+ b'=' * (-len(strr) % 4)).decode("UTF-8")