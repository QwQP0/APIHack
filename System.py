from enum import Enum
import json
import os

class File:
    # ������Ʈ ����
    def createProject(project_path:str, project_name:str, target_url:str):
        if not os.path.exists(project_path+'/'+project_name):
            os.makedirs(project_path+'/'+project_name, mode=711)  # ������Ʈ ���� ����
        else: 
            print("Project name already exists")
            return False

        # ������Ʈ ���� ����
        project=open(project_path+'/'+project_name+'/'+project_name+".ahp", 'w')  # ������Ʈ ���� ����
        content={}
        content["last_path"]=project_path
        content["requests"]={}  # ��û ����
        content["requests"][CONST.DEFAULT_NAME.REQUEST]=["{{$base_url}}", 0, "", ""]  # �⺻ ��û : [Ÿ��, ��Ӵٿ� ��ȣ, ���, ���̷ε�]
        content["variables"]={}  # ���� ����
        content["variables"]["base_url"]=["String", "", target_url]  # �⺻ url ����
        content["decoder"]={}
        content["decoder"]["lastest_text"]=""  # ���������� �Էµ� �ؽ�Ʈ
        content["decoder"]["lastest_text_num"]=0  # ���������� �Էµ� �ؽ�Ʈ�� ��ȣ
        content["decoder"]["seq_functions"]=[]  # ���ڴ������� ���
        content["comparer"]={}
        content["comparer"]["last_text_name_1"]=""  # ���������� ������ ���� 1
        content["comparer"]["last_text_name_2"]=""  # ���������� ������ ���� 2
        project.write(json.dumps(content))  # ��ȣȭ(���� ����) �� ���� �ۼ�
        project.close()  # ���� �ݱ�

        # ���� ����
        os.makedirs(project_path+'/'+project_name+'/saved', mode=711)

        # �α� ���� ����
        open(project_path+'/'+project_name+'/'+"log.txt", 'w').close()

        File.openProject(project_path, project_name)

        return True

    # �̹� �����ϴ� ������Ʈ ����
    def openProject(path:str, project_name:str) -> str:
        if project_name in Global.projects_data:
            print("Project is already opened")
            return True  # ������Ʈ�� �̹� �����ִٴ� ��

        project=open(path+'/'+project_name+'/'+project_name+".ahp")
        content_json=json.loads(project.read())  # ��ȣȭ(���� ����) �� json ��ȯ
        project.close()
        
        Global.projects_data[project_name]=content_json

    def saveProject(project_name:str):
        print("System.File.saveProject : Project Name-"+project_name)
        project=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+project_name+".ahp", 'w')
        project.write(json.dumps(Global.projects_data[project_name]))  # ��ȣȭ(���� ����) �� ���� �ۼ�
        project.close()

    def appendLog(project_name:str, text:str):
        log=open(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/'+"log.txt", 'a')
        log.write("LOG: "+text+"\n")
        print("LOG: "+text)
        log.close()

    # ����, ���� �� �ڵ����� �̸� ����
    def setNameAuto(basename:str, project_name:str, content_type) -> str:
        if basename=="":
            if content_type=='p':  # ������Ʈ
                return File.setNameAuto(CONST.DEFAULT_NAME.PROJECT, project_name, content_type)
            elif content_type=='q':  # ��û
                return File.setNameAuto(CONST.DEFAULT_NAME.REQUEST, project_name, content_type)
            elif content_type=='s':  # ����� ����
                return File.setNameAuto(CONST.DEFAULT_NAME.SAVED, project_name, content_type)
            
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
                    print("fail")
            else:
                print("fail")
        else:
            print("fail")

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
                print(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+basename+".rsv")
                if os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+basename+".rsv"):  # �ش� �̸��� ��û�� ���� ����
                    last_num=0
                else:
                    return basename

            while True:  # ���� ��ȣ ���̱�
                last_num+=1

                if not os.path.exists(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+basename+f' ({last_num}).rsv'):  # ������ �����ϴ��� �˻�
                    return basename+f' ({last_num})'

class Global:
    default_project_path="default_project_path"  # �⺻ ���� ���

    projects_data={}  # ������Ʈ ������

    # Ŭ���� ����
    main=None
    req=None
    var=None
    res=None

    responses=[]  # ��û �� ������� ����
    
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