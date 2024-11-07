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
	# ������Ʈ ����
	def createProject(project_path:str, project_name:str, target_url:str):
		if not os.path.exists(project_path+'/'+project_name):  # �ش� �̸��� �̹� �ִ��� Ȯ��
			os.makedirs(project_path+'/'+project_name, mode=711)  # ������Ʈ ���� ����
		else: 
			print("System.File.createProject : Project name already exists")  #todo# �˸����� ����
			return False  # ������Ʈ ���� ����

		# ������Ʈ ���� ����
		project=open(project_path+'/'+project_name+'/'+project_name+".ahp", 'w')  # ������Ʈ ���� ����
		content={}
		content["last_path"]=project_path
		content["requests"]={}  # ��û ����
		content["requests"][CONST.DEFAULT_NAME.REQUEST]=["", "", "", "GET"]  # �⺻ ��û : [Ÿ��, ���, ���̷ε�, ��Ӵٿ� ��ȣ]
		content["variables"]={}  # ���� ����
		if target_url!="":  # Ÿ�� URL�� �Է� �޾��� ��
			content["requests"][CONST.DEFAULT_NAME.REQUEST][0]="{{$base_url}}"
			content["variables"]["base_url"]=("Fix", target_url)  # �⺻ url ����
		content["decoder"]={}
		content["decoder"]["inputs"]=["", ""]  # �Է� ����
		content["decoder"]["functions"]=[("", "")]  # ��� ����
		content["decoder"]["enable_index"]=1  # ��Ȱ��ȭ ���� ����
		content["decoder"]["error_index"]=-1  # ���� ���� ����
		project.write(json.dumps(content))  # ��ȣȭ(���� ����) �� ���� �ۼ�
		project.close()  # ���� �ݱ�

		# ���� ����
		os.makedirs(project_path+'/'+project_name+'/saved', mode=711)

		# �α� ���� ����
		open(project_path+'/'+project_name+'/'+"log.txt", 'w').close()

		return File.openProject(project_path, project_name)
	# ������Ʈ �ҷ�����
	def openProject(project_path:str, project_name:str) -> str:
		if project_name in Global.projects_data:
			print("System.File.openProject : Project is already opened")
			return False

		project=open(project_path+'/'+project_name+'/'+project_name+".ahp")
		content_json=json.loads(project.read())  # ��ȣȭ(���� ����) �� json ��ȯ
		project.close()
		
		Global.projects_data[project_name]=content_json  # ������Ʈ ������ ����
		Global.res[project_name]={}  # ������Ʈ ���� �� ���� ����(�ֹ߼�)
		Global.request_thread[project_name]={}  # ������Ʈ ��û ������ ���� ����(�ֹ߼�)

		return True
	# ������Ʈ ����
	def saveProject(project_name:str):
		print("System.File.saveProject : Project Name-"+project_name)
		project=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+project_name+".ahp", 'w')
		project.write(json.dumps(Global.projects_data[project_name]))  # ��ȣȭ(���� ����) �� ���� �ۼ�
		project.close()

		return
	# �α� �ۼ�
	def appendLog(project_name:str, text:str):
		log=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+"log.txt", 'a')
		log.write("LOG: "+text+"\n")
		log.close()

		return


	# ����, ���� �� �ڵ����� �̸� ����
	def setNameAuto(basename:str, path:str, content_type:str) -> str:
		if basename=="":
			if content_type=='p':  # ������Ʈ
				if not File.isInvalidName(CONST.DEFAULT_NAME.PROJECT, path, content_type):
					return CONST.DEFAULT_NAME.PROJECT
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.PROJECT, path, content_type)
			if content_type=='q':  # ��û
				if not File.isInvalidName(CONST.DEFAULT_NAME.REQUEST, path, content_type):
					return CONST.DEFAULT_NAME.REQUEST
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.REQUEST, path, content_type)
			if content_type=='s':  # ���� ����
				if not File.isInvalidName(CONST.DEFAULT_NAME.SAVED, path, content_type):
					return CONST.DEFAULT_NAME.SAVED
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.SAVED, path, content_type)
			if content_type=='v':  # ����
				if not File.isInvalidName(CONST.DEFAULT_NAME.VAR, path, content_type):
					return CONST.DEFAULT_NAME.VAR
				else:
					return File.setNameAuto(CONST.DEFAULT_NAME.VAR, path, content_type)

		## ��ȣ �� ���� ����
		# �ڿ��� ù ��° ��ȣ Ž��
		s=-1
		e=-1
		for i in range(len(basename)-1, -1, -1):
			if basename[i]==')':
				e=i
			if basename[i]=='(':
				if e!=-1:
					s=i
					break
		# ��ȣ�� ��ȿ����
		if e!=len(basename)-1:  # ���� ���� ��ȣ �ƴ�
			is_copied_name=False
		else:
			try:
				int(basename[s+1:e])
				is_copied_name=True
			except:  # ��ȣ �� ���ڰ� ���ڰ� �ƴ�
				is_copied_name=False

		if is_copied_name:  # ����� �̸� ����
			last_num=int(basename[s+1:e])
			basename=basename[:len(basename)-2-len(str(last_num))]  # ���� �̸� ����(��ȣ�� ���� ���� ��)
		else:  # ����� �̸� �ƴ�
			last_num=0
		
		while True:
			last_num+=1
			if not File.isInvalidName(basename+'('+str(last_num)+')', path, content_type):  # �� �̸� ����
				return basename+'('+str(last_num)+')'

		return
	# �̸� ��ȿ �˻�(�� ĭ, �ߺ� �̸�, ������ ����)
	def isInvalidName(name:str, path:str="", content_type:str="") -> bool:
		print(name, path)
		if isEmptyStr:  # ��ĭ��
			return True
		if len(name.split('/'))!=1:  # �����ð� ���Ե� �̸�
			return True
		
		if content_type=='p':  # ������Ʈ
			return os.path.exists(path+'/'+name)
		elif content_type=='q':  # ��û
			if name in list(Global.projects_data[path]["requests"].keys()):
				return True
			else:
				return False
		elif content_type=='s':  # ���� ����
			return os.path.exists(Global.projects_data[path]["last_path"]+'/'+path+"/saved/"+name+".rsv")
		elif content_type=='v':  # ����
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

	# Ŭ����
	main=None
	sdv=None  # ���̵� ��
	dcd=None  # ���ڴ� ��
	cmp=None  # ���� ��
	req=None  # ��û ��
	var=None  # ���� ��
	res:dict={}  # ���� ��(��û���� �и�)

	request_thread:dict={}  # ��û ������


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

		## ������Ʈ ����
		super().__init__()
		self.div=QVBoxLayout()
		self.label=QLabel(label)
		self.text=QLineEdit(default_text)
		self.error_text=QLabel(error_text)
		self.ok_btn=QPushButton("OK")
		self.cancel_btn=QPushButton("Cancel")

		## ������Ʈ ����
		self.div.addWidget(self.label)
		self.div.addWidget(self.text)
		self.div.addWidget(self.error_text)
		# ��ư
		self.div.addLayout(QHBoxLayout())
		self.div.itemAt(3).addWidget(self.ok_btn)
		self.div.itemAt(3).addWidget(self.cancel_btn)
		
		## �̺�Ʈ ����
		# ��ư Ŭ�� �̺�Ʈ
		self.ok_btn.clicked.connect(self.onClickOK)
		self.cancel_btn.clicked.connect(self.onClickCancel)
		# �ؽ�Ʈ ����
		self.text.textChanged.connect(lambda: self.checkInvaildText(checker, params))
		print(params)

		## ��Ÿ ����
		self.error_text.setStyleSheet("color:#c33")  # ���� �ؽ�Ʈ �� ����
		self.setLayout(self.div)
		self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

		self.exec()

		return


	### �̺�Ʈ
	## ��ư �̺�Ʈ
	# Ȯ�� ��ư Ŭ��
	def onClickOK(self) -> tuple:
		self.close()
		self.return_data=(self.text.text(), True)

		return 
	# ��� ��ư Ŭ��
	def onClickCancel(self) -> tuple:
		self.close()
		self.return_data=("", False)

		return
	## �ؽ�Ʈ ���� �̺�Ʈ
	# �ؽ�Ʈ ���� �� ��ȿ�� �˻�
	def checkInvaildText(self, checker, params):
		if checker(self.text.text(), params[0], params[1]):
			self.error_text.setText("Invalid name")  #todo# �������� ���� ����
			self.ok_btn.setDisabled(True)  # ��ư ��Ȱ��ȭ
		else:
			self.error_text.setText("")
			self.ok_btn.setDisabled(False)

		return