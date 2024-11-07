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
        self.target_div=QBoxLayout(QBoxLayout.TopToBottom)  # 타겟 구역
        self.header_div=QBoxLayout(QBoxLayout.TopToBottom)  # 헤더 구역
        self.payloads_div=QBoxLayout(QBoxLayout.TopToBottom)  # 페이로드 구역
        
        ## 타겟 구역 구성
        self.target_div.addWidget(QLabel("Target"))
        self.target_div.addLayout(QBoxLayout(QBoxLayout.LeftToRight))
        #self.target=QLineEdit("${base_url}")  # 타겟 url 입력 칸
        self.target=QLineEdit()  # 타겟 url 입력 칸
        self.rest_dropdown=QComboBox()  # 모드 드롭다운
        
        for rest in System.CONST.REQUEST_TYPE:  # 드롭다운에 항목 추가
            self.rest_dropdown.addItem(rest.name)  # 추가

        self.target_div.children()[0].addWidget(self.target)
        self.target_div.children()[0].addWidget(self.rest_dropdown)
        self.request_tab_content.addLayout(self.target_div)

        ## 헤더 구역 구성
        self.header_div.addWidget(QLabel("Header"))
        self.header=QTextEdit()  # 헤더 입력 칸
        self.header_div.addWidget(self.header)
        self.request_tab_content.addLayout(self.header_div)

        ## 페이로드 구역 구성
        self.payloads_div.addWidget(QLabel("Payloads"))
        self.payloads=QTextEdit()  # 페이로드 입력 칸
        self.payloads_div.addWidget(self.payloads)
        self.request_tab_content.addLayout(self.payloads_div)

        ## 요청 버튼 구성
        self.request_btn=QPushButton("Request")
        self.request_btn.clicked.connect(self.onClickRequest)
        self.request_tab_content.addWidget(self.request_btn)

    # 프로젝트 생성/불러오기 시 타겟 기본값 지정
    def initRequest(self, project_name, request_name):
        self.target.setText(System.Global.projects_data[project_name]["requests"][request_name][0])  # 타겟 url 입력
        self.rest_dropdown.setCurrentIndex(System.Global.projects_data[project_name]["requests"][request_name][1])  # 드롭다운 설정
        self.header.setPlainText(System.Global.projects_data[project_name]["requests"][request_name][2])  # 헤더 입력
        self.payloads.setPlainText(System.Global.projects_data[project_name]["requests"][request_name][3])  # 페이로드 입력

    # 요청 탭 현재 정보 반환
    def getTabInfo(self):
        req_info=[self.target.text(), self.rest_dropdown.currentIndex(), self.header.toPlainText(), self.payloads.toPlainText()]
        System.Global.projects_data[System.Global.main.last_highlighted_project]["requests"][System.Global.main.last_highlighted_request]=req_info

    # 요청 스레드 시작
    def onClickRequest(self):
        System.Global.var.getTabInfo()  # 변수 탭 정보 Global에 저장
        self.getTabInfo()  # 요청 탭 정보 Global에 저장
        System.File.saveProject(System.Global.main.last_highlighted_project)  # 현재 프로젝트 저장

        # 요청 시작
        self.request_thread=self.requestAPI(self.rest_dropdown.currentText().lower(), self.target.text(), self.header.toPlainText(), self.payloads.toPlainText())
        self.request_thread.response_signal.connect(System.Global.res.addRow)
        self.request_thread.start()

    # 요청 스레드
    class requestAPI(QThread):
        response_signal=Signal(float)

        def __init__(self, req_type:str, target:str, header:str, payloads:str):
            self.req_type=req_type
            self.target=target
            self.header=header
            self.payloads=payloads
            super().__init__()

        # 요청
        def run(self):
            print("Request.requestAPI : Vars-", System.Global.projects_data[System.Global.main.last_highlighted_project]["variables"])  # LOG
            self.request_params=Variables.getPlainText(self.target, self.header, self.payloads)

            for t, h, p in self.request_params:  # 요청 순회
                print("Request.requestAPI : Target-\t"+t)
                print("Request.requestAPI : Header-\t"+h)
                print("Request.requestAPI : Payload-\t"+p)
                print("-------------------------------------------------------------")
                request_time=time.time()
                res=getattr(requests, self.req_type.lower())(t)  # 요청  #todo# 헤더,페이로드 추가할것
                response_time=time.time()
                System.Global.responses.append(res)
                self.response_signal.emit(response_time-request_time)











