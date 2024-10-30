#################### Imports ####################


import time
import requests

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout

from System import CONST, File, Global
from Variables import VarParser, Variables


##################### Main ######################



class Request:
	def __init__(self, parent):
		self.request_tab_content=QVBoxLayout(parent)

		self.initUI()

		return

	
	## ������ ����
	# ������ ���� �� ���� �ҷ�����
	def getTabInfo(self) -> list:
		request_data=[]
		request_data.append(self.target.text())
		request_data.append(self.header.toPlainText())
		request_data.append(self.payload.toPlainText())
		request_data.append(self.req_type_dropdown.currentText())

		return request_data


	## �� ����
	# UI ����
	def initUI(self, request_data:list=None):
		if request_data==None:  # �⺻ UI ����
			## ������Ʈ ����
			# ����
			self.target_div=QVBoxLayout()  # Ÿ�� ����
			self.header_div=QVBoxLayout()  # ��� ����
			self.payload_div=QVBoxLayout()  # ���̷ε� ����
			# �Է� ĭ
			self.target=QLineEdit()  # Ÿ�� url �Է� ĭ
			self.header=QTextEdit()  # ��� �Է� ĭ
			self.payload=QTextEdit()  # ���̷ε� �Է� ĭ
			# ��Ӵٿ�
			self.req_type_dropdown=QComboBox()  # ��û ��� ��Ӵٿ�
			# ��ư
			self.request_btn=QPushButton("Request")  # ��û ��ư

			## UI ����
			# Ÿ�� ���� ����
			self.target_div.addWidget(QLabel("Target"))
			self.target_div.addLayout(QHBoxLayout())
			self.target_div.children()[0].addWidget(self.target)
			self.target_div.children()[0].addWidget(self.req_type_dropdown)
			# ��� ���� ����
			self.header_div.addWidget(QLabel("Header"))
			self.header_div.addWidget(self.header)
			# ���̷ε� ���� ����
			self.payload_div.addWidget(QLabel("Payload"))
			self.payload_div.addWidget(self.payload)
			# �� ����
			self.request_tab_content.addLayout(self.target_div)  # Ÿ�� ���� ����
			self.request_tab_content.addLayout(self.header_div)  # ��� ���� ����
			self.request_tab_content.addLayout(self.payload_div) # ���̷ε� ���� ����
			self.request_tab_content.addWidget(self.request_btn)  # Ÿ�� ���� ����

			for rest in CONST.REQUEST_TYPE:  # ��Ӵٿ �׸� �߰�
				self.req_type_dropdown.addItem(rest.name)  # �߰�

			# �̺�Ʈ ����
			self.request_btn.clicked.connect(self.onClickRequest)  # ��û ��ư Ŭ�� ��; ��û
		else:  # ��û ������ �Է�
			self.target.setText(request_data[0])
			self.header.setPlainText(request_data[1])
			self.payload.setPlainText(request_data[2])
			self.req_type_dropdown.setCurrentIndex(self.req_type_dropdown.findText(request_data[3]))

			#todo#Global.request_thread���� ��û ������

		return
		

	## ��ư Ŭ�� �̺�Ʈ
	# ��û ������ ����
	def onClickRequest(self):
		Global.main.main_tabs.setCurrentIndex(2)  # ���� ������ ��ȯ
		project_name=Global.cur_project_name  # ���� ������Ʈ ����
		request_name=Global.cur_request_name  # ���� ��û ����

		Global.res[project_name][request_name].clearData()  # ���� ���̺� ������ ����

		# ���� �� ��Ȳ ����
		Global.projects_data[project_name]["requests"][request_name]=Global.req.getTabInfo()  # ��û ��
		Global.projects_data[project_name]["variables"]=Global.var.getTabInfo()  # ���� ��
		Global.projects_data[project_name]["decoder"]=Global.dcd.getTabInfo()  # ���ڴ� ��
		File.saveProject(project_name)  # ������Ʈ ���� ����

		# ��û ����
		Global.request_thread[project_name][request_name]=self.RequestAPI(project_name, request_name, self.getTabInfo())  # ������
		Global.request_thread[project_name][request_name].response_signal.connect(Global.res[project_name][request_name].addRow)   # �ش� ��û�� ����� ����
		Global.request_thread[project_name][request_name].start()  # ������ ����

		return
	# ��û ������
	class RequestAPI(QThread):
		response_signal=Signal(float, requests.Response)  # �ñ׳η� ���� ������ Ÿ�� ����

		def __init__(self, project_name, request_name, request_data:list):
			super().__init__()

			self.project_name=project_name
			self.request_name=request_name

			self.target=request_data[0]
			self.header=request_data[1]
			self.payload=request_data[2]
			self.req_type=request_data[3].lower()

			return


		# ��û
		def run(self):
			print("Request.requestAPI : Vars-", Global.projects_data[self.project_name]["variables"])
			self.iterator=VarParser(Global.projects_data[self.project_name]["variables"], self.target, self.header, self.payload)
			self.request_params=self.iterator.varToText()

			for t, h, p in self.request_params:  # ��û ��ȸ
				print("Request.requestAPI : Target-\t"+t)
				print("Request.requestAPI : Header-\t"+h)
				print("Request.requestAPI : Payload-\t"+p)
				print("-------------------------------------------------------------")

				request_time=time.time()
				res=getattr(requests, self.req_type)(t)  # ��û  #todo# ���,���̷ε� �߰��Ұ�
				response_time=time.time()

				self.response_signal.emit(response_time-request_time, res)

			return