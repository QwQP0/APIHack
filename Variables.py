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

	
	## ������ ����
	# ������ ���� �� ���� �ҷ�����
	def getTabInfo(self) -> dict:
		variables_data={}
		
		for i in range(1, self.var_table.count()-1):
			row:QHBoxLayout=self.var_table.itemAt(i).widget().findChild(QHBoxLayout)
			variables_data[row.itemAt(2).widget().text()]=(row.itemAt(3).widget().currentText(), row.itemAt(4).widget().text())  # QLineEdit, QComboBox, QLabel

		return variables_data


	# UI ����
	def initUI(self, variables_data:list=None):
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
	def addRow(self, clicked:bool, var_name:str="", var_type:str="", var_range:str="", index:int=-1):
		if index==-1:
			index=self.var_table.count()-1

		# ������Ʈ ����
		new_row_widget=QWidget()
		new_row=QHBoxLayout(new_row_widget)  # ���̺� ��
		var_name_field=QLineEdit(var_name)
		type_dropdown=QComboBox()  # ���� Ÿ�� ��Ӵٿ�
		range_btn=QPushButton(var_range)  # ���� ���� ĭ

		# �� ����
		new_row.addWidget(QCheckBox())  # üũ�ڽ� �߰�
		new_row.addWidget(QLabel(str(self.var_table.count()-2+1)))  # �� ��ȣ �߰�, -2: ���̺� ��, + ��ư ����, +1: ��ȣ 1���� ����
		new_row.addWidget(var_name_field)  # ���� �̸� ĭ �߰�
		new_row.addWidget(type_dropdown)  # ���� Ÿ�� ĭ �߰�
		new_row.addWidget(range_btn)  # ���� ���� ĭ �߰�

		## ��Ÿ ����
		# �̸� ĭ
		if var_name_field.text()=="":
			var_name_field.setText(File.setNameAuto("", Global.cur_project_name, 'v'))
		# ��Ӵٿ�
		for cvtype in CONST.VARIABLES_TYPE:  # Ÿ�� ��Ӵٿ �׸� �߰�
			type_dropdown.addItem(cvtype.name.capitalize())  # �߰�
		if var_type!="":
			type_dropdown.setCurrentIndex(type_dropdown.findText(var_type))  # ��Ӵٿ �� ����
		else:
			type_dropdown.setCurrentIndex(type_dropdown.findText(CONST.VARIABLES_TYPE.CONST.name.lower().capitalize()))  # ��Ӵٿ �� ����

		## �̺�Ʈ ����
		# ���� �̸� ����
		var_name_field.textChanged.connect(lambda :self.onChangeVarName(var_name_field))
		# ��Ӵٿ� �̺�Ʈ
		type_dropdown.currentTextChanged.connect(lambda : range_btn.setText(""))  # ��Ӵٿ� ���� �� ���� ĭ ����
		# ���� ĭ Ŭ�� �� �̺�Ʈ
		range_btn.clicked.connect(lambda : self.SetVarRangeDialog(int(new_row.itemAt(1).widget().text())))
		# -> ���� ���� ���� ��ȭâ�� ���� �̸�, Ÿ��, ���� �ѱ�
		# ��Ŭ�� �̺�Ʈ
		self.rightClickListener(new_row_widget).connect(self.viewContextMenu)

		self.var_table.insertWidget(index, new_row_widget)  # �� ����

		return
	# ���� �̸� ���� ��
	def onChangeVarName(self, obj:QLineEdit):
		if obj.text()=="" or len(obj.text().split(' '))==0:  # �� ĭ�̰ų� ����
			obj.setStyleSheet("background-color:#fcc")
		else:
			obj.setStyleSheet()

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



	class SetVarRangeDialog():
		def __init__(self, index:int):
			self.var_table_row=Global.var.var_table.itemAt(index).widget().findChild(QHBoxLayout)
			self.var_name=self.var_table_row.itemAt(2).widget().text()
			self.var_type=CONST.VARIABLES_TYPE[self.var_table_row.itemAt(3).widget().currentText().upper()]
			self.var_range=self.var_table_row.itemAt(4).widget().text()

			self.initUI()

			return


		# UI ����
		def initUI(self):
			## ������Ʈ ����
			self.dialog=QDialog()
			self.dialog_contents=QVBoxLayout(self.dialog)
			btn_div=QHBoxLayout()
			cancel_btn=QPushButton("Cancel")
			ok_btn=QPushButton("OK")

			data=VarParser.rangeStrToData(self.var_range, self.var_type)  # ������ ��ȯ

			if self.var_type==CONST.VARIABLES_TYPE.CONST:  # ������
				## ������Ʈ ����
				range_field=QLineEdit(data[0])
				## ȭ�� ����
				self.dialog_contents.addWidget(QLabel("Set Value"))
				self.dialog_contents.addWidget(range_field)
			elif self.var_type==CONST.VARIABLES_TYPE.NUMBER:  # ����
				## ������Ʈ ����
				s_num_field=QLineEdit(str(data[0]))
				e_num_field=QLineEdit(str(data[1]))
				d_num_field=QLineEdit(str(data[2]))
				## ȭ�� ����
				self.dialog_contents.addWidget(QLabel("Start Number"))
				self.dialog_contents.addWidget(s_num_field)
				self.dialog_contents.addWidget(QLabel("End Number"))
				self.dialog_contents.addWidget(e_num_field)
				self.dialog_contents.addWidget(QLabel("Gap"))
				self.dialog_contents.addWidget(d_num_field)
			elif self.var_type==CONST.VARIABLES_TYPE.LIST:  # ����Ʈ
				## ������Ʈ ����
				s_index_field=QLineEdit(str(data[0]))
				e_index_field=QLineEdit(str(data[1]))
				list_div=QHBoxLayout()
				list_table=QTableWidget()
				list_btn_div=QVBoxLayout()
				upload_btn=QPushButton("^")
				insert_btn=QPushButton("+")
				delete_btn=QPushButton("-")
				delete_all_btn=QPushButton("X")
				## ȭ�� ����
				self.dialog_contents.addWidget(QLabel("Start Index"))
				self.dialog_contents.addWidget(s_index_field)
				self.dialog_contents.addWidget(QLabel("End Index"))
				self.dialog_contents.addWidget(e_index_field)
				list_div.addWidget(list_table)  # ���̺�
				list_btn_div.addWidget(upload_btn)
				list_btn_div.addWidget(insert_btn)
				list_btn_div.addWidget(delete_btn)
				list_btn_div.addWidget(delete_all_btn)
				list_div.addLayout(list_btn_div)  # ��ư ����
				self.dialog_contents.addLayout(list_div)
				## �̺�Ʈ ����
				upload_btn.clicked.connect(lambda: self.uploadList(list_table))
				insert_btn.clicked.connect(lambda: self.insertRowList(list_table))
				delete_btn.clicked.connect(lambda: self.deleteRowList(list_table))
				delete_all_btn.clicked.connect(lambda: self.deleteAllRowList(list_table))
				## ��Ÿ ����
				# ���̺� ����
				list_table.setColumnCount(1)
				list_table.setHorizontalHeaderLabels(["Value"])
				list_table.setRowCount(len(data[2]))
				# ���̺� �� ����
				for i in range(len(data[2])):
					list_table.setItem(i, 0, QTableWidgetItem(data[2][i]))
			elif self.var_type==CONST.VARIABLES_TYPE.STRING:
				pass

			## ȭ�� ����
			btn_div.addWidget(cancel_btn)
			btn_div.addWidget(ok_btn)
			self.dialog_contents.addLayout(btn_div)

			## �̺�Ʈ ����
			cancel_btn.clicked.connect(self.dialog.close)
			ok_btn.clicked.connect(self.onClickOK)

			## �˾� ���̱�
			self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
			self.dialog.resize(640, 360)
			self.dialog.exec()

			return
		# ��ȭâ���� ������ ������
		def getDialogContents(self) -> list:
			return_data=[]

			if self.var_type==CONST.VARIABLES_TYPE.CONST:
				return_data.append(self.dialog_contents.itemAt(1).widget().text())  # ������ : QLineEdit
			elif self.var_type==CONST.VARIABLES_TYPE.NUMBER:
				return_data.append(self.dialog_contents.itemAt(1).widget().text())  # ���� �� : QLineEdit
				return_data.append(self.dialog_contents.itemAt(3).widget().text())  # �� �� : QLineEdit
				return_data.append(self.dialog_contents.itemAt(5).widget().text())  # ���� �� : QLineEdit
			elif self.var_type==CONST.VARIABLES_TYPE.LIST:
				return_data.append(self.dialog_contents.itemAt(1).widget().text())  # ���� �ε��� : QLineEdit
				return_data.append(self.dialog_contents.itemAt(3).widget().text())  # �� �ε��� : QLineEdit
				return_data.append(self.getTableData(self.dialog_contents.itemAt(4).itemAt(0).widget()))
				# -> ���̺� : QTableWidget (dialog_contents->QHBoxLayout->QTableWidget)
			elif self.var_type==CONST.VARIABLES_TYPE.STRING:
				pass

			return return_data
		# ���̺��� ������ ������
		def getTableData(self, table:QTableWidget) -> list:
			return_data=[]

			for i in range(table.rowCount()):
				return_data.append(table.item(i, 0).text())

			return return_data


		### �̺�Ʈ
		## ��ư Ŭ�� �̺�Ʈ
		# ����Ʈ ���� ���ε� ��ư
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
					table.insertRow(pos+i)  # �� �߰�
					table.setItem(pos+i, 0, QTableWidgetItem())
					table.item(pos+i, 0).setText(lines[i][:len(lines[i])-1])  # �ؽ�Ʈ ����(�� ���� ����)

			return
		# ����Ʈ ���� �� �߰� ��ư
		def insertRowList(self, table:QTableWidget):
			if table.currentRow()==-1:
				table.insertRow(table.rowCount())
				table.setItem(table.rowCount()-1, 0, QTableWidgetItem())
			else:
				table.insertRow(table.currentRow())
				table.setItem(table.currentRow()-1, 0, QTableWidgetItem())
			table.selectRow(table.currentRow())

			return
		# ����Ʈ ���� �� ����
		def deleteRowList(self, table:QTableWidget):
			if table.currentRow()==-1:
				table.removeRow(table.rowCount())
			else:
				table.removeRow(table.currentRow())
			table.selectRow(table.currentRow())
			
			return
		# ����Ʈ ���� �� ��ü ����
		def deleteAllRowList(self, table:QTableWidget):
			table.setRowCount(0)

			return
		# Ȯ�� ��ư
		def onClickOK(self):
			var_range_data:list=self.getDialogContents()

			self.var_table_row.itemAt(4).widget().setText(VarParser.dataToRangeStr(var_range_data, self.var_type))  # ���� �ؽ�Ʈ ����

			self.dialog.close()  # ����

			return



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
		link_sep_data=self.separateVar(self.link)
		var_names.extend(link_sep_data[1])
		# ���
		header_sep_data=self.separateVar(self.header)  
		var_names.extend(header_sep_data[1])
		# ���̷ε�
		payload_sep_data=self.separateVar(self.payload)
		var_names.extend(payload_sep_data[1])

		var_names=list(set(var_names))  # �������� ��ȯ �� �ٽ� ����Ʈ�� ��ȯ(���Ǵ� �������� �ߺ��Ǵ� ���� �̸� ����)

		self.var_order=self.setVarOrder(var_names)  # ���� ��ȸ ���� ����

		iterator=self.stackVars()  # ��ȸ��
		for var_value in iterator:  # ��ȸ
			new_link=self.rebuildText(link_sep_data, var_value)
			new_header=self.rebuildText(header_sep_data, var_value)
			new_payload=self.rebuildText(payload_sep_data, var_value)
			yield new_link, new_header, new_payload
	# ���� ��ȸ ���� ����(link �� ����)
	def setVarOrder(self, var_names:list) -> list:
		var_names=deque(var_names)
		defined_var=set()
		var_order=[]

		while len(var_names):
			var_name=var_names.popleft()
			links=self.getLinks(var_name)  # ��ũ Ž��

			for i in range(len(links)):
				if not links[i] in defined_var:  # ��ũ�� ������ ���� �������� ����
					var_names.append(links[i])
					var_names.append(var_name)
					break
			else:
				var_order.append(var_name)  # ������ ����
				defined_var.add(var_name)

		return var_order
	## ���� ����
	# �ٸ� ������ ����Ǿ� �ִ��� �˻�
	def getLinks(self, var_name:str) -> list:
		var_values=self.var_data[var_name]  # ���� ���� �ҷ���/  �̸� : Ÿ��/��/������

		sep_data=self.separateVar(var_values[1])  # ���� ������ �ٸ� ������ ����Ǿ� �ִ��� �˻�

		return sep_data[1]
	## �ؽ�Ʈ ����
	# ����/�񺯼� �и�
	def separateVar(self, text:str) -> list:
		def addNormal(char:str=""):
			if len(return_data[2])==0 or return_data[0][-1]!=CONST.VARIABLES_SPLIT_TYPE.NORMAL:  # �Ϲ� ���� �Է����� �ƴ�
				return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.NORMAL)
				return_data[2].append("")  # �Ϲ� ���� �Է� ����
				return_data[4].append(len(func_stack))
			return_data[2][-1]+=char

		return_data=[[], [], [], [], []]  # ��Ȳ, ���� �̸�, �񺯼�, �Լ� �̸�, �Լ� ��ø ��
		func_stack=[]
		is_var=False
		is_func=False
		is_param=False

		## ��ũ
		i=0
		while i<len(text):
			if text[i]=='{':
				if i+3<len(text):
					if text[i:i+3]=="{{$":  # ���� �̸� ����
						i+=2
						return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.VAR)
						return_data[1].append("")  # ���� �Է� ��
						return_data[4].append(len(func_stack))
						is_var=True
					elif text[i:i+3]=="{{@":  # �Լ� �̸� ����
						i+=2
						return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.FUNC_OPEN)
						return_data[3].append("")  # �Լ� �Է� ��
						return_data[4].append(len(func_stack))
						is_func=True
					else:  # �Ϲ� ���� {
						addNormal("{")
				else:  # �Ϲ� ���� {
					addNormal("{")
			elif text[i]=='}':
				if i+1<len(text):
					if text[i+1]=='}':  # ����, �Լ� �̸� ��
						if is_var:  # ���� �Է� ��
							is_var=False

							i+=1
						elif is_func and is_param:  # �Լ� �Ķ���� �Է� ��
							is_func=False
							is_param=False
							return_data[0].append(CONST.VARIABLES_SPLIT_TYPE.FUNC_CLOSE)  # �Լ� ����
							func_stack.pop()
							return_data[4].append(len(func_stack))

							i+=1
						else:  # �Ϲ� ���� }}
							addNormal("}}")
					else:  # �Ϲ� ���� }
						addNormal("}")
				else:  # �Ϲ� ���� }
					addNormal("}")
			elif text[i]=='/':
				if is_var:
					return_data[1][-1]+="/"
				elif is_func:  # �Լ� �Է���
					if is_param:  # �Ķ���� �Է���(�Ϲ� ����)
						addNormal("/")
					else:
						# �Լ� �̸� �Է� ��
						func_stack.append(return_data[3][-1])  # ���ÿ� �߰�
						is_param=True
				else:
					addNormal("/")
			else:
				if is_var:
					return_data[1][-1]+=text[i]
				elif is_func:  # �Լ� �Է���
					if is_param:  # �Ķ���� �Է���(�Ϲ� ����)
						addNormal(text[i])
					else:
						return_data[3][-1]+=text[i]
				else:
					addNormal(text[i])

			i+=1

		if is_var or is_func:  # ����, �Լ� �Է��� ������ ����
			return "error"  #todo#

		#print("VarParser.separateVar : data -", return_data)  #log#
		return return_data
	# ������ �ؽ�Ʈ ������
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
				value=getattr(VarFunctions, func_stack.pop().upper())(param.pop())  # �Լ� ���

				if len(func_stack)!=0:  # �Ķ���� �Է� ��
					param[-1]+=value
				else:
					res+=value
			elif sep_data[0][i]==CONST.VARIABLES_SPLIT_TYPE.NORMAL:
				if len(func_stack)!=0:  # �Ķ���� �Է� ��
					param[-1]+=sep_data[2][pointer[1]]
					pointer[1]+=1
				else:
					res+=sep_data[2][pointer[1]]
					pointer[1]+=1
			elif sep_data[0][i]==CONST.VARIABLES_SPLIT_TYPE.VAR:
				if len(func_stack)!=0:  # �Ķ���� �Է� ��
					param[-1]+=str(var_value[sep_data[1][pointer[0]]])
					pointer[0]+=1
				else:
					res+=str(var_value[sep_data[1][pointer[0]]])
					pointer[0]+=1

		#print("VarParser.rebuildText : text -", res)  #log#
		return res
	## ��ȸ
	# ��ü ���� ��ȸ(��Ʈ��ŷ)
	def stackVars(self) -> dict:  # type: ignore
		var_value={}
		var_iterator_stack=[]

		while True:
			print(var_value, len(var_iterator_stack))

			if len(var_value)==len(self.var_order):  # ��Ʈ �ϼ�
				yield var_value

				try:
					var_value.pop(self.var_order[-1])
				except:
					return
			else:  # ��Ʈ �̿ϼ�
				if len(var_value)==len(var_iterator_stack):  # ���� ��ȸ�� ���� ����
					var_iterator_stack.append(self.traverseVar(self.var_order[len(var_iterator_stack)], var_value))
				else:  # ���� ���� ���� ����
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
	# ���� ���� ��ȸ
	def traverseVar(self, var_name:str, var_value:dict) -> str: # type: ignore
		# ������ �Լ��� ���Ե� ���� �����͸� ����� ��ȯ
		def fixVarValue(value:str):
			while True:
				sep_var=self.separateVar(value)

				if len(sep_var[1])==0 and len(sep_var[3])==0:  # ���� ����ְų� ����� ���� ��
					return value
				else:
					value=self.rebuildText(sep_var, var_value)

			return

		var_type, var_range=self.var_data[var_name]
		var_type=CONST.VARIABLES_TYPE[var_type.upper()]
		var_range=VarParser.rangeStrToData(var_range, var_type)

		if var_type==CONST.VARIABLES_TYPE.CONST:  # ������
			yield fixVarValue(var_range[0])
		elif var_type==CONST.VARIABLES_TYPE.NUMBER:  # �Ǽ�
			s=fixVarValue(var_range[0])
			e=fixVarValue(var_range[1])
			d=fixVarValue(var_range[2])

			if s=="" or e=="" or d=="":  # �� �Է�
				yield 0
			else:
				try:
					s=float(s)
					e=float(e)
					d=float(d)
					
					if d==0 and s!=e:  # �ݺ����� ������ ����
						raise ValueError()
					if (e-s)*d<0:  # �ݺ����� ������ ����
						raise ValueError()

					while (e-s)*d>=0:
						yield s
						s+=d
				except:
					return "error"  #todo#
		elif var_type==CONST.VARIABLES_TYPE.LIST:  # ����Ʈ
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
		elif var_type==CONST.VARIABLES_TYPE.STRING:  # ���ڿ�
			pass
	## ������
	# �ؽ�Ʈ���� �����ͷ�
	def rangeStrToData(var_range:str, data_type) -> list:
		# ���� ������ ����
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
			var_range=var_range[:len(var_range)-1]  # ���� ���ȣ ����

			if var_range[0]=='[':  # ���� ���� ����
				data=re.split(', ' , var_range[1:])  # ���� ���ȣ ���� �� ����Ʈȭ

				return_data=["", "", data]
			else:
				data=re.split(', ' , var_range)  # ����Ʈȭ
				s=data[0]
				e=data[1]

				data=data[2:]
				data[0]=data[0][1:]  # ���� ���ȣ ����

				return_data=[s, e, data]  # ["...", "...", [...]]
		elif data_type==CONST.VARIABLES_TYPE.STRING:
			pass

		return return_data
	# �����Ϳ��� �ؽ�Ʈ��
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
					return list_str  # ����, �� �������� ����Ʈ��
				else:
					return f"1, {data[1]}, {list_str}"  # ���� �⺻�� 1
			else:
				if data[1]=="":
					return f"{data[0]}, {str(len(data[2]))}, {list_str}"  # �� �⺻�� ����Ʈ ����
				else:
					return f"{data[0]}, {data[1]}, {list_str}"
		elif data_type==CONST.VARIABLES_TYPE.STRING:
			pass

		return



