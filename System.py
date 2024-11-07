from enum import Enum
import json
import os

class File:
    # 프로젝트 생성
    def createProject(project_path:str, project_name:str, target_url:str):
        if not os.path.exists(project_path+'/'+project_name):
            os.makedirs(project_path+'/'+project_name, mode=711)  # 프로젝트 폴더 생성
        else: 
            print("Project name already exists")
            return False

        # 프로젝트 파일 구성
        project=open(project_path+'/'+project_name+'/'+project_name+".ahp", 'w')  # 프로젝트 파일 생성
        content={}
        content["last_path"]=project_path
        content["requests"]={}  # 요청 저장
        content["requests"][CONST.DEFAULT_NAME.REQUEST]=["{{$base_url}}", 0, "", ""]  # 기본 요청 : [타겟, 드롭다운 번호, 헤더, 페이로드]
        content["variables"]={}  # 변수 저장
        content["variables"]["base_url"]=["String", "", target_url]  # 기본 url 변수
        content["decoder"]={}
        content["decoder"]["lastest_text"]=""  # 마지막으로 입력된 텍스트
        content["decoder"]["lastest_text_num"]=0  # 마지막으로 입력된 텍스트의 번호
        content["decoder"]["seq_functions"]=[]  # 디코더에서의 기능
        content["comparer"]={}
        content["comparer"]["last_text_name_1"]=""  # 마지막으로 열었던 파일 1
        content["comparer"]["last_text_name_2"]=""  # 마지막으로 열었던 파일 2
        project.write(json.dumps(content))  # 암호화(아직 안함) 후 파일 작성
        project.close()  # 파일 닫기

        # 저장 폴더
        os.makedirs(project_path+'/'+project_name+'/saved', mode=711)

        # 로그 파일 생성
        open(project_path+'/'+project_name+'/'+"log.txt", 'w').close()

        File.openProject(project_path, project_name)

        return True

    # 이미 존재하는 프로젝트 열기
    def openProject(path:str, project_name:str) -> str:
        if project_name in Global.projects_data:
            print("Project is already opened")
            return True  # 프로젝트가 이미 열려있다는 뜻

        project=open(path+'/'+project_name+'/'+project_name+".ahp")
        content_json=json.loads(project.read())  # 복호화(아직 안함) 후 json 변환
        project.close()
        
        Global.projects_data[project_name]=content_json

    def saveProject(project_name:str):
        print("System.File.saveProject : Project Name-"+project_name)
        project=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+project_name+".ahp", 'w')
        project.write(json.dumps(Global.projects_data[project_name]))  # 암호화(아직 안함) 후 파일 작성
        project.close()

    def appendLog(project_name:str, text:str):
        log=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+"log.txt", 'a')
        log.write("LOG: "+text+"\n")
        print("LOG: "+text)
        log.close()

    # 복제, 저장 시 자동으로 이름 설정
    def setNameAuto(basename:str, project_name:str, content_type) -> str:
        if basename=="":
            if content_type=='p':  # 프로젝트
                return File.setNameAuto(CONST.DEFAULT_NAME.PROJECT, project_name, content_type)
            elif content_type=='q':  # 요청
                return File.setNameAuto(CONST.DEFAULT_NAME.REQUEST, project_name, content_type)
            elif content_type=='s':  # 저장된 응답
                return File.setNameAuto(CONST.DEFAULT_NAME.SAVED, project_name, content_type)
            
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
                    print("fail")
            else:
                print("fail")
        else:
            print("fail")

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
                print(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+basename+".rsv")
                if os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+basename+".rsv"):  # 해당 이름의 요청이 아직 없음
                    last_num=0
                else:
                    return basename

            while True:  # 다음 번호 붙이기
                last_num+=1

                if not os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+basename+f' ({last_num}).rsv'):  # 파일이 존재하는지 검사
                    return basename+f' ({last_num})'

class Global:
    default_project_path="default_project_path"  # 기본 파일 경로

    projects_data={}  # 프로젝트 데이터

    # 클래스 변수
    main=None
    req=None
    var=None
    res=None

    responses=[]  # 요청 후 응답받은 내용
    
class CONST:
    class DEFAULT_NAME:
        PROJECT="My project"
        REQUEST="New Request"
        SAVED="Response"

    class REQUEST_TYPE(Enum):
        GET=1
        POST=2
        PUT=3
        DELETE=999

    class DECODER_MODE(Enum):
        ENCODE=1
        DECODE=2
        
    class DECODER_CRYPT(Enum):
        BASE_64=1
        SHA=2

    DECODER_DEFAULT_FUNCTION=[DECODER_MODE.ENCODE, DECODER_CRYPT.BASE_64]