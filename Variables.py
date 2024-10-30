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

	
	## ������ ����
	# ������ ���� �� ���� �ҷ�����
	def getTabInfo(self) -> dict:
		variables_data={}
		
		for i in range(1, self.var_table.count()-1):
			row:QHBoxLayout=self.var_table.itemAt(i).widget().findChild(QHBoxLayout)
			variables_data[row.itemAt(2).widget().text()]=(row.itemAt(3).widget().text(), row.itemAt(4).widget().text())

		return variables_data


	# UI ����
	def initUI(self, variables_data:dict=None):
		if variables_data==None:  # �⺻ UI ����
			## ������Ʈ ����
			# ���̺� ��
			self.var_table=QVBoxLayout()
			table_labels=QHBoxLayout()
			# �� �߰� ��ư
			addrow_btn=QPushButton("+")
		
			## ������Ʈ ����
			# ���̺� �� ����
			table_labels.addWidget(QLabel("*"))  # üũ�ڽ�
			table_labels.addWidget(QLabel("No."))  # ��ȣ
			table_labels.addWidget(QLabel("Name"))  # �̸�
			table_labels.addWidget(QLabel("Type"))  # Ÿ��
			table_labels.addWidget(QLabel("Range"))  # ����
			# ���̺� ����
			self.var_table.addLayout(table_labels)
			self.var_table.addWidget(addrow_btn)
			# �� ����
			self.variables_tab_content.addLayout(self.var_table)

			## �̺�Ʈ ����
			addrow_btn.clicked.connect(self.addRow)
		else:  # ������Ʈ ������ ��� UI ����
			# ���� ���̺� �� ��ü ����
			for i in range(1, self.var_table.count()-1):  # ��, ��ư ����
				for j in range(self.var_table.itemAt(1).widget().findChild(QHBoxLayout).count()):
					deleteObject(self.var_table.itemAt(1).widget().findChild(QHBoxLayout).itemAt(0).widget())  # üũ�ڽ�, ��ȣ, �̸�, Ÿ��, ���� ������Ʈ ����
				#deleteObject(self.var_table.itemAt(1).widget().findChild(QHBoxLayout))  # �� ���̾ƿ� ����
				deleteObject(self.var_table.itemAt(1).widget())  # �� ���� ����

			# ���� ���� �ҷ���
			var_list=list(variables_data.keys())  # ���� �̸� �ҷ���
			
			for var_name in var_list:
				self.addRow(False, var_name, variables_data[var_name][0], variables_data[var_name][1])  # �� �߰�

		return


	### �̺�Ʈ
	## ��Ŭ�� �̺�Ʈ
	# ��Ŭ�� �޴�
	def viewContextMenu(self):
		menu=QMenu(self.last_right_clicked_object, self.right_click_mouse_pos)

		# ���� ����
		duplicate_action=QAction("Duplicate")
		duplicate_action.triggered.connect(self.duplicate)
		menu.addAction(duplicate_action)
		# ���� ����
		delete_action=QAction("Delete")
		delete_action.triggered.connect(self.delete)
		menu.addAction(delete_action)

		menu.exec(self.right_click_mouse_pos)

		return
	# �� ����
	def duplicate(self):
		var_index=int(self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(1).widget().text())
		var_name=self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(2).widget().text()
		new_var_name=File.setNameAuto(var_name, Global.cur_project_name, 'v')

		Global.projects_data[Global.cur_project_name]["variables"][new_var_name]=Global.projects_data[Global.cur_project_name]["variables"][var_name]
		# -> ���� ������ ����
		self.addRow(False, new_var_name, Global.projects_data[Global.cur_project_name]["variables"][new_var_name][0],\
		   Global.projects_data[Global.cur_project_name]["variables"][new_var_name][1], var_index+1)  # ������ �� �Ʒ��� �� �߰�

		self.setIndexLabel()  # �� ��ȣ ������

		return
	# �� ����
	def delete(self):
		var_index=int(self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(1).widget().text())
		var_name=self.last_right_clicked_object.findChild(QHBoxLayout).itemAt(2).widget().text()

		try:  # ���� �����Ͱ� ������ ���� ������ ����
			del Global.projects_data[Global.cur_project_name]["variables"][var_name]  # ���� ������ ����
		except:
			pass

		# �� ����
		for j in range(self.var_table.itemAt(var_index).widget().findChild(QHBoxLayout).count()):
			deleteObject(self.var_table.itemAt(var_index).widget().findChild(QHBoxLayout).itemAt(0).widget())  # üũ�ڽ�, ��ȣ, �̸�, Ÿ��, ���� ������Ʈ ����
		#deleteObject(self.var_table.itemAt(var_index).widget().findChild(QHBoxLayout))  # �� ���̾ƿ� ����
		deleteObject(self.var_table.itemAt(var_index).widget())  # �� ���� ����

		self.setIndexLabel()  # �� ��ȣ ������

		return
	## ��ư Ŭ�� �̺�Ʈ
	# �� �� �߰�
	def addRow(self, clicked:bool, var_name:str="", var_type:str=CONST.VARIABLES_TYPE.CONST.name, var_range:str="", index:int=-1):
		if index==-1:
			index=self.var_table.count()-1

		# ������Ʈ ����
		new_row_widget=QWidget()
		new_row=QHBoxLayout(new_row_widget)  # ���̺� ��
		type_dropdown=QComboBox()  # ���� Ÿ�� ��Ӵٿ�
		range_field=QLabel(var_range)  # ���� ���� ĭ

		# �� ����
		new_row.addWidget(QCheckBox())  # üũ�ڽ� �߰�
		new_row.addWidget(QLabel(str(self.var_table.count()-2+1)))  # �� ��ȣ �߰�, -2: ���̺� ��, + ��ư ����, +1: ��ȣ 1���� ����
		new_row.addWidget(QLineEdit(File.setNameAuto(var_name)))  # ���� �̸� ĭ �߰�
		new_row.addWidget(type_dropdown)  # ���� Ÿ�� ĭ �߰�
		new_row.addWidget(range_field)  # ���� ���� ĭ �߰�

		# ��Ӵٿ�
		for type in CONST.VARIABLES_TYPE:  # Ÿ�� ��Ӵٿ �׸� �߰�
			type_dropdown.addItem(type.name.capitalize())  # �߰�
		type_dropdown.setCurrentIndex(type_dropdown.findText(var_type))  # ��Ӵٿ �� ����

		## �̺�Ʈ ����
		# ��Ӵٿ� �̺�Ʈ
		#todo#
		# ���� ĭ Ŭ�� �� �̺�Ʈ
		self.rightClickListener(new_row_widget).connect(self.viewContextMenu)

		self.var_table.insertWidget(index, new_row_widget)  # �� ����

		return


	# �� ��ȣ ���Է�(�� ����, ���� ��)
	def setIndexLabel(self):
		for i in range(1, self.var_table.count()-1):
			self.var_table.itemAt(i).widget().findChild(QHBoxLayout).itemAt(1).widget().setText(str(i))  # �� ����->�� ���̾ƿ�->�� ��ȣ ��

		return


	# ��Ŭ�� ����
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


	### ���� ����, ��ȸ
	# ���� ��ȸ��
	def varToText(self) -> tuple: # type: ignore
		var_names=[]
		
		## ����/�񺯼� �и�
		# ��ũ
		link_vars, link_non_vars=self.separateVar(self.link)
		var_names.extend(link_vars)
		# ���
		header_vars, header_non_vars=self.separateVar(self.header)  
		var_names.extend(header_vars)
		# ���̷ε�
		payload_vars, payload_non_vars=self.separateVar(self.payload)
		var_names.extend(payload_vars)

		var_names=list(set(var_names))  # �������� ��ȯ �� �ٽ� ����Ʈ�� ��ȯ(���Ǵ� �������� �ߺ��Ǵ� ���� �̸� ����)

		var_order=self.setVarOrder(var_names)  # ���� ��ȸ ���� ����

		iterator=self.stackVars(var_order)  # ��ȸ��
		for var_value in iterator:  # ��ȸ
			var_values={}

			for i in range(len(var_value)):
				var_values[var_order[i]]=var_value[i]

			new_link=self.rebuildText(link_vars, link_non_vars, var_values)
			new_header=self.rebuildText(header_vars, header_non_vars, var_values)
			new_payload=self.rebuildText(payload_vars, payload_non_vars, var_values)
			yield new_link, new_header, new_payload
	# ���� ��ȸ ���� ����(link �� ����)
	def setVarOrder(self, var_names:list) -> list:
		var_names=deque(var_names)
		defined_var=set()
		var_order=[]

		while len(var_names):
			var_name=var_names.popleft()
			links=self.getLinks(var_name)  # ��ũ Ž��

			if len(links)==0:  # ��ũ ����
				var_order.append(var_name)  # ������ ����
				defined_var.add(var_name)
			else:
				isbreaked=False
				for i in range(len(links)):
					if not links[i] in defined_var:  # ��ũ�� ������ ���� �������� ����
						isbreaked=True
						break

				if isbreaked:
					var_names.append(var_name)
				else:
					var_order.append(var_name)  # ������ ����
					defined_var.add(var_name)

		return var_order
	# �ٸ� ������ ����Ǿ� �ִ��� �˻�
	def getLinks(self, var_name:str) -> list:
		var_values=self.var_data[var_name]  # ���� ���� �ҷ���/  �̸� : Ÿ��/��/������

		links, tmp=self.separateVar(var_values[1])  # ���� ������ �ٸ� ������ ����Ǿ� �ִ��� �˻�

		return links
	## �ؽ�Ʈ ����
	# ����/�񺯼� �и�
	def separateVar(self, text:str) -> tuple:
		var_names=[]  # ����
		var_name=""  # ���� �̸� �����
		non_var=[]  # �񺯼�
		non_var_s=0  # �񺯼� ������(���������� �νĵ� ������ �� ��+1)

		## ��ũ
		i=0
		while i<len(text):
			if text[i]=='{':
				if i+3<len(text) and text[i:i+3]=="{{$":  # ���� �̸� ����
					i+=3
					var_name=text[i]
			elif text[i]=='}':
				if i+1<len(text) and text[i+1]=='}':  # ���� �̸� ��
					if var_name!="":
						non_var.append(text[non_var_s:(i+1)-5-len(var_name)+1])  # (���� �̸��� ������ �ε���)-(��ȣ, $ ����)-(���� �̸� ���� ����)+(����)
						# -> �񺯼� ����
						var_names.append(var_name)  # ���� �̸� ����
						var_name=""  # �ʱ�ȭ
						non_var_s=(i+1)+1  # ���� �̸� } ���κ� + ���� �ε���
						# -> ���� ������ ����
			else:
				if var_name!="":  # ���� �̸� �Է���
					var_name+=text[i]

			i+=1

		if non_var_s!=len(text):
			non_var.append(text[non_var_s:])

		return var_names, non_var
	# ������ �ؽ�Ʈ ������
	def rebuildText(self, var_names:list, non_vars:list, var_value:dict) -> str:
		res=""

		for i in range(len(var_names)):
			res+=non_vars[i]
			res+=str(var_value[var_names[i]])

		if len(non_vars)>len(var_names):
			res+=non_vars[-1]

		return res
	## ��ȸ
	# ��ü ���� ��ȸ(��Ʈ��ŷ)
	def stackVars(self, var_order:list) -> list: # type: ignore
		var_value_stack=[]
		var_iterator_stack=[]

		while True:
			print(var_order,var_value_stack, var_iterator_stack)

			if len(var_value_stack)!=len(var_iterator_stack):  # ��ȸ�ڸ� �ְ� ������ ���� �ȳ���
				try:
					var_value_stack.append(next(var_iterator_stack[-1]))  # ���� ���� ����
				except:  # ���� ���� ����! -> ���� ��ȸ ����
					try:
						var_value_stack.pop()  # �� ���� ������ ���� ��� ����
						var_iterator_stack.pop()  # ��ȸ�� ���� ����
					except:
						return
			else:  # ���� ��ȸ�� ���� ����
				if len(var_value_stack)!=len(var_order):  # ��Ʈ �̿ϼ�
					var_name=var_order[len(var_value_stack)]  # ���� ��ȸ�� ������ ���� �ҷ���
					var_iterator_stack.append(self.traverseVar(var_name))  # ���� ��ȸ�� �߰�
				
					var_value_stack.append(next(var_iterator_stack[-1]))  # ù ���� ���
				else:  # ��Ʈ �ϼ�
					yield var_value_stack  # ��Ʈ ��ȯ

					try:
						var_value_stack.pop()  # ��Ʈ��
					except:
						return
	# ���� ���� ��ȸ
	def traverseVar(self, var_name:str) -> str: # type: ignore
		var_info=self.var_data[var_name]
		 
		#todo# ��ũ �� �����ϱ�
		if var_info[0]=="Const":  # ������
			yield var_info[1]
		if var_info[0]=="Number":  # �Ǽ�
			yield "error"
		elif var_info[0]=="List":  # ����Ʈ
			for ret in var_info[1].split(','):    
				yield ret
		elif var_info[0]=="String":  # ���ڿ�
			yield "error"