class VarFunctions:
	# ��Ģ ���� ���
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

		# ��ø�� +, - Ȯ��
		new_split=[]
		i=0
		while i<len(split):
			if split[i]=='+' or split[i]=='-':
				if i==len(split)-1:  # ���κп� +, - ����
					return str(0)  # ����#todo#
				else:
					if split[i]=='+':
						ispos=True
					else:
						ispos=False

					while True:
						i+=1

						if i==len(split):  # ��ħ
							return str(0)  # ����#todo#

						if split[i]=="+":
							pass
						elif split[i]=="-":
							ispos=not ispos
						elif split[i]=="*" or split[i]=="/":
							return str(0)  # ����#todo#
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

		# *, / ���
		new_split=[]
		i=0
		while i<len(split):
			if split[i]=='*' or split[i]=='/':
				if i!=0 or i!=len(split)-1:  # ���� �ִ°� �ƴ�
					if split[i-1]!='*' and split[i-1]!='/' and split[i-1]!='+' and split[i-1]!='-':  # �տ� ��ȣ ����
						if split[i+1]!='*' and split[i+1]!='/':  # �ڿ� *, / ����
							# ���
							if split[i+1]=='-':
								try:
									if split[i]=='*':
										if split[i-1]=="":  # �տ��� ����ؼ� �̹� �Ѿ
											new_split.append(str(float(new_split.pop())*float(split[i+2])*-1))
										else:
											new_split.append(str(float(split[i-1])*float(split[i+2])*-1))
									else:
										if split[i-1]=="":  # �տ��� ����ؼ� �̹� �Ѿ
											new_split.append(str(float(new_split.pop())/float(split[i+2])*-1))
										else:
											new_split.append(str(float(split[i-1])/float(split[i+2])*-1))
									split[i+2]=""  # ��ŷ(�̹� �����)
									i+=2
								except:  # ���ڷ� ��ȯ�� �� ����
									return str(0)  # ����#todo#
							elif split[i+1]=='+':
								try:
									if split[i]=='*':
										if split[i-1]=="":  # �տ��� ����ؼ� �̹� �Ѿ
											new_split.append(str(float(new_split.pop())*float(split[i+2])))
										else:
											new_split.append(str(float(split[i-1])*float(split[i+2])))
									else:
										if split[i-1]=="":  # �տ��� ����ؼ� �̹� �Ѿ
											new_split.append(str(float(new_split.pop())/float(split[i+2])))
										else:
											new_split.append(str(float(split[i-1])/float(split[i+2])))

									split[i+2]=""  # ��ŷ(�̹� �����)
									i+=2
								except:  # ���ڷ� ��ȯ�� �� ����
									return str(0)  # ����#todo#
							else:
								try:
									if split[i]=='*':
										if split[i-1]=="":  # �տ��� ����ؼ� �̹� �Ѿ
											new_split.append(str(float(new_split.pop())*float(split[i+1])))
										else:
											new_split.append(str(float(split[i-1])*float(split[i+1])))
									else:
										if split[i-1]=="":  # �տ��� ����ؼ� �̹� �Ѿ
											new_split.append(str(float(new_split.pop())/float(split[i+1])))
										else:
											new_split.append(str(float(split[i-1])/float(split[i+1])))

									split[i+1]=""  # ��ŷ(�̹� �����)
									i+=1
								except:  # ���ڷ� ��ȯ�� �� ����
									return str(0)  # ����#todo#
						else:
							return str(0)  # ����#todo#
					else:
						return str(0)  # ����#todo#
				else:
					return str(0)  # ����#todo#
			else:
				new_split.append(split[i])
				split[i]=""

			i+=1

		split=new_split[:]

		#print("VarFunctions.EXP : cal3 -", split)  #log#

		# +, - ���
		res=float(split[0])
		i=0

		for i in range(1, len(split), 2):
			try:
				if split[i]=='+':
					res+=float(split[i+1])
				else:  # -
					res-=float(split[i+1])
			except:
				return str(0)  # ����#todo#

		# ���� ��ȯ?
		if res==int(res):
			res=int(res)

		#print("VarFunctions.EXP : result -", res)  #log#

		return str(res)
	# 16���� ��ȯ
	def HEX(text:str) -> str:
		try:
			return str(hex(int(text)))
		except:
			return str(0)  # ����#todo#

		return