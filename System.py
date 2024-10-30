from enum import Enum
import json
import os


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
		content["requests"][CONST.DEFAULT_NAME.REQUEST]=["", "", "", ""]  # �⺻ ��û : [Ÿ��, ���, ���̷ε�, ��Ӵٿ� ��ȣ]
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
	def setNameAuto(basename:str, project_name:str, content_type:str) -> str:
		if basename=="":
			if content_type=='p':  # ������Ʈ
				return File.setNameAuto(CONST.DEFAULT_NAME.PROJECT, project_name, content_type)
			elif content_type=='q':  # ��û
				return File.setNameAuto(CONST.DEFAULT_NAME.REQUEST, project_name, content_type)
			elif content_type=='s':  # ���� ����
				return File.setNameAuto(CONST.DEFAULT_NAME.SAVED, project_name, content_type)
			elif content_type=='v':  # ����
				return File.setNameAuto(CONST.DEFAULT_NAME.VAR, project_name, content_type)
			
		is_copied_name=False
		last_num=-1

		# �̸� �˻�
		s=basename.find('(')
		if s!=-1:
			e=basename.find(')', s)

			if e!=-1:  # ��ȣ�� �ѷ��� �κ�
				try:
					last_num=int(basename[s+1:e])
					basename=basename[:s]
					
					if basename[-1]==' ':
						basename=basename[:s-1]

					is_copied_name=True
				except:
					print("System.File.setNameAuto : not copied name")
			else:
				print("System.File.setNameAuto : not copied name")
		else:
			print("System.File.setNameAuto : not copied name")

		if content_type=='p':  # ������Ʈ
			if not is_copied_name:
				# ������Ʈ �̸��� �̹� �����ϴ��� �˻�
				if project_name=="": 
					if os.path.exists(Global.projects_data[basename]["last_path"]+'/'+basename):  # ������ �����ϴ��� �˻�
						last_num=0
					else:
						return basename
				else:  # �� ������Ʈ ���� �� �Է��� ���(Ȥ�� ������ ���) �˻縦 ���� ��ΰ� [project_name]���� ����
					if os.path.exists(project_name+'/'+basename):  # ������ �����ϴ��� �˻�
						last_num=0
					else:
						return basename

			while True:  # ���� ��ȣ ���̱�
				last_num+=1
				
				if project_name=="": 
					if not os.path.exists(Global.projects_data[basename]["last_path"]+'/'+basename+f' ({last_num})'):  # ������ �����ϴ��� �˻�
						return basename+f' ({last_num})'  # ������ [basename] (n) ��ȯ
				else:  # �� ������Ʈ ���� �� �Է��� ���(Ȥ�� ������ ���) �˻縦 ���� ��ΰ� [project_name]���� ����
					if not os.path.exists(project_name+'/'+basename+f' ({last_num})'):  # ������ �����ϴ��� �˻�
						return basename+f' ({last_num})'  # ������ [basename] (n) ��ȯ

		elif content_type=='q':  # ��û
			if not is_copied_name:
				if basename in Global.projects_data[project_name]["requests"].keys():  # �ش� �̸��� ��û�� ���� ����
					last_num=0
				else:
					return basename

			while True:  # ���� ��ȣ ���̱�
				last_num+=1

				if not basename+f" ({last_num})" in Global.projects_data[project_name]["requests"].keys():  # ��û�� �����ϴ� �� �˻�
					return basename+f' ({last_num})'

		elif content_type=='s':  # ����� ����
			if not is_copied_name:
				if os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+basename+".rsv"):  # �ش� �̸��� ��û�� ���� ����
					last_num=0
				else:
					return basename

			while True:  # ���� ��ȣ ���̱�
				last_num+=1

				if not os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+basename+f' ({last_num}).rsv'):  # ������ �����ϴ��� �˻�
					return basename+f' ({last_num})'
		elif content_type=='v':  # ����
			if not is_copied_name:
				if basename in Global.projects_data[project_name]["variables"].keys():  # �ش� �̸��� ������ ���� ����
					last_num=0
				else:
					return basename

			while True:  # ���� ��ȣ ���̱�
				last_num+=1

				if not basename+f" ({last_num})" in Global.projects_data[project_name]["variables"].keys():  # ������ �����ϴ� �� �˻�
					return basename+f' ({last_num})'


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



	class DECODER_MODE(Enum):
		DECODE=1
		ENCODE=2
		


	class DECODER_TYPE(Enum):
		BASE_64=1
		SHA=2

	DECODER_DEFAULT_FUNCTION=(DECODER_MODE.DECODE.name, DECODER_TYPE.BASE_64.name)