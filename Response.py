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


	# ���� ������ ����
	def clearData(self):
		self.response_data=[]
		ResponseController.clearTable(self.response_table)

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(0+" responses")  # ���� �� ǥ�� �� ����

		return


	# �� �߰�
	def addRow(self, response_time:float, response_data:requests.Response):
		self.response_data.append((response_time, response_data))  # ������ �߰�
		self.response_table.insertWidget(1, ResponseController.initRow(len(self.response_data), response_time, response_data))  # ���̺� �ֻ��(�� �ٷ� �Ʒ�)�� ����

		self.response_tab_content_layout.itemAt(0).itemAt(0).widget().setText(str(self.response_data)+" responses")  # ���� �� ǥ�� �� ����

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

		return response_table
	# ���� ���̺� �� ����
	def initRow(num:int, response_time:float, response_data:requests.Response) -> QWidget:
		new_row_widget=QWidget()
		new_row=QHBoxLayout(new_row_widget)

		new_row.addWidget(QLabel(str(num)))  # ��ȣ
		new_row.addWidget(QLabel(str(response_data.status_code)))  # ���� �ڵ�
		new_row.addWidget(QLabel(str(len(response_data.content))))  # ���� ����
		new_row.addWidget(QLabel(str(response_time)))  # ���� �ҿ� �ð�

		return new_row_widget
	# ���� ���̺� ���
	def clearTable(response_table:QVBoxLayout):
		for i in range(1, response_table.count()):
			for j in range(response_table.itemAt(0).widget().findChild(QHBoxLayout).count()):
				deleteObject(response_table.itemAt(0).widget().findChild(QHBoxLayout).itemAt(0).widget())  # ��ȣ, ���� �ڵ�, ���� ����, ���� �ð� �� ����
			#deleteObject(response_table.itemAt(0).widget().findChild(QHBoxLayout))  # �� ���̾ƿ� ����
			deleteObject(response_table.itemAt(0).widget())  # �� ����

		return



	class Loading(QThread):
		pass



	class Filter(QWidget):
		pass



# ���� ���� �˾�
class ResponseView():
	def __init__(self, project_name:str=None, request_name:str=None, saved_name:str=None, index:int=-1):
		self.initUI()  # UI ����

		if index==-1:  # ����� ���� ����
			project_path=Global.projects_data[project_name]["last_path"]

			saved_data=open(project_path+'/'+project_name+'/saved/'+saved_name+".rsv")  # ���� ����
			self.contents.setPlainText(saved_data.read())
			saved_data.close()  # ���� �ݱ�
		else:
			self.contents.setPlainText(Global.res[project_name][request_name].response_data[index][1].text)
			# -> ResponseŬ����->���� ������ ����Ʈ->���� ������


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
		#todo# ���ڷ� ������
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

