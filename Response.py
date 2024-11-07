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


	# ���� ������ ����
	def clearData(self):
		self.response_data=[]
		ResponseController.clearTable()

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(str(0)+" responses")  # ���� �� ǥ�� �� ����

		return


	# �� �߰�
	def addRow(self, response_time:float, response_data:requests.Response):
		self.response_data.append((response_time, response_data))  # ������ �߰�
		self.response_table.insertWidget(1, ResponseController.initRow(len(self.response_data), response_time, response_data))  # ���̺� �ֻ��(�� �ٷ� �Ʒ�)�� ����

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(str(len(self.response_data))+" responses")  # ���� �� ǥ�� �� ����

		return



class ResponseController:
	## �� ����
	# UI ����
	def initUI(parent:QBoxLayout) -> QVBoxLayout:
		### ������Ʈ ����
		## ���
		top_div=QHBoxLayout()
		filter_btn=QPushButton("#")  # ���� ��ư
		## ���̺� ����
		response_table=QVBoxLayout()
		# ���̺� ��
		table_labels=QHBoxLayout()

		### UI ����
		## ��� ����
		top_div.addWidget(QLabel("0"+" responses"))  # ���� �� ǥ�� ��
		top_div.addWidget(filter_btn)
		## ���̺� �� ����
		table_labels.addWidget(QLabel("No."))  # ��ȣ
		table_labels.addWidget(QLabel("Response Code"))  # ���� �ڵ�
		table_labels.addWidget(QLabel("Length"))  # ���� ����
		table_labels.addWidget(QLabel("Response Time"))  # ���� �ҿ� �ð�
		## �� ����
		response_table.addLayout(table_labels)  # ���̺� �� ����
		parent.addLayout(top_div)
		parent.addLayout(response_table)

		### �̺�Ʈ ����
		## ��ư �̺�Ʈ
		# ���� ��ư Ŭ�� ��
		filter_btn.clicked.connect(lambda: ResponseController.openFilter(filter_btn, Global.res[Global.cur_project_name][Global.cur_request_name].filter_data))

		return response_table
	# ���� ���̺� �� ����
	def initRow(num:int, response_time:float, response_data:requests.Response) -> QWidget:
		new_row_widget=QWidget()
		new_row_widget.resize(30, 200)
		new_row=QHBoxLayout(new_row_widget)

		new_row.addWidget(QLabel(str(num)))  # ��ȣ
		new_row.addWidget(QLabel(str(response_data.status_code)))  # ���� �ڵ�
		new_row.addWidget(QLabel(str(len(response_data.content))))  # ���� ����
		new_row.addWidget(QLabel(str(response_time)))  # ���� �ҿ� �ð�

		# �̺�Ʈ ����
		ResponseController.rightClickListener(new_row_widget)

		return new_row_widget
	# ���� ���̺� ���
	def clearTable(project_name:str="", request_name:str=""):
		project_name=Global.cur_project_name
		request_name=Global.cur_request_name

		response_table=Global.res[project_name][request_name].response_table

		for i in range(1, response_table.count()):
			ResponseController.deleteRow(response_table.itemAt(1).widget())

		return


	### �̺�Ʈ
	## ��Ŭ��
	# ��Ŭ�� �޴� ǥ��
	def viewContextMenu(obj:QWidget, mouse_pos):
		menu=QMenu(obj, mouse_pos)
		index=int(obj.findChild(QHBoxLayout).itemAt(0).widget().text())  # ��Ŭ�� �� ������Ʈ�� ��ȣ

		# ���� �˾� ���� �׼�
		open_action=QAction("Open")
		open_action.triggered.connect(lambda : ResponseView(index=index))
		menu.addAction(open_action)
		# ���� �����ϱ� �׼�
		save_action=QAction("Save")
		save_action.triggered.connect(lambda : ResponseController.saveResponse(index=index))
		menu.addAction(save_action)
		# ���м�
		menu.addAction("").setSeparator(True)
		# ���ڷ� ������ �׼�
		send_to_cmp_action=QAction("Send to Comparer")
		send_to_cmp_action.triggered.connect(lambda : ResponseController.sendComparer(index=index))
		menu.addAction(send_to_cmp_action)
		# ���м�
		menu.addAction("").setSeparator(True)
		# ���� �׼�
		delete_action=QAction("Delete")
		delete_action.triggered.connect(lambda : ResponseController.deleteResponse(index=index))
		menu.addAction(delete_action)

		menu.exec(mouse_pos)  # ǥ��

		return
	# ���� �����ϱ�
	def saveResponse(project_name:str="", request_name:str="", index:int=-1):
		project_name=Global.cur_project_name
		request_name=Global.cur_request_name
		saved_name, ok = QInputDialog.getText(Global.main, "", "Name:", Qt.WindowType.FramelessWindowHint)

		if ok:
			#todo# �̸� ��ġ���� Ȯ�� �� �˸�
			file=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+saved_name+"rsv", 'a')
			file.write(Global.res[project_name][request_name].response_data[index-1][1].text)
			file.close()

		return
	# ���ڷ� ������
	def sendComparer(project_name:str="", request_name:str="", saved_name:str="",index:int=-1):
		if index!=-1:  # ���� ��(Ȥ�� �ű⼭ ���� �˾�)���� �ٷ� ����
			project_name=Global.cur_project_name
			request_name=Global.cur_request_name
		else:  # ���� ���Ͽ��� ����
			pass

		return
	# �����ϱ�
	def deleteResponse(project_name:str="", request_name:str="", index:int=-1):
		project_name=Global.cur_project_name
		request_name=Global.cur_request_name

		ResponseController.deleteRow(Global.res[project_name][request_name].response_table.itemAt(index).widget())  # �� ����
		Global.res[project_name][request_name].response_data[index-1]=(-1, "deleted")  # �� ������ ����

		return
	## ��ư
	# ���� ����
	def openFilter(btn:QPushButton, filter_data:list):
		btn.clicked.connect(lambda: ResponseController.closeFilter(btn, Global.res[Global.cur_project_name][Global.cur_request_name].filter_data))
		Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.initUI(filter_data)
		Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.dialog.exec()

		return
	# ���� �ݱ�
	def closeFilter(btn:QPushButton, filter_data:list):
		filter_data=Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.getFilterData()
		ResponseController.applyFilter(filter_data)

		btn.clicked.connect(lambda: ResponseController.openFilter(btn, Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.filter_data))
		Global.res[Global.cur_project_name][Global.cur_request_name].res_filter.dialog.close()

		return


	# �� ����
	def deleteRow(obj:QWidget):
		for i in range(obj.findChild(QHBoxLayout).count()):
			deleteObject(obj.findChild(QHBoxLayout).itemAt(0).widget())  # ��ȣ, ���� �ڵ�, ���� ����, ���� �ð� �� ����
			#deleteObject(response_table.itemAt(0).widget().findChild(QHBoxLayout))  # �� ���̾ƿ� ����
		deleteObject(obj)  # �� ����

		return


	# ���� ����
	def applyFilter(filter_data:list=[]):
		#todo#
		# True �ɸ� ���� �ؼ�
		# �ö��ִ� �� �� ���� �ʴ� �� ����
		# ���� �ö���� �࿡�� ���� ����

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


	## UI ����
	# �⺻ UI ����
	def initUI(self, filter_data:list=[]):
		if len(filter_data)==0:
			## ������Ʈ ����
			self.dialog=QDialog()
			self.layout=QVBoxLayout()
			self.filter_list=QListWidget()
			self.add_filter_btn=QPushButton("+")

			## ������Ʈ ����
			self.dialog.setLayout(self.layout)
			# ����Ʈ ��
			self.layout.addLayout(QHBoxLayout())
			self.layout.itemAt(0).addWidget(QLabel("Type"))
			self.layout.itemAt(0).addWidget(QLabel("Filter"))
			self.layout.addWidget(self.filter_list)
			self.layout.addWidget(self.add_filter_btn)

			## �̺�Ʈ ����
			# + ��ư Ŭ��
			self.add_filter_btn.clicked.connect(self.addRow)
		else:
			for i in range(len(filter_data)):
				self.addRow(filter_data[i])  # ����Ʈ�� �� ����
					
			return
	# �� �߰�
	def addRow(self, ischecked:bool=True, filter_type:str="", filter_text:str=""):
		row_item=QListWidgetItem()
		row_widget=self.Row(ischecked, filter_type, filter_text)  # �� ����
		self.rightClickListener(row_widget).connect(self.viewContextMenu)  # ��Ŭ�� �̺�Ʈ ����
		row_item.setSizeHint(row_widget.sizeHint())  # ũ�� ����(�ʼ�)
		self.filter_list.insertItem(self.filter_list.count()-1, row_item)
		self.filter_list.setItemWidget(row_item, row_widget)

		return


	### �̺�Ʈ
	## ��Ŭ��
	# ��Ŭ�� �޴� ǥ��
	def viewContextMenu(self):
		menu=QMenu(self.last_right_clicked_obj, self.right_click_mouse_pos)
		
		# �� ����
		delete_filter_action=QAction("Delete")
		delete_filter_action.triggered.connect(self.deleteRow)
		menu.addAction(delete_filter_action)
		
		menu.exec(self.right_click_mouse_pos)  # ǥ��

		return
	# �� ����
	def deleteRow(self, event, index:int=-1):
		if index==-1:
			item_widget=self.last_right_clicked_obj
			row, index=self.getListItem(item_widget)
		else:
			item_widget=self.filter_list.itemWidget(self.filter_list.item(index))
			row=self.filter_list.item(index)

		
		# ������Ʈ ����
		deleteObject(item_widget.findChild(QHBoxLayout).itemAt(0).widget())  # üũ�ڽ�
		deleteObject(item_widget.findChild(QHBoxLayout).itemAt(0).widget())  # ��Ӵٿ�
		deleteObject(item_widget.findChild(QHBoxLayout).itemAt(0).widget())  # �Է� ĭ
		#deleteObject(item_widget.findChild(QHBoxLayout))
		deleteObject(item_widget)
		self.filter_list.takeItem(index)  # ����Ʈ���� ����

		return


	# ����Ʈ ���� ��� �����۰� �ε��� ��ȯ
	def getListItem(self, item_widget:QWidget) -> tuple:
		for i in range(self.filter_list.count()):
			item=self.filter_list.item(i)
			print(item, self.filter_list.itemWidget(item), item_widget)
			if self.filter_list.itemWidget(item)==item_widget:
				return item, i

		return
	# ���� ������ ��ȯ
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

			## ������Ʈ ����
			row=QHBoxLayout()
			type_dropdown=QComboBox()
			filter_if=QLineEdit(filter_text)

			## ������Ʈ ����
			row.addWidget(QCheckBox())
			row.addWidget(type_dropdown)
			row.addWidget(filter_if)

			## ��Ÿ ����
			# üũ�ڽ� üũ ���� ����
			row.itemAt(0).widget().setChecked(ischecked)
			# ��Ӵٿ� �ؽ�Ʈ ����
			for crtype in CONST.RESPONSE_FILTER_TYPE:
				tmp=crtype.name.split('_')  # _ ����
				for i in range(len(tmp)):
					tmp[i]=tmp[i].lower().capitalize()  # �ձ��� �빮�ڷ�
				type_dropdown.addItem(' '.join(tmp))  # ���� �߰�
			if filter_type=="":
				type_dropdown.setCurrentIndex(0)  # ù ���� ��ҷ� ����
			else:
				type_dropdown.setCurrentIndex(type_dropdown.findText(filter_type))
	
			## �̺�Ʈ ����
			type_dropdown.currentIndexChanged.connect(lambda: filter_if.setText(""))  # Ÿ�� ���� �� ���� ĭ ���

			self.setLayout(row)
	
			return





