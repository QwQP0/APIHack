from enum import Enum
import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


def isEmptyStr(s:str) -> bool:
	return len(s.split(' '))==len(s)+1


def deleteObject(obj):
	obj.setParent(None)
	obj.deleteLater()
	obj=None

	return

class File:
	# 프로젝트 생성
	def createProject(project_path:str, project_name:str, target_url:str):
		if not os.path.exists(project_path+'/'+project_name):  # 해당 이름이 이미 있는지 확인
			os.makedirs(project_path+'/'+project_name, mode=711)  # 프로젝트 폴더 생성
		else: 
			print("System.File.createProject : Project name already exists")  #todo# 알림으로 띄우기
			return False  # 프로젝트 생성 실패

		# 프로젝트 파일 구성
		project=open(project_path+'/'+project_name+'/'+project_name+".ahp", 'w')  # 프로젝트 파일 생성
		content={}
		content["last_path"]=project_path
		content["requests"]={}  # 요청 저장
		content["requests"][CONST.DEFAULT_NAME.REQUEST]=["", "", "", "GET"]  # 기본 요청 : [타겟, 헤더, 페이로드, 드롭다운 번호]
		content["variables"]={}  # 변수 저장
		if target_url!="":  # 타겟 URL을 입력 받았을 때
			content["requests"][CONST.DEFAULT_NAME.REQUEST][0]="{{$base_url}}"
			content["variables"]["base_url"]=("Fix", target_url)  # 기본 url 변수
		content["decoder"]={}
		content["decoder"]["inputs"]=["", ""]  # 입력 구역
		content["decoder"]["functions"]=[("", "")]  # 기능 구역
		content["decoder"]["enable_index"]=1  # 비활성화 기준 지점
		content["decoder"]["error_index"]=-1  # 오류 시작 지점
		project.write(json.dumps(content))  # 암호화(아직 안함) 후 파일 작성
		project.close()  # 파일 닫기

		# 저장 폴더
		os.makedirs(project_path+'/'+project_name+'/saved', mode=711)

		# 로그 파일 생성
		open(project_path+'/'+project_name+'/'+"log.txt", 'w').close()

		return File.openProject(project_path, project_name)
	# 프로젝트 불러오기
	def openProject(project_path:str, project_name:str) -> str:
		if project_name in Global.projects_data:
			print("System.File.openProject : Project is already opened")
			return False

		project=open(project_path+'/'+project_name+'/'+project_name+".ahp")
		content_json=json.loads(project.read())  # 복호화(아직 안함) 후 json 변환
		project.close()
		
		Global.projects_data[project_name]=content_json  # 프로젝트 데이터 저장
		Global.res[project_name]={}  # 프로젝트 응답 탭 저장 변수(휘발성)
		Global.request_thread[project_name]={}  # 프로젝트 요청 스레드 저장 변수(휘발성)

		return True
	# 프로젝트 저장
	def saveProject(project_name:str):
		print("System.File.saveProject : Project Name-"+project_name)
		project=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+project_name+".ahp", 'w')
		project.write(json.dumps(Global.projects_data[project_name]))  # 암호화(아직 안함) 후 파일 작성
		project.close()

		return
	# 로그 작성
	def appendLog(project_name:str, text:str):
		log=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+"log.txt", 'a')
		log.write("LOG: "+text+"\n")
		log.close()

		return


	# 복제, 저장 시 자동으로 이름 설정
	def setNameAuto(basename:str, path:str, content_type:str) -> str:
		if basename=="":
			if content_type=='p':  # 프로젝트
				if not File.isInvalidName(CONST.DEFAULT_NAME.PROJECT, path, content_type):
					return CONST.DEFAULT_NAME.PROJECT
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.PROJECT, path, content_type)
			if content_type=='q':  # 요청
				if not File.isInvalidName(CONST.DEFAULT_NAME.REQUEST, path, content_type):
					return CONST.DEFAULT_NAME.REQUEST
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.REQUEST, path, content_type)
			if content_type=='s':  # 저장 파일
				if not File.isInvalidName(CONST.DEFAULT_NAME.SAVED, path, content_type):
					return CONST.DEFAULT_NAME.SAVED
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.SAVED, path, content_type)
			if content_type=='v':  # 변수
				if not File.isInvalidName(CONST.DEFAULT_NAME.VAR, path, content_type):
					return CONST.DEFAULT_NAME.VAR
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.VAR, path, content_type)

		## 괄호 안 숫자 추출
		# 뒤에서 첫 번째 괄호 탐색
		s=-1
		e=-1
		for i in range(len(basename)-1, -1, -1):
			if basename[i]==')':
				e=i
			if basename[i]=='(':
				if e!=-1:
					s=i
					break
		# 괄호가 유효한지
		if e!=len(basename)-1:  # 끝에 붙은 괄호 아님
			is_copied_name=False
		else:
			try:
				int(basename[s+1:e])
				is_copied_name=True
			except:  # 괄호 내 글자가 숫자가 아님
				is_copied_name=False

		if is_copied_name:  # 복사된 이름 맞음
			last_num=int(basename[s+1:e])
			basename=basename[:len(basename)-2-len(str(last_num))]  # 순수 이름 추출(괄호와 숫자 길이 뺌)
		else:  # 복사된 이름 아님
			last_num=0
		
		while True:
			last_num+=1
			if not File.isInvalidName(basename+'('+str(last_num)+')', path, content_type):  # 새 이름 생성
				return basename+'('+str(last_num)+')'

		return
	# 이름 유효 검사(빈 칸, 중복 이름, 슬래시 여부)
	def isInvalidName(name:str, path:str="", content_type:str="") -> bool:
		print(name, path)
		if isEmptyStr:  # 빈칸임
			return True
		if len(name.split('/'))!=1:  # 슬래시가 포함된 이름
			return True
		
		if content_type=='p':  # 프로젝트
			return os.path.exists(path+'/'+name)
		elif content_type=='q':  # 요청
			if name in list(Global.projects_data[path]["requests"].keys()):
				return True
			else:
				return False
		elif content_type=='s':  # 저장 파일
			return os.path.exists(Global.projects_data[path]["last_path"]+'/'+path+"/saved/"+name+".rsv")
		elif content_type=='v':  # 변수
			if name in list(Global.projects_data[path]["variables"].keys()):
				return True
			else:
				return False
		else:
			return False

		return True


