#################### Imports ####################

import time
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QBoxLayout, QComboBox, QLabel, QLineEdit, QPushButton, QTextEdit

import requests

import System
from Variables import Variables


###################### Main #####################

class Request():
    def __init__(self, parent):
        self.request_tab_content=QBoxLayout(QBoxLayout.TopToBottom, parent)
        self.initUI()


    def initUI(self):
        self.target_div=QBoxLayout(QBoxLayout.TopToBottom)  # Ÿ�� ����
        self.header_div=QBoxLayout(QBoxLayout.TopToBottom)  # ��� ����
        self.payloads_div=QBoxLayout(QBoxLayout.TopToBottom)  # ���̷ε� ����
        
        ## Ÿ�� ���� ����
        self.target_div.addWidget(QLabel("Target"))
        self.target_div.addLayout(QBoxLayout(QBoxLayout.LeftToRight))
        #self.target=QLineEdit("${base_url}")  # Ÿ�� url �Է� ĭ
        self.target=QLineEdit()  # Ÿ�� url �Է� ĭ
        self.rest_dropdown=QComboBox()  # ��� ��Ӵٿ�
        
        for rest in System.CONST.REQUEST_TYPE:  # ��Ӵٿ �׸� �߰�
            self.rest_dropdown.addItem(rest.name)  # �߰�

        self.target_div.children()[0].addWidget(self.target)
        self.target_div.children()[0].addWidget(self.rest_dropdown)
        self.request_tab_content.addLayout(self.target_div)

        ## ��� ���� ����
        self.header_div.addWidget(QLabel("Header"))
        self.header=QTextEdit()  # ��� �Է� ĭ
        self.header_div.addWidget(self.header)
        self.request_tab_content.addLayout(self.header_div)

        ## ���̷ε� ���� ����
        self.payloads_div.addWidget(QLabel("Payloads"))
        self.payloads=QTextEdit()  # ���̷ε� �Է� ĭ
        self.payloads_div.addWidget(self.payloads)
        self.request_tab_content.addLayout(self.payloads_div)

        ## ��û ��ư ����
        self.request_btn=QPushButton("Request")
        self.request_btn.clicked.connect(self.onClickRequest)
        self.request_tab_content.addWidget(self.request_btn)

    # ������Ʈ ����/�ҷ����� �� Ÿ�� �⺻�� ����
    def initRequest(self, project_name, request_name):
        self.target.setText(System.Global.projects_data[project_name]["requests"][request_name][0])  # Ÿ�� url �Է�
        self.rest_dropdown.setCurrentIndex(System.Global.projects_data[project_name]["requests"][request_name][1])  # ��Ӵٿ� ����
        self.header.setPlainText(System.Global.projects_data[project_name]["requests"][request_name][2])  # ��� �Է�
        self.payloads.setPlainText(System.Global.projects_data[project_name]["requests"][request_name][3])  # ���̷ε� �Է�

    # ��û �� ���� ���� ��ȯ
    def getTabInfo(self):
        req_info=[self.target.text(), self.rest_dropdown.currentIndex(), self.header.toPlainText(), self.payloads.toPlainText()]
        System.Global.projects_data[System.Global.main.last_highlighted_project]["requests"][System.Global.main.last_highlighted_request]=req_info

    # ��û ������ ����
    def onClickRequest(self):
        System.Global.var.getTabInfo()  # ���� �� ���� Global�� ����
        self.getTabInfo()  # ��û �� ���� Global�� ����
        System.File.saveProject(System.Global.main.last_highlighted_project)  # ���� ������Ʈ ����

        # ��û ����
        self.request_thread=self.requestAPI(self.rest_dropdown.currentText().lower(), self.target.text(), self.header.toPlainText(), self.payloads.toPlainText())
        self.request_thread.response_signal.connect(System.Global.res.addRow)
        self.request_thread.start()

    # ��û ������
    class requestAPI(QThread):
        response_signal=Signal(float)

        def __init__(self, req_type:str, target:str, header:str, payloads:str):
            self.req_type=req_type
            self.target=target
            self.header=header
            self.payloads=payloads
            super().__init__()

        # ��û
        def run(self):
            print("Request.requestAPI : Vars-", System.Global.projects_data[System.Global.main.last_highlighted_project]["variables"])  # LOG
            self.request_params=Variables.getPlainText(self.target, self.header, self.payloads)

            for t, h, p in self.request_params:  # ��û ��ȸ
                print("Request.requestAPI : Target-\t"+t)
                print("Request.requestAPI : Header-\t"+h)
                print("Request.requestAPI : Payload-\t"+p)
                print("-------------------------------------------------------------")
                request_time=time.time()
                res=getattr(requests, self.req_type.lower())(t)  # ��û  #todo# ���,���̷ε� �߰��Ұ�
                response_time=time.time()
                System.Global.responses.append(res)
                self.response_signal.emit(response_time-request_time)











