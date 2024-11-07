#################### Imports ####################

from collections import deque
from PySide6.QtWidgets import QBoxLayout, QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from System import Global



###################### Main #####################

class Variables():
    def __init__(self, parent):
        self.variables_tab_content=QVBoxLayout(parent)
        self.initUI()


    def initUI(self):
        ## 변수 테이블 라벨
        self.var_table_label=QHBoxLayout()
        self.var_table_label.addWidget(QLabel("*"))
        self.var_table_label.addWidget(QLabel("Name"))
        self.var_table_label.addWidget(QLabel("Type"))
        self.var_table_label.addWidget(QLabel("Range"))
        self.var_table_label.addWidget(QLabel("Fix"))
        self.variables_tab_content.addLayout(self.var_table_label)

        ## + 버튼 추가
        self.var_add_row_btn=QPushButton("+")
        self.var_add_row_btn.clicked.connect(lambda :self.addRow())
        self.variables_tab_content.addWidget(self.var_add_row_btn)

    # 한 줄 추가
    def addRow(self, saved_var=["", "", "", ""]):
        row=QHBoxLayout()
        row.addWidget(QCheckBox())
            
        for i in range(4):
            row.addWidget(QLineEdit(saved_var[i]))
        
        print("add Var")

        self.variables_tab_content.insertLayout(len(self.variables_tab_content.children()), row)


    # 현재 프로젝트의 변수 적용
    def initVariables(self, project_name):
        children=self.variables_tab_content.children()
        delete_obj=[]

        print(children)
      
        ## 기존 변수 줄 삭제
        for i in range(1, len(children)):
            delete_obj.append(children[i])
            for j in range(5):  # 하위의 체크박스, 입력창 삭제
                delete_obj.append(children[i].itemAt(j).widget())
            
        for i in range(len(delete_obj)):  # 오브젝트 삭제
            delete_obj[i].deleteLater()
            delete_obj[i].setParent(None)
            
        saved_vars=list(Global.projects_data[project_name]["variables"].keys())
        
        ## 저장된 변수 추가
        for i in range(len(saved_vars)):
            self.addRow([saved_vars[i]]+Global.projects_data[project_name]["variables"][saved_vars[i]])

    # 변수 탭 현재 변수 정보 반환
    def getTabInfo(self):
        var_list=list(self.variables_tab_content.findChildren(QHBoxLayout))
        Global.projects_data[Global.main.last_highlighted_project]["variables"]={}  # 현재 변수 값 초기화

        for i in range(1, len(var_list)):
            var_name=var_list[i].itemAt(1).widget().text()
            var_type=var_list[i].itemAt(2).widget().text()
            var_range=var_list[i].itemAt(3).widget().text()
            var_fix=var_list[i].itemAt(4).widget().text()

            Global.projects_data[Global.main.last_highlighted_project]["variables"][var_name]=[var_type, var_range, var_fix]  # 변수 입력


    # 변수 인식 후 순회
    # 링크, 헤더, 페이로드에 포함된 변수(사용중인 변수) 파악
    def getPlainText(link:str, header:str, payloads:str):
        var_names=[]
        
        ## 링크
        link_vars, link_non_vars=Variables.separateVar(link)  
        var_names.extend(link_vars)
        ## 헤더
        header_vars, header_non_vars=Variables.separateVar(header)  
        var_names.extend(header_vars)
        ## 페이로드
        payloads_vars, payloads_non_vars=Variables.separateVar(payloads)  
        var_names.extend(payloads_vars)

        var_order=Variables.setVarOrder(var_names)  # 변수 순회 순서 결정

        iterator=Variables.stackVars(var_order)  # 순회자
        for var_value in iterator:  # 순회
            var_values={}

            for i in range(len(var_value)):
                var_values[var_order[i]]=var_value[i]

            new_link=Variables.rebuildText(link_vars, link_non_vars, var_values)
            new_header=Variables.rebuildText(header_vars, header_non_vars, var_values)
            new_payloads=Variables.rebuildText(payloads_vars, payloads_non_vars, var_values)
            yield new_link, new_header, new_payloads

    # 텍스트 내 변수 이름 인식
    def separateVar(text:str):
        var_names=[]  # 변수
        var_name=""  # 변수 이름 저장용
        non_var=[]  # 
        non_var_s=0  #

        ## 링크
        i=0
        while i<len(text):
            if text[i]=='{':
                if i+3<len(text) and text[i:i+3]=="{{$":  # 변수 이름 시작
                    i+=3
                    var_name=text[i]
            elif text[i]=='}':
                if i+1<len(text) and text[i+1]=='}':  # 변수 이름 끝
                    if var_name!="":
                        non_var.append(text[non_var_s:(i+1)-5-len(var_name)+1])  # (변수 이름이 끝나는 인덱스)-(괄호, $ 제외)-(변수 이름 길이 제외)+(보정)
                        # -> 변수가 아닌 부분 저장
                        var_names.append(var_name)  # 변수 이름 전달
                        var_name=""  # 초기화
                        non_var_s=(i+1)+1  # 변수 이름 } 끝부분 + 다음 인덱스
                        # -> 다음 시작점 저장
            else:
                if var_name!="":  # 변수 이름 입력중
                    var_name+=text[i]

            i+=1

        if non_var_s!=len(text):
            non_var.append(text[non_var_s:])

        return var_names, non_var

    # 변수 순회 순서 결정(link 에 따라)
    def setVarOrder(var_names:list):
        var_names=deque(var_names)
        defined_var=set()
        var_order=[]

        while len(var_names):
            var_name=var_names.popleft()
            links=Variables.getLinks(var_name)

            if len(links)==0:  # 링크 없음
                var_order.append(var_name)  # 순서에 삽입
                defined_var.add(var_name)
            else:
                isbreaked=False
                for i in range(len(links)):
                    if not links[i] in defined_var:  # 링크된 변수가 아직 설정되지 않음
                        isbreaked=True
                        break

                if isbreaked:
                    var_names.append(var_name)
                else:
                    var_order.append(var_name)  # 순서에 삽입
                    defined_var.add(var_name)

        return var_order

    # 다른 변수와 연계되어 있는지 검사
    def getLinks(var_name:str):
        var_values=Global.projects_data[Global.main.last_highlighted_project]["variables"][var_name]  # 변수 정보 불러옴/  이름 : 타입/값/고정값

        if var_values[2]=="":  # 고정값 없음
            links, tmp=Variables.separateVar(var_values[1])  # 변수 값에 다른 변수가 연계되어 있는지 검사
        else:  # 고정값 있음
            links, tmp=Variables.separateVar(var_values[2])  # 변수 고정값에 다른 변수가 연계되어 있는지 검사

        return links

    # 변수와 텍스트 재조립
    def rebuildText(var_names:list, non_vars:list, var_value:dict):
        res=""

        for i in range(len(var_names)):
            res+=non_vars[i]
            res+=str(var_value[var_names[i]])

        if len(non_vars)>len(var_names):
            res+=non_vars[-1]

        return res


    # 전체 변수 순회
    def stackVars(var_order):
        var_value_stack=[]
        var_iterator_stack=[]

        while True:
            if len(var_value_stack)!=len(var_iterator_stack):  # 순회자만 넣고 변수는 아직 안넣음
                try:
                    var_value_stack.append(next(var_iterator_stack[-1]))  # 다음 변수 기입
                except:  # 다음 변수 없음! -> 변수 순회 종료
                    try:
                        var_value_stack.pop()  # 이 변수 스택을 통한 경로 없음
                        var_iterator_stack.pop()  # 순회가 끝난 스택
                    except:
                        return
            else:  # 다음 순회자 넣을 차례
                if len(var_value_stack)!=len(var_order):  # 세트 미완성
                    var_name=var_order[len(var_value_stack)]  # 현재 순회할 변수의 정보 불러옴
                    var_iterator_stack.append(Variables.traverseVar(var_name))  # 변수 순회자 추가
                
                    var_value_stack.append(next(var_iterator_stack[-1]))  # 첫 변수 등록

                else:  # 세트 완성
                    yield var_value_stack  # 세트 반환

                    try:
                        var_value_stack.pop()  # 백트랙
                    except:
                        return

    # 단일 변수 순회
    def traverseVar(var_name):
        var_info=Global.projects_data[Global.main.last_highlighted_project]["variables"][var_name]
         
        #todo# 링크 시 가공하기
        if var_info[2]!="":  # 고정값 있음
            yield var_info[2]
        else:  # 고정값 없음
            ### 변수 타입
            if var_info[0]=="Number":  ## 실수
                yield "error"
            elif var_info[0]=="List":  ## 리스트
                for ret in var_info[1].split(','):    
                    yield ret
            elif var_info[0]=="String":  ## 문자열
                yield "error"
            elif var_info[0]=="Hex":  ## 16진수
                yield "error"