class Global:
	default_project_path:str=""

	projects_data:dict={}

	cur_project_name:str=""
	cur_request_name:str=""

	# 클래스
	main=None
	sdv=None  # 사이드 뷰
	dcd=None  # 디코더 탭
	cmp=None  # 비교자 탭
	req=None  # 요청 탭
	var=None  # 변수 탭
	res:dict={}  # 응답 탭(요청마다 분리)

	request_thread:dict={}  # 요청 스레드


class CONST:
	class DEFAULT_NAME:
		PROJECT="My project"
		REQUEST="New Request"
		SAVED="Response"
		VAR="var"



	class REQUEST_TYPE(Enum):
		GET=1
		POST=2
		PUT=3
		DELETE=999



	class VARIABLES_TYPE(Enum):
		CONST=1
		NUMBER=2
		LIST=3
		STRING=4



	class VARIABLES_SPLIT_TYPE(Enum):
		VAR=0
		NORMAL=1
		FUNC_OPEN=10
		FUNC_CLOSE=20



	class DECODER_MODE(Enum):
		DECODE=1
		ENCODE=2
		


	class DECODER_TYPE(Enum):
		BASE_64=1
		SHA=2



	class RESPONSE_FILTER_TYPE(Enum):
		RESPONSE_CODE=1
		LENGTH=2
		RESPONSE_TIME=3
		WORD=4

	DECODER_DEFAULT_FUNCTION=(DECODER_MODE.DECODE.name, DECODER_TYPE.BASE_64.name)





class InputDialog(QDialog):
	def __init__(self, label:str="", default_text:str="", error_text:str="", checker=None, *params):
		self.return_data=()

		## 오브젝트 선언
		super().__init__()
		self.div=QVBoxLayout()
		self.label=QLabel(label)
		self.text=QLineEdit(default_text)
		self.error_text=QLabel(error_text)
		self.ok_btn=QPushButton("OK")
		self.cancel_btn=QPushButton("Cancel")

		## 오브젝트 구성
		self.div.addWidget(self.label)
		self.div.addWidget(self.text)
		self.div.addWidget(self.error_text)
		# 버튼
		self.div.addLayout(QHBoxLayout())
		self.div.itemAt(3).addWidget(self.ok_btn)
		self.div.itemAt(3).addWidget(self.cancel_btn)
		
		## 이벤트 연결
		# 버튼 클릭 이벤트
		self.ok_btn.clicked.connect(self.onClickOK)
		self.cancel_btn.clicked.connect(self.onClickCancel)
		# 텍스트 변경
		self.text.textChanged.connect(lambda: self.checkInvaildText(checker, params))
		print(params)

		## 기타 설정
		self.error_text.setStyleSheet("color:#c33")  # 오류 텍스트 색 설정
		self.setLayout(self.div)
		self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

		self.exec()

		return


	### 이벤트
	## 버튼 이벤트
	# 확인 버튼 클릭
	def onClickOK(self) -> tuple:
		self.close()
		self.return_data=(self.text.text(), True)

		return 
	# 취소 버튼 클릭
	def onClickCancel(self) -> tuple:
		self.close()
		self.return_data=("", False)

		return
	## 텍스트 변경 이벤트
	# 텍스트 변경 시 유효성 검사
	def checkInvaildText(self, checker, params):
		if checker(self.text.text(), params[0], params[1]):
			self.error_text.setText("Invalid name")  #todo# 부적절한 이유 설명
			self.ok_btn.setDisabled(True)  # 버튼 비활성화
		else:
			self.error_text.setText("")
			self.ok_btn.setDisabled(False)

		return