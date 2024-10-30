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

	
	## 데이터 관리
	# 저장을 위한 탭 정보 불러오기
	def getTabInfo(self) -> list:
		request_data=[]
		request_data.append(self.target.text())
		request_data.append(self.header.toPlainText())
		request_data.append(self.payload.toPlainText())
		request_data.append(self.req_type_dropdown.currentText())

		return request_data


	## 탭 구성
	# UI 구성
	def initUI(self, request_data:list=None):
		if request_data==None:  # 기본 UI 구성
			## 오브젝트 선언
			# 구역
			self.target_div=QVBoxLayout()  # 타겟 구역
			self.header_div=QVBoxLayout()  # 헤더 구역
			self.payload_div=QVBoxLayout()  # 페이로드 구역
			# 입력 칸
			self.target=QLineEdit()  # 타겟 url 입력 칸
			self.header=QTextEdit()  # 헤더 입력 칸
			self.payload=QTextEdit()  # 페이로드 입력 칸
			# 드롭다운
			self.req_type_dropdown=QComboBox()  # 요청 모드 드롭다운
			# 버튼
			self.request_btn=QPushButton("Request")  # 요청 버튼

			## UI 구성
			# 타겟 구역 구성
			self.target_div.addWidget(QLabel("Target"))
			self.target_div.addLayout(QHBoxLayout())
			self.target_div.children()[0].addWidget(self.target)
			self.target_div.children()[0].addWidget(self.req_type_dropdown)
			# 헤더 구역 구성
			self.header_div.addWidget(QLabel("Header"))
			self.header_div.addWidget(self.header)
			# 페이로드 구역 구성
			self.payload_div.addWidget(QLabel("Payload"))
			self.payload_div.addWidget(self.payload)
			# 탭 구성
			self.request_tab_content.addLayout(self.target_div)  # 타겟 구역 조립
			self.request_tab_content.addLayout(self.header_div)  # 헤더 구역 조립
			self.request_tab_content.addLayout(self.payload_div) # 페이로드 구역 조립
			self.request_tab_content.addWidget(self.request_btn)  # 타겟 구역 조립

			for rest in CONST.REQUEST_TYPE:  # 드롭다운에 항목 추가
				self.req_type_dropdown.addItem(rest.name)  # 추가

			# 이벤트 연결
			self.request_btn.clicked.connect(self.onClickRequest)  # 요청 버튼 클릭 시; 요청
		else:  # 요청 데이터 입력
			self.target.setText(request_data[0])
			self.header.setPlainText(request_data[1])
			self.payload.setPlainText(request_data[2])
			self.req_type_dropdown.setCurrentIndex(self.req_type_dropdown.findText(request_data[3]))

			#todo#Global.request_thread에서 요청 중인지

		return
		

	## 버튼 클릭 이벤트
	# 요청 스레드 시작
	def onClickRequest(self):
		Global.main.main_tabs.setCurrentIndex(2)  # 응답 탭으로 전환
		project_name=Global.cur_project_name  # 현재 프로젝트 저장
		request_name=Global.cur_request_name  # 현재 요청 저장

		Global.res[project_name][request_name].clearData()  # 응답 테이블 데이터 삭제

		# 현재 탭 현황 저장
		Global.projects_data[project_name]["requests"][request_name]=Global.req.getTabInfo()  # 요청 탭
		Global.projects_data[project_name]["variables"]=Global.var.getTabInfo()  # 변수 탭
		Global.projects_data[project_name]["decoder"]=Global.dcd.getTabInfo()  # 디코더 탭
		File.saveProject(project_name)  # 프로젝트 파일 저장

		# 요청 시작
		Global.request_thread[project_name][request_name]=self.RequestAPI(project_name, request_name, self.getTabInfo())  # 스레드
		Global.request_thread[project_name][request_name].response_signal.connect(Global.res[project_name][request_name].addRow)   # 해당 요청의 응답과 연결
		Global.request_thread[project_name][request_name].start()  # 스레드 실행

		return
	# 요청 스레드
	class RequestAPI(QThread):
		response_signal=Signal(float, requests.Response)  # 시그널로 보낼 데이터 타입 설정

		def __init__(self, project_name, request_name, request_data:list):
			super().__init__()

			self.project_name=project_name
			self.request_name=request_name

			self.target=request_data[0]
			self.header=request_data[1]
			self.payload=request_data[2]
			self.req_type=request_data[3].lower()

			return


		# 요청
		def run(self):
			print("Request.requestAPI : Vars-", Global.projects_data[self.project_name]["variables"])
			self.iterator=VarParser(Global.projects_data[self.project_name]["variables"], self.target, self.header, self.payload)
			self.request_params=self.iterator.varToText()

			for t, h, p in self.request_params:  # 요청 순회
				print("Request.requestAPI : Target-\t"+t)
				print("Request.requestAPI : Header-\t"+h)
				print("Request.requestAPI : Payload-\t"+p)
				print("-------------------------------------------------------------")

				request_time=time.time()
				res=getattr(requests, self.req_type)(t)  # 요청  #todo# 헤더,페이로드 추가할것
				response_time=time.time()

				self.response_signal.emit(response_time-request_time, res)

			return