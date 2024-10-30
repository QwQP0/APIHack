from enum import Enum
import json
import os


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
		content["requests"][CONST.DEFAULT_NAME.REQUEST]=["", "", "", ""]  # 기본 요청 : [타겟, 헤더, 페이로드, 드롭다운 번호]
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
	def setNameAuto(basename:str, project_name:str, content_type:str) -> str:
		if basename=="":
			if content_type=='p':  # 프로젝트
				return File.setNameAuto(CONST.DEFAULT_NAME.PROJECT, project_name, content_type)
			elif content_type=='q':  # 요청
				return File.setNameAuto(CONST.DEFAULT_NAME.REQUEST, project_name, content_type)
			elif content_type=='s':  # 저장 파일
				return File.setNameAuto(CONST.DEFAULT_NAME.SAVED, project_name, content_type)
			elif content_type=='v':  # 변수
				return File.setNameAuto(CONST.DEFAULT_NAME.VAR, project_name, content_type)
			
		is_copied_name=False
		last_num=-1

		# 이름 검사
		s=basename.find('(')
		if s!=-1:
			e=basename.find(')', s)

			if e!=-1:  # 괄호로 둘러싼 부분
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

		if content_type=='p':  # 프로젝트
			if not is_copied_name:
				# 프로젝트 이름이 이미 존재하는지 검사
				if project_name=="": 
					if os.path.exists(Global.projects_data[basename]["last_path"]+'/'+basename):  # 파일이 존재하는지 검사
						last_num=0
					else:
						return basename
				else:  # 새 프로젝트 생성 시 입력한 경로(혹은 마지막 경로) 검사를 위해 경로가 [project_name]으로 들어옴
					if os.path.exists(project_name+'/'+basename):  # 파일이 존재하는지 검사
						last_num=0
					else:
						return basename

			while True:  # 다음 번호 붙이기
				last_num+=1
				
				if project_name=="": 
					if not os.path.exists(Global.projects_data[basename]["last_path"]+'/'+basename+f' ({last_num})'):  # 폴더가 존재하는지 검사
						return basename+f' ({last_num})'  # 없으면 [basename] (n) 반환
				else:  # 새 프로젝트 생성 시 입력한 경로(혹은 마지막 경로) 검사를 위해 경로가 [project_name]으로 들어옴
					if not os.path.exists(project_name+'/'+basename+f' ({last_num})'):  # 폴더가 존재하는지 검사
						return basename+f' ({last_num})'  # 없으면 [basename] (n) 반환

		elif content_type=='q':  # 요청
			if not is_copied_name:
				if basename in Global.projects_data[project_name]["requests"].keys():  # 해당 이름의 요청이 아직 없음
					last_num=0
				else:
					return basename

			while True:  # 다음 번호 붙이기
				last_num+=1

				if not basename+f" ({last_num})" in Global.projects_data[project_name]["requests"].keys():  # 요청이 존재하는 지 검사
					return basename+f' ({last_num})'

		elif content_type=='s':  # 저장된 응답
			if not is_copied_name:
				if os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+basename+".rsv"):  # 해당 이름의 요청이 아직 없음
					last_num=0
				else:
					return basename

			while True:  # 다음 번호 붙이기
				last_num+=1

				if not os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+basename+f' ({last_num}).rsv'):  # 파일이 존재하는지 검사
					return basename+f' ({last_num})'
		elif content_type=='v':  # 변수
			if not is_copied_name:
				if basename in Global.projects_data[project_name]["variables"].keys():  # 해당 이름의 변수가 아직 없음
					last_num=0
				else:
					return basename

			while True:  # 다음 번호 붙이기
				last_num+=1

				if not basename+f" ({last_num})" in Global.projects_data[project_name]["variables"].keys():  # 변수가 존재하는 지 검사
					return basename+f' ({last_num})'


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



	class DECODER_MODE(Enum):
		DECODE=1
		ENCODE=2
		


	class DECODER_TYPE(Enum):
		BASE_64=1
		SHA=2

	DECODER_DEFAULT_FUNCTION=(DECODER_MODE.DECODE.name, DECODER_TYPE.BASE_64.name)