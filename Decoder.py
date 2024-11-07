#################### Imports ####################


import base64
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout

from System import CONST, deleteObject




##################### Main ######################



class Decoder:
	def __init__(self, parent):
		## ����
		# ������Ʈ
		self.decoder_tab_content=QVBoxLayout(parent)
		# Ŭ���� ����
		self.prevent_recursion=False  # inputChanged �Լ� ���� decode �Լ����� �߻��ϴ� �Է� ĭ �ؽ�Ʈ ���濡 ���� ��� ���� ����
		self.enable_index=1  # Ȱ��ȭ ���� �ε���(�Է� ���� ��ȣ �� ����)
		self.error_index=-1  # ���� ���� �ε���(�Է� ���� ��ȣ �� ����)

		self.initUI()  # �⺻ UI ����

		return
		
	
	## ������ ����
	# ������ ���� �� ���� �ҷ�����
	def getTabInfo(self) -> dict:
		inputs=[]
		functions=[]

		for i in range(self.decoder_tab_content.count()):  # ������ ������ ����
			div=self.decoder_tab_content.itemAt(i)  # QHBoxLayout

			if i%2==0:  # �Է� ���� ������
				inputs.append(div.itemAt(1).widget().toPlainText())
			else:  # ��� ���� ������
				functions.append((div.itemAt(1).widget().currentText(), div.itemAt(3).widget().currentText()))  # Ʃ�÷� ����

		decoder_data={}
		decoder_data["inputs"]=inputs
		decoder_data["functions"]=functions
		decoder_data["enable_index"]=self.enable_index
		decoder_data["error_index"]=self.error_index

		return decoder_data


	## �� ����
	# UI ����
	def initUI(self, decoder_data:dict=None):
		if decoder_data==None:  # �⺻ UI ����
			self.initInput(1)  # �Է� ���� �߰�
			self.initFunction(2)  # ��� ���� �߰�
			self.initInput(2)  # �Է� ���� �߰�
		else:  # ������Ʈ ������ ��� UI ����
			for i in range(self.decoder_tab_content.count()):  # ���� ������ ��ü ����
				div=self.decoder_tab_content.itemAt(0)  # QHBoxLayout

				if i%2==0:  # �Է� ���� ������
					self.deleteInput(div)
				else:  # ��� ���� ������
					self.deleteFunction(div)

			## UI �籸��
			# ������ �߰�
			for i in range(len(decoder_data["functions"])):
				self.initInput(i+1, decoder_data["inputs"][i])
				self.initFunction(i+1, decoder_data["functions"][i])
			self.initInput(len(decoder_data["inputs"]), decoder_data["inputs"][-1])
			
			self.enable_index=decoder_data["enable_index"]  # ��Ȱ��ȭ ����
			self.error_index=decoder_data["error_index"]  # ���� ���� ����
			self.setState()  # ���� ǥ��

		return
	# �Է� ���� �߰�
	def initInput(self, index:int, text:str=""):
		input_div=QHBoxLayout()
		btn_div=QVBoxLayout()
		delete_btn=QPushButton("X")  # x ��ư
		insert_btn=QPushButton("+")  # + ��ư

		## �Է� ���� ����
		input_div.addWidget(QLabel(str(index)))  # ��ȣ �� �߰�
		input_div.addWidget(QTextEdit(text))  # �Է� ĭ �߰�
		input_div.addLayout(btn_div)
		btn_div.addWidget(delete_btn)  # x ��ư �߰�  
		btn_div.addWidget(insert_btn)  # + ��ư �߰�
			
		## �̺�Ʈ ����
		input_div.itemAt(1).widget().textChanged.connect(lambda : self.onChangeInput(int(input_div.itemAt(0).widget().text())))  # �Է� ���� ���� ��
		delete_btn.clicked.connect(lambda :self.onClickDelete(int(input_div.itemAt(0).widget().text())))  # x ��ư Ŭ��; ���� ��ȣ �ѱ��
		insert_btn.clicked.connect(lambda :self.onClickInsert(int(input_div.itemAt(0).widget().text())))  # + ��ư Ŭ��; ���� ��ȣ �ѱ��

		if index==1:
			deleteObject(delete_btn)

		self.decoder_tab_content.insertLayout((index-1)*2, input_div)  # �������� ����

		return
	# ��� ���� �߰�
	def initFunction(self, index:int, data:tuple=CONST.DECODER_DEFAULT_FUNCTION):
		function_div=QHBoxLayout()

		# ��� ��Ӵٿ� �߰�
		function_mode=QComboBox()
		for mode in CONST.DECODER_MODE:
			function_mode.addItem(mode.name)  # �߰�
		# ��� ��Ӵٿ� �߰�
		function_type=QComboBox()
		for crypt in CONST.DECODER_TYPE:
			function_type.addItem(crypt.name)  # �߰�

		# �� ����
		function_mode.setCurrentText(data[0])
		function_type.setCurrentText(data[1])

		# �̺�Ʈ ����

		function_mode.currentTextChanged.connect(lambda : self.onChangeFunction(int(function_div.itemAt(0).widget().text())))  # ��� ��Ӵٿ� ���� ��; ��ȣ �� �ѱ�
		function_type.currentTextChanged.connect(lambda : self.onChangeFunction(int(function_div.itemAt(0).widget().text())))  # ��� ��Ӵٿ� ���� ��; ��ȣ �� �ѱ�

		# ��� ���� ����
		function_div.addWidget(QLabel(str(index)))  # ���� ǥ�ÿ� ��  #todo#��ȣ �����
		function_div.addWidget(function_mode)
		function_div.addWidget(QLabel(" to "))
		function_div.addWidget(function_type)

		self.decoder_tab_content.insertLayout(index*2-3, function_div)

		return


	## UI ��ȯ
	# ���� ����(����, ���� �� �� ��ȣ ���̹Ƿ�)
	def setIndexLabel(self):
		for i in range(self.decoder_tab_content.count()):
			self.decoder_tab_content.itemAt(i).itemAt(0).widget().setText(str((i+3)//2))  # ��ȣ �� �缳��

		return
	# ���� ǥ��
	def setState(self):
		for i in range(self.decoder_tab_content.count()):
			if i<(self.enable_index-1)*2:  # ��Ȱ��ȭ
				self.decoder_tab_content.itemAt(i).itemAt(0).widget().setStyleSheet("background-color:#ddd")
			elif self.error_index>0 and i>=(self.error_index-1)*2:  # ����
				self.decoder_tab_content.itemAt(i).itemAt(0).widget().setStyleSheet("background-color:#fdd")
			else:
				self.decoder_tab_content.itemAt(i).itemAt(0).widget().setStyleSheet("")

		return
	

	### �̺�Ʈ
	## ��ư Ŭ�� �̺�Ʈ
	# ���� �߰�(+ ��ư)
	def onClickInsert(self, index:int):
		self.initFunction(index+1)  # ��� ���� �߰�
		self.initInput(index+1)  # �Է� ���� �߰�

		self.setIndexLabel()  # ��ȣ �� �缳��

		if index<self.enable_index:
			self.onChangeInput(index)
		else:
			self.onChangeInput(self.enable_index)
		
		return
	# ���� ����(x ��ư)
	def onClickDelete(self, index:int):
		## ������Ʈ ����
		self.deleteInput(self.decoder_tab_content.itemAt((index-1)*2))  # �Է� ���� ����
		self.deleteFunction(self.decoder_tab_content.itemAt(index*2-3))  # ��� ���� ����

		self.setIndexLabel()  # ��ȣ �� �缳��

		if index<self.enable_index:
			self.onChangeInput(index)
		else:
			self.onChangeInput(self.enable_index)
		
		return
	## ������ �����̺�Ʈ
	# ��� ���� ���� ��
	def onChangeFunction(self, index:int):
		self.prevent_recursion=True  # decode�Լ����� �ؽ�Ʈ ���� �� �߻��ϴ� inputChanged���� ��� ����

		self.decode(index)  # ��ȯ
		self.enable_index=index-1  # ��Ȱ��ȭ ���� ����
		self.setState()  # �� ���� ����

		self.prevent_recursion=False

		return
	# �Է� ���� ���� ��
	def onChangeInput(self, index:int):
		if not self.prevent_recursion:
			self.prevent_recursion=True  # decode�Լ����� �ؽ�Ʈ ���� �� �߻��ϴ� inputChanged���� ��� ����

			self.decode(index)  # ��ȯ
			self.enable_index=index  # ��Ȱ��ȭ ���� ����
			self.setState()  # �� ���� ����

		self.prevent_recursion=False

		return


	## ������Ʈ ����
	# �Է� ���� ����
	def deleteInput(self, obj):
		deleteObject(obj.itemAt(0).widget())  # ��ȣ �� ����
		deleteObject(obj.itemAt(0).widget())  # �Է� ĭ ����
		deleteObject(obj.itemAt(0).itemAt(0).widget())  # x ��ư ����
		try:
			deleteObject(obj.itemAt(0).itemAt(0).widget())  # + ��ư ����
		except:  # ù ��° �Է� ������ ��
			pass
		deleteObject(obj.itemAt(0))  # ��ư ���� ����
		deleteObject(obj)  # �Է� ���� ����

		return
	# ��� ���� ����
	def deleteFunction(self, obj):
		deleteObject(obj.itemAt(0).widget())  # ���� �� ����
		deleteObject(obj.itemAt(0).widget())  # ��� ��Ӵٿ� ����
		deleteObject(obj.itemAt(0).widget())  # �� ����
		deleteObject(obj.itemAt(0).widget())  # ��� ��Ӵٿ� ����
		deleteObject(obj)  # ��� ���� ����

		return


	## ��ȯ
	# Ȱ��ȭ�� ������ ��ȯ �� �Է� ĭ ����
	def decode(self, index):
		text=self.decoder_tab_content.itemAt((index-1)*2).itemAt(1).widget().toPlainText()

		for i in range(index*2, self.decoder_tab_content.count(), 2):  # Ȱ��ȭ �� �Է� �������� �� ��° �Է� ��������
			try:
				func_div=self.decoder_tab_content.itemAt(i-1)  # ��� ����
				text=getattr(self.Transformer, func_div.itemAt(1).widget().currentText()+"To"+func_div.itemAt(3).widget().currentText())(text)  # ��ȯ
				self.decoder_tab_content.itemAt(i).itemAt(1).widget().setPlainText(text)  # ��ȯ�� �ؽ�Ʈ �Է�
			except:  # ��ȯ�� �Ұ�����
				self.error_index=i//2+1
				return

		self.error_index=-1

		return
	# ��ȯ �Լ� ����
	class Transformer:
		def ENCODEToBASE_64(strr:str):
			return base64.b64encode(strr.encode("UTF-8")).decode("UTF-8")
		def DECODEToBASE_64(strr:str):
			return base64.b64decode(strr.encode("UTF-8")+ b'=' * (-len(strr) % 4)).decode("UTF-8")