# ���� ���� �˾�
class ResponseView:
	def __init__(self, project_name:str="", request_name:str="", saved_name:str="", index:int=-1):
		self.project_name=project_name
		self.request_name=request_name
		self.saved_name=saved_name
		self.index=index

		self.initUI()  # UI ����

		if index==-1:  # ����� ���� ����
			project_path=Global.projects_data[project_name]["last_path"]

			saved_data=open(project_path+'/'+project_name+'/saved/'+saved_name+".rsv")  # ���� ����
			self.contents.setPlainText(saved_data.read())
			saved_data.close()  # ���� �ݱ�
		else:
			if project_name=="":
				self.contents.setPlainText(Global.res[Global.cur_project_name][Global.cur_request_name].response_data[index-1][1].text)
			else:
				self.contents.setPlainText(Global.res[project_name][request_name].response_data[index-1][1].text)
				# -> ResponseŬ����->���� ������ ����Ʈ->���� ������

		return


	def initUI(self) -> None:
		## ������Ʈ ����
		self.dialog=QWidget()
		self.window=QVBoxLayout()
		# ���
		self.header_div=QHBoxLayout()
		self.switch=QHBoxLayout()
		self.raw_switch=QPushButton("raw")
		self.pretty_switch=QPushButton("pretty")
		self.comparer_btn=QPushButton("Comparer")
		self.close_btn=QPushButton("X")
		# �ٵ�
		self.body_div=QHBoxLayout()
		self.contents=QTextEdit()

		## ������Ʈ ����
		# ����ġ ����
		self.switch.addWidget(self.raw_switch)
		self.switch.addWidget(self.pretty_switch)
		self.header_div.addLayout(self.switch)  # ��� �׷쿡 ����ġ �߰�
		self.header_div.addWidget(self.comparer_btn)
		self.header_div.addWidget(self.close_btn)
		self.body_div.addWidget(self.contents)
		# ȭ�� ����
		self.window.addLayout(self.header_div)
		self.window.addLayout(self.body_div)
		self.dialog.setLayout(self.window)
		self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
		self.dialog.setFixedSize(1280, 720)  # ȭ�� ũ��

		## �̺�Ʈ ����
		# ����ġ ����
		self.raw_switch.clicked.connect(self.switching_raw)
		self.pretty_switch.clicked.connect(self.switching_pretty)
		# ���ڷ� ������ ��ư ����
		self.comparer_btn.clicked.connect(lambda : ResponseController.sendComparer(self.project_name, self.request_name, self.saved_name, self.index))
		# �ݱ� ��ư ����
		self.close_btn.clicked.connect(self.dialog.close)
		# �巡�� �̺�Ʈ ����
		self.dialog.mousePressEvent=self.mousePressEvent
		self.dialog.mouseMoveEvent=self.mouseMoveEvent
		self.dialog.mouseReleaseEvent=self.mouseReleaseEvent

		## ��Ÿ ����
		# ����ġ ����
		self.raw_switch.setCheckable(True)
		self.raw_switch.setChecked(True)  # raw ���·� �⺻ ����
		self.pretty_switch.setCheckable(True)
		# �ؽ�Ʈ ���� ����
		self.contents.setReadOnly(True)  # �б� ����
			
		## ����
		self.dialog.show()
		self.dialog.destroyed.connect(lambda : print("close"))  # ���� �� close ���

		return



	### �̺�Ʈ
	## raw-pretty ����ġ
	# raw�� ��ȯ
	def switching_raw(self) -> None:
		if self.raw_switch.isChecked():
			return

		# ��Ŀ�� ����
		self.raw_switch.setChecked(True)
		self.pretty_switch.setChecked(False)
		
		self.contents.setPlainText(self.contents.toPlainText())  # �ؽ�Ʈ �Է�

		return
	# pretty�� ��ȯ
	def switching_pretty(self) -> None:
		if self.pretty_switch.isChecked():
			return

		# ��Ŀ�� ����
		self.raw_switch.setChecked(False)
		self.pretty_switch.setChecked(True)

		self.contents.setPlainText(self.contents.toPlainText())  # �ؽ�Ʈ �Է�

		return
	## â �巡��
	# ���콺 Ŭ��
	def mousePressEvent(self, event: QMouseEvent) -> None:
		self.mouse_start_postion=event.globalPos()  # Ŭ�� ��ġ ����
		self.widget_position=self.dialog.pos()  # â ��ġ ����

		return
	# ���콺 �̵�
	def mouseMoveEvent(self, event: QMouseEvent) -> None:
		if self.mouse_start_postion!=None:  # Ŭ�� �Ǿ����� ��
			# ��� �巡��
			self.dialog.move(self.widget_position.x()+event.globalPos().x()-self.mouse_start_postion.x(), \
			self.widget_position.y()+event.globalPos().y()-self.mouse_start_postion.y())

		return
	# ���콺 ����
	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		self.mouse_start_postion=None
		
		return



