#################### Imports ####################

import json
import os
import shutil
import sys

from PySide6.QtCore import QEvent, QObject, QPoint, Signal
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QInputDialog, QMainWindow, QMenu, QMessageBox, QStyle, QTabWidget, QVBoxLayout
from PySide6.QtWidgets import QDialog, QFileDialog
from PySide6.QtWidgets import QMenuBar, QPushButton, QWidget, QLabel, QLineEdit
from PySide6.QtWidgets import QBoxLayout
from PySide6.QtGui import QAction, QKeySequence, Qt
from shiboken6 import delete

from Decoder import Decoder
from Request import Request
from Response import Response
from System import File, Global
from Variables import Variables



###################### Main #####################

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_tab_reinited=False
        self.last_left_clicked_object=None
        self.last_right_clicked_object=None
        self.last_highlighted_project=""  # 마지막으로 하이라이트된 프로젝트 이름
        self.last_highlighted_request=""  # 마지막으로 하이라이트된 요청 이름
        # -> 현재 프로젝트 파악에 사용

        self.left_div_widget=None

        Global.main=self

        self.initUI()
    

    # UI 초기 설정
    def initUI(self):
        self.initMenu()
        self.initTab()
        
        self.setCentralWidget(self.main_tabs)  # 프로젝트 열기 전 탭만 표시(사이드뷰 미표시)
        
        # 창 생성
        self.setWindowTitle('APIHACK')
        self.setGeometry(960, 540, 480, 270) # 크기, 위치 설정
        self.show()


    # 메뉴 바 구축
    def initMenu(self):
        # 메뉴 바 생성
        self.menubar=QMenuBar()
        self.setMenuBar(self.menubar)
        self.menu_list={}
        
        ## 파일 메뉴 생성
        self.menu_list["File"]=self.menubar.addMenu("File")
        # 파일 생성 옵션 생성
        self.menu_list["File"].addAction("New..", QKeySequence(Qt.CTRL | Qt.Key_N))
        self.menu_list["File"].children()[1].triggered.connect(self.createProject)  # 함수 연결
        # 파일 불러오기 옵션 생성
        self.menu_list["File"].addAction("Open..", QKeySequence(Qt.CTRL | Qt.Key_O))
        self.menu_list["File"].children()[2].triggered.connect(self.openProject)  # 함수 연결
        # 구분선
        self.menu_list["File"].addAction("").setSeparator(True)
        # 파일 저장 옵션 생성
        self.menu_list["File"].addAction("Save", QKeySequence(Qt.CTRL | Qt.Key_S))
        self.menu_list["File"].children()[4].triggered.connect(self.saveCurProject)  # 함수 연결

    # 탭 구축
    def initTab(self):
        # 탭 생성
        self.main_tabs=QTabWidget()

        ## 홈 탭
        self.home_tab=QWidget()
        self.main_tabs.addTab(self.home_tab, "HOME")
        self.home_tab_content=QBoxLayout(QBoxLayout.TopToBottom, self.home_tab)
        # 텍스트 표시
        self.home_tab_content.addWidget(QLabel("Start Hack With ***"))
        self.home_tab_content.addWidget(QLabel("Start new project or open existing projects"))
        # 버튼 생성
        self.crt_pj_btn=QPushButton("new project")
        self.open_pj_btn=QPushButton("open project")
        self.crt_pj_btn.clicked.connect(self.createProject)
        self.open_pj_btn.clicked.connect(self.openProject)
        self.btn_div=QBoxLayout(QBoxLayout.LeftToRight)
        self.btn_div.addWidget(self.crt_pj_btn)
        self.btn_div.addWidget(self.open_pj_btn)
        self.home_tab_content.addLayout(self.btn_div)  # 탭 내용에 추가

        ## 디코더 탭
        self.decoder_tab=QWidget()
        self.main_tabs.addTab(self.decoder_tab, "Decoder")
        Decoder(self.decoder_tab)

    # 프로젝트 생성, 불러오기 후 탭 재구성
    def reInitTab(self, project_name):
        if not self.is_tab_reinited:  # 아직 재구성 안함
            self.main_tabs.removeTab(0)  # 홈 탭 삭제

            ## 요청 탭
            self.request_tab=QWidget()
            self.main_tabs.insertTab(0, self.request_tab, "Request")
            Global.req=Request(self.request_tab)

            ## 변수 탭
            self.variables_tab=QWidget()
            self.main_tabs.insertTab(1, self.variables_tab, "Variables")
            Global.var=Variables(self.variables_tab)

            ## 응답 탭
            self.response_tab=QWidget()
            self.main_tabs.insertTab(2, self.response_tab, "Response")
            self.response_tab.setObjectName("response_tab")
            Global.res=Response(self.response_tab)
        
        else:  # 재구성 함(현재 띄워진 프로젝트가 있음)
            self.saveCurProject()  # 프로젝트 전환 전 현재 프로젝트 저장

        self.main_tabs.setCurrentIndex(1)  # 요청 탭으로 탭 설정
        self.is_tab_reinited=True

        tmp_request=list(Global.projects_data[project_name]["requests"].keys())[0]
        self.last_highlighted_project=project_name
        self.last_highlighted_request=tmp_request
        Global.req.initRequest(project_name, tmp_request) # 요청 탭 구성
        Global.var.initVariables(project_name) # 변수 탭 구성
        

    # 프로젝트 생성/불러오기 시 사이드뷰 생성/업데이트 + 프로젝트 접기/*열기* 기능 시 사용 
    def initLeft(self, project_name, insert_pos=-1):
        if self.left_div_widget==None:  # 아직 사이드 뷰가 없을 때
            self.left_div_widget=QWidget()
            self.left_div=QVBoxLayout(self.left_div_widget)
            self.left_div_widget.setObjectName("left")

            self.rightClickListener(self.left_div_widget).connect(self.viewContextMenu)

            # 사이드 뷰 적용
            self.body_div=QWidget()
            self.body=QHBoxLayout(self.body_div)
            self.body.addWidget(self.left_div_widget)
            self.body.addWidget(self.main_tabs)
            self.setCentralWidget(self.body_div)
            
        ## 요소 구성
        # 프로젝트
        if insert_pos==-1:  # 이미 프로젝트가 열려 있음
            new_project=QLabel(project_name)  # 접힘 표시 아이콘 넣기
            new_project.setObjectName("open")
            self.left_div.addWidget(new_project)
            self.leftClickListener(new_project).connect(lambda :self.viewSubItems(new_project))  # 프로젝트 좌클릭 시 하위 요소 표시
            self.rightClickListener(new_project).connect(self.viewContextMenu)  # 프로젝트 우클릭 시 우클릭 메뉴 표시
            
            self.focusLabel(new_project)

        # 요청
        for request_name in Global.projects_data[project_name]["requests"].keys():
            new_request=(QLabel(request_name))
            new_request.setObjectName(project_name)

            if insert_pos==-1:
                self.left_div.addWidget(new_request)
            else:
                self.left_div.insertWidget(insert_pos, new_request)
                insert_pos+=1

            self.leftClickListener(new_request).connect(self.viewRequest)  # 요청 좌클릭 시 내용 표시
            self.rightClickListener(new_request).connect(self.viewContextMenu)  # 요청 우클릭 시 우클릭 메뉴 표시

        # 저장된 응답 폴더
        new_saves=QLabel("saved")
        new_saves.setObjectName(project_name+"/open")

        if insert_pos==-1:
            self.left_div.addWidget(new_saves)
        else:
            self.left_div.insertWidget(insert_pos, new_saves)
            insert_pos+=1
        
        self.leftClickListener(new_saves).connect(lambda :self.viewSubItems(new_saves))  # 좌클릭 시
        self.rightClickListener(new_saves).connect(self.viewContextMenu)  # 우클릭 시 우클릭 메뉴 표시

        # 저장된 응답
        save_file_names=[]
        for save_files in os.walk(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved"):  # 세이브 폴더 하위 파일 순회
            save_file_names.extend(save_files[2])  # 이름 저장

        for i in range(len(save_file_names)):
            save_file_name=save_file_names[i].split('.')
            extension=save_file_name[-1]  # 확장자
            save_file_name='.'.join(save_file_name[:len(save_file_name)-1])  # 파일 이름 조립(확장자 제외)

            print(save_file_name, extension)

            if extension=="rsv":
                new_save=QLabel(save_file_name)
                new_save.setObjectName(project_name+"/saved")
                
                if insert_pos==-1:
                    self.left_div.addWidget(new_save)
                else:
                    self.left_div.insertWidget(insert_pos, new_save)
                    insert_pos+=1

                self.leftClickListener(new_save).connect(self.viewContent)  # 저장된 응답 좌클릭 시 내용 표시
                self.rightClickListener(new_save).connect(self.viewContextMenu)  # 저장된 응답 우클릭 시 우클릭 메뉴 표시


    # 사이드의 요소 클릭 시 하이라이트 표시
    # 프로젝트, 요청 QLabel에 적용
    def focusLabel(self, obj:QLabel):
        ### 기존 하이라이트 제거
        if not (self.last_highlighted_project=="" and self.last_highlighted_request==""):  # 기존 하이라이트 되어있는 오브젝트 없지 않음
            ## 하이라이트된 오브젝트 탐색
            project_labels=list(obj.parent().findChildren(QLabel, "open"))  # 열려있는 프로젝트 탐색
            project_labels.extend(list(obj.parent().findChildren(QLabel, "close")))  # 닫혀있는 프로젝트 탐색

            for project_label in project_labels:  # 프로젝트 탐색
                if project_label.text()==self.last_highlighted_project:  # 하이라이트된 프로젝트 찾음
                    project_label.setStyleSheet("")  # 하이라이트 제거
                    break

            self.last_highlighted_project=""

            if self.last_highlighted_request!="":  # 최근 하이라이트 된 오브젝트가 "요청"임
                request_labels=list(obj.parent().findChildren(QLabel, self.last_highlighted_project))  # 프로젝트의 하위 요청 탐색

                for request_label in request_labels:  # 프로젝트 탐색
                    if request_label.text()==self.last_highlighted_request:  # 하이라이트된 요청 찾음
                        request_label.setStyleSheet("")  # 하이라이트 제거
                        break

        ### 하이라이트 추가
        if not (obj.objectName()=="open" or obj.objectName()=="close"):  # 요청 선택시
            project_labels=list(obj.parent().findChildren(QLabel, "open"))  # 열려있는 프로젝트 탐색
            project_labels.extend(list(obj.parent().findChildren(QLabel, "close")))  # 닫혀있는 프로젝트 탐색
        
            for project_label in project_labels:  # 현재 하이라이트 된 요청의 프로젝트 탐색
                if project_label.text()==obj.objectName():
                    project_label.setStyleSheet("background-color:gray;")  # 프로젝트 하이라이트
                    break
            
            self.last_highlighted_request=obj.text()  # 현재 하이라이트된 요청 이름 저장
            self.last_highlighted_project=obj.objectName()  # 현재 하이라이트된 프로젝트 이름 저장
        else:  # 프로젝트 선택시
            self.last_highlighted_project=obj.text()  # 현재 하이라이트된 프로젝트 이름 저장

        obj.setStyleSheet("background-color:gray;")  # 하이라이트

    # 좌클릭 시 하위 아이템 보이기/숨기기
    # 프로젝트, 저장 폴더에 적용
    def viewSubItems(self, obj:QLabel):
        if obj.objectName()=="open":  # 프로젝트 열려있을 때; 접기
            if obj.text()!=self.last_highlighted_project:  # 하이라이트가 없음
                # -> not (프로젝트가 최근 선택 or 프로젝트의 하위 요청이 최근 선택됨)
                self.focusLabel(obj)  # 오브젝트 하이라이트
                return  # 종료

            items=obj.parent().children()
            delete_obj=[]

            for i in range(len(items)):  # 삭제할 요소 탐색
                if items[i].objectName().split('/')[0]==obj.text():
                    delete_obj.append(items[i])  # 삭제할 요소 임시 저장
                    print(items[i])

            for i in range(len(delete_obj)):  # 삭제
                delete_obj[i].deleteLater()
                delete_obj[i].setParent(None)
            
            obj.setObjectName("close")  # 프로젝트 접음

        elif obj.objectName()=="close":  # 프로젝트 접혀있을 때; 열기
            self.initLeft(obj.text(), insert_pos=self.left_div.indexOf(obj)+1)

            obj.setObjectName("open")  # 프로젝트 염

            if obj.text()!=self.last_highlighted_project:  # 하이라이트가 없음
                self.focusLabel(obj)

        elif obj.objectName().split('/')[1]=="open":  # 저장 폴더 열려있을 때; 접기
            items=obj.parent().children()
            project_name=obj.objectName().split('/')[0]
            print(project_name)
            delete_obj=[]

            for i in range(len(items)):  # 삭제할 요소 탐색
                if items[i].objectName()==project_name+"/saved":
                    delete_obj.append(items[i])  # 삭제할 요소 임시 저장

            for i in range(len(delete_obj)):  # 삭제
                delete_obj[i].deleteLater()
                delete_obj[i].setParent(None)

            obj.setObjectName(project_name+"/close")  # 폴더 접음

        elif obj.objectName().split('/')[1]=="close":  # 저장 폴더 접혀있을 때; 열기
            insert_pos=self.left_div.indexOf(obj)+1
            project_name=obj.objectName().split('/')[0]
            save_file_names=[]

            for save_files in os.walk(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved"):  # 세이브 폴더 하위 파일 순회
                save_file_names.extend(save_files[2])  # 이름 저장

            for i in range(len(save_file_names)):
                save_file_name=save_file_names[i].split('.')
                extension=save_file_name[-1]  # 확장자
                save_file_name='.'.join(save_file_name[:len(save_file_name)-1])  # 파일 이름 조립(확장자 제외)

                print(save_file_name, extension)
                    
                if extension=="rsv":
                    new_save=QLabel(save_file_name)
                    new_save.setObjectName(project_name+"/saved")
                
                    self.left_div.insertWidget(insert_pos, new_save)  # 삽입
                    insert_pos+=1
                            
                    self.leftClickListener(new_save).connect(self.viewContent)  # 저장된 응답 좌클릭 시 내용 표시
                    self.rightClickListener(new_save).connect(self.viewContextMenu)  # 저장된 응답 우클릭 시 우클릭 메뉴 표시
                        
            obj.setObjectName(project_name+"/open")  # 폴더 염

    # 응답 내용 보이기
    def viewContent(self):
        project_name=self.last_left_clicked_object.objectName().split('/')[0]
        saved_name=self.last_left_clicked_object.text()

        Response.ResponseView(project_name=project_name.split('/')[0], saved_name=saved_name)
        print("Main.viewContent : "+ saved_name)

    # 요청 선택
    def viewRequest(self):
        self.saveCurProject()  # 요청 전환 전 현재 프로젝트 저장

        self.focusLabel(self.last_left_clicked_object)  # 하이라이트
        
        self.main_tabs.setCurrentIndex(0)  # 탭 전환

        Global.req.target.setText(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][0])
        Global.req.rest_dropdown.setCurrentIndex(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][1])
        Global.req.header.setPlainText(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][2])
        Global.req.payloads.setPlainText(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][3])


    # 새 요청 생성
    def newRequest(self):
        new_request_dialog=QInputDialog()

        name, ok=new_request_dialog.getText(self, "", "New Request", text=File.setNameAuto("", self.last_right_clicked_object.text(), 'q'), flags=Qt.WindowType.FramelessWindowHint)

        #todo# 요청 이름 겹치는 지 확인

        if ok:
            self.saveCurProject()  # 요청 전환 전 현재 프로젝트 저장

            if self.last_right_clicked_object.objectName()=="close":  # 프로젝트 접혀 있음
                self.viewSubItems(self.last_right_clicked_object)  # 프로젝트 열기

            children=self.last_right_clicked_object.parent().children()

            # 삽입 위치 탐색 후 삽입
            for i in range(2, len(children)):  # 2: 사이드 뷰 본인과 우클릭 트리거 제외
                if children[i].objectName().split('/')[0]==self.last_right_clicked_object.text() and\
                     (children[i].objectName().split('/')[1]=="open" or children[i].objectName().split('/')[1]=="close"):  # 해당 프로젝트의 saved 폴더 찾기
                    Global.projects_data[self.last_right_clicked_object.text()]["requests"][name]={}  # #todo#기본 요청 정보 저장

                    new_request=QLabel(name)
                    new_request.setObjectName(self.last_right_clicked_object.text())  # 프로젝트 이름으로 오브젝트 이름 설정
                    self.left_div.insertWidget(i-2, new_request)  # -2: 사이드 뷰 본인과 우클릭 트리거 제외
                    self.leftClickListener(new_request).connect(self.viewRequest)  # 요청 좌클릭 시 내용 표시
                    self.rightClickListener(new_request).connect(self.viewContextMenu)  # 요청 우클릭 시 우클릭 메뉴 표시

                    break

            self.viewRequest(self.last_right_clicked_object.text(), name)
            
        self.focusLabel(new_request)  # 하이라이트
        File.saveProject(self.last_right_clicked_object.text())  # 저장

    # 프로젝트, 저장된 응답, 요청 이름 변경
    def rename(self):
        rename_dialog=QInputDialog()

        if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트 일 때
            name, ok=rename_dialog.getText(self, "", "Rename Project", flags=Qt.WindowType.FramelessWindowHint)
        else:
            name, ok=rename_dialog.getText(self, "", "Rename", flags=Qt.WindowType.FramelessWindowHint)

        #todo# 이름 겹치는 지 확인(경로/이름 <-이 존재하는지)

        if ok:
            if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트일 때
                Global.projects_data[name]=Global.projects_data[self.last_right_clicked_object.text()]  # 데이터 복제
                Global.projects_data[name]["project_name"]=name  # 데이터 이름 변경
                shutil.move(Global.projects_data[name]["last_path"]+'/'+self.last_right_clicked_object.text(), Global.projects_data[name]["last_path"]+'/'+name)  # 프로젝트 폴더 이름변경
                shutil.move(Global.projects_data[name]["last_path"]+'/'+name+'/'+self.last_right_clicked_object.text()+".ahp", Global.projects_data[name]["last_path"]+'/'+name+'/'+name+".ahp")
                # -> 프로젝트 파일 이름 변경
                del Global.projects_data[self.last_right_clicked_object.text()]  # 원본 데이터 삭제

                # 사이드 뷰의 하위 요소(요청, 응답) objectName 변경하기
                children=self.last_right_clicked_object.parent().children()

                for i in range(len(children)):
                    tag=children[i].objectName().split('/')

                    if tag[0]==self.last_right_clicked_object.text():
                        if len(tag)==1:  # 요청
                            children[i].setObjectName(name)
                        else:  # 저장 폴더, 응답
                            children[i].setObjectName(name+'/'+tag[1])  # 폴더의 경우 열림/접힘 상태 유지

                self.last_right_clicked_object.setText(name)  # 사이드 뷰의 오브젝트 이름 변경

            elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # 요청일 때
                project_name=self.last_right_clicked_object.objectName().split('/')[0]  # 오브젝트 이름에서 프로젝트 이름 가져오기

                Global.projects_data[project_name]["requests"][name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]  # 데이터 복제
                del Global.projects_data[self.last_right_clicked_object.text()]  # 원본 데이터 삭제

                self.last_right_clicked_object.setText(name)  # 사이드 뷰의 오브젝트 이름 변경

            else:  # 저장된 응답일 때
                project_name=self.last_right_clicked_object.objectName().split('/')[0]  # 오브젝트 이름에서 프로젝트 이름 가져오기

                shutil.move(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+self.last_right_clicked_object.text()+'.rsv', \
                    Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+name+'.rsv')  # 저장된 파일 이름 변경

                self.last_right_clicked_object.setText(name)  # 사이드 뷰의 오브젝트 이름 변경

        else:
            print("cancel")

    # 저장된 응답, 요청 복제
    def duplicate(self):
        if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트일 때
            project_name=self.last_right_clicked_object.text()
            project_path=Global.projects_data[project_name]['last_path']
            new_name=File.setNameAuto(project_name, "", 'p')

            # 파일 복제
            shutil.copy(project_path+'/'+project_name, project_path+'/'+new_name)  # 프로젝트 폴더 복제
            shutil.move(project_path+'/'+project_name+'/'+project_name+".ahp", project_path+'/'+new_name+'/'+new_name+".ahp")  # 프로젝트 파일 이름 변경
            Global.projects_data[new_name]=Global.projects_data[project_name]  # 데이터 복제
            Global.projects_data[new_name]["project_name"]=new_name

            self.initLeft(new_name)

        elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # 요청일 때
            project_name=self.last_right_clicked_object.objectName()
            new_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 'q')

            # 새 요청 생성
            Global.projects_data[project_name]["requests"][new_name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]
            # -> 데이터 복제

            new_request=QLabel(new_name)
            new_request.setObjectName(project_name)
            insert_pos=self.left_div.indexOf(self.last_right_clicked_object)+1
            self.left_div.insertWidget(insert_pos, new_request)  # 리스트에 삽입
            self.leftClickListener(new_request).connect(self.viewRequest)  #요청 좌클릭 시 내용 표시
            self.rightClickListener(new_request).connect(self.viewContextMenu)  # 요청 우클릭 시 우클릭 메뉴 표시

            self.focusLabel(new_save)
            File.saveProject(project_name)

        else:  # 저장된 응답일 때
            project_name=self.last_right_clicked_object.objectName().split('/')[0]
            project_path=Global.projects_data[project_name]['last_path']+'/'+project_name
            new_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 's')

            shutil.copy(project_path+"/saved/"+self.last_right_clicked_object.text()+".rsv", project_path+"/saved/"+new_name+".rsv")  # 저장 파일 복제
            
            new_save=QLabel(new_name)
            new_save.setObjectName(project_name+"/saved")
            insert_pos=self.left_div.indexOf(self.last_right_clicked_object)+1
            self.left_div.insertWidget(insert_pos, new_save)  # 리스트에 삽입
            self.leftClickListener(new_save).connect(self.viewContent)  # 저장된 응답 좌클릭 시 내용 표시
            self.rightClickListener(new_save).connect(self.viewContextMenu)  # 저장된 응답 우클릭 시 우클릭 메뉴 표시

            self.focusLabel(new_save)

    # 프로젝트, 저장된 응답, 요청 삭제
    def delete(self):
        if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트일 때
            are_you_sure=QMessageBox()
            are_you_sure.setText("Delete Project File?")
            are_you_sure.setStandardButtons(QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.No|QMessageBox.StandardButton.Yes)
            answer=are_you_sure.exec()

            if answer!=QMessageBox.StandardButton.Cancel:
                # 사이드 뷰의 하위 요소(요청, 응답) 삭제
                children=self.last_right_clicked_object.parent().children()
                delete_obj=[]

                for i in range(len(children)):  # 탐색
                    print(children[i].objectName())
                    if children[i].objectName().split('/')[0]==self.last_right_clicked_object.text():  # 하위 요청
                        delete_obj.append(children[i])  # 삭제할 오브젝트 임시 저장

                for i in range(len(delete_obj)):  # 삭제
                    delete_obj[i].deleteLater()
                    delete_obj[i].setParent(None)

                if answer==QMessageBox.StandardButton.Yes:  # 파일까지 삭제 선택
                    print(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())
                    shutil.rmtree(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())  # 프로젝트 폴더 삭제

                del Global.projects_data[self.last_right_clicked_object.text()]  # 프로젝트 데이터 삭제

                # 사이드 뷰에서 프로젝트 제거
                self.last_right_clicked_object.deleteLater()
                self.last_right_clicked_object.setParent(None)

        elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # 요청일 때
            project_name=self.last_right_clicked_object.objectName()  # 프로젝트 이름 가져오기
            name=self.last_right_clicked_object.text()  # 요청 이름 가져오기

            del Global.projects_data[project_name]["requests"][name]  # 요청 데이터 삭제

            #todo#  현재 탭이 Request이고 삭제한 요청이 열려있는 상태일때 탭 전환
            #todo#  각 프로젝트에서 요청 최소 1개씩은 남길 것
            
            # 사이드 뷰에서 제거
            self.last_right_clicked_object.deleteLater()
            self.last_right_clicked_object.setParent(None)
            
        else:  # 저장된 응답일 때
            project_name=self.last_right_clicked_object.objectName().split('/')[0]  # 프로젝트 이름 가져오기
            name=self.last_right_clicked_object.text()  # 저장된 응답 이름 가져오기

            os.remove(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+name+".rsv")  # 저장된 파일 삭제

            #todo#  해당 응답이 팝업 상태로 열려있을 떄 종료

            # 사이드 뷰에서 제거
            self.last_right_clicked_object.deleteLater()
            self.last_right_clicked_object.setParent(None)

    # 저장된 응답 전체 삭제
    def deleteAllSave(self):
        are_you_sure=QMessageBox.question(self, "", "Delete All Save?", QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.Yes)

        if are_you_sure==QMessageBox.StandardButton.Yes:
            children=self.last_right_clicked_object.parent().children()
            delete_obj=[]
            
            project_name=self.last_right_clicked_object.objectName().split('/')[0]  # 오브젝트 이름에서 프로젝트 이름 가져오기

            for i in range(len(children)):
                if children[i].objectName()==project_name+"/saved":  # 하위 저장된 응답
                    delete_obj.append(children[i])
                    os.remove(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+children[i].text()+".rsv")  # 파일 삭제

            for i in range(len(delete_obj)):  # 사이드 뷰에서 삭제
                delete_obj[i].deleteLater()
                delete_obj[i].setParent(None)
        
                
    # 현재 선택한 프로젝트 저장
    def saveCurProject(self):
        Global.var.getTabInfo()
        Global.req.getTabInfo()
        File.saveProject(self.last_highlighted_project)

    ## 프로젝트 추가
    # 프로젝트 생성 팝업 생성
    def createProject(self):
        print("create project")
        pop=CreateProjectPopup()

        if pop.is_created:
            self.initLeft(pop.pjname_if.text())  # 사이드 뷰 적용
            self.reInitTab(pop.pjname_if.text())

    # 프로젝트 불러오기 팝업 생성(파일 탐색기)
    def openProject(self):
        print("open project")
        path= QFileDialog.getOpenFileName(self, 'Open file', './')

        if path[0]:
            path=path[0].split('/')
            project_path='/'.join(path[:len(path)-2])
            project_name=path[-1]
            
            print(project_path, project_name)

            if not project_name.split('.')[-1]=="ahp":  # 프로젝트 파일이 아닐 때
                print("not project file")
            else:
                is_project_opened=File.openProject(project_path, project_name.split('.')[0])

                if not is_project_opened:
                    self.initLeft(project_name.split('.')[0])  # 사이드뷰 프로젝트 목록에 추가
                    self.reInitTab(project_name.split('.')[0])  # 탭 재구성



#################### EventListener ####################

    # 사이드 뷰 좌클릭 감지
    def leftClickListener(self, widget) -> Signal:
        class Filter(QObject):
            clicked = Signal()

            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                    Global.main.last_left_clicked_object=obj
                    self.clicked.emit()

                return super().eventFilter(obj, event)

        click_filter = Filter(widget)
        widget.installEventFilter(click_filter)
        return click_filter.clicked

    # 사이드 뷰 우클릭 감지
    def rightClickListener(self, widget) -> Signal:
        class Filter(QObject):
            clicked = Signal()

            def eventFilter(self, obj, event:QEvent):
                if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
                    Global.main.right_click_mouse_pos=event.globalPos()
                    Global.main.last_right_clicked_object=obj
                    self.clicked.emit()

                return super().eventFilter(obj, event)

        click_filter = Filter(widget)
        widget.installEventFilter(click_filter)
        return click_filter.clicked



####################### Dialog #######################

class CreateProjectPopup(QDialog):
     def __init__(self):
         super().__init__()
         self.is_created=False

         self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
         self.initUI()
         self.exec()
        
     # UI 초기 설정
     def initUI(self):
         self.pjpath_if_div=QVBoxLayout()
         self.pjname_if_div=QVBoxLayout()
         self.tgurl_if_div=QVBoxLayout()
         self.btn_div=QHBoxLayout()
         
         # 프로젝트 경로 입력 칸
         self.pjpath_if_div.addWidget(QLabel("Project Path"))
         self.pjpath_if_div.addLayout(QHBoxLayout())
         self.pjpath_if=QLineEdit(Global.default_project_path)
         self.pjpath_if.textChanged.connect(lambda :self.pjname_if.setText(File.setNameAuto("", self.pjpath_if.text(), 'p')))
         self.file_exp_btn=QPushButton("\\")
         self.file_exp_btn.clicked.connect(lambda :self.pjpath_if.setText(QFileDialog.getExistingDirectory(parent=self, caption="Set Directory")))
         # -> 기본 파일 경로 설정
         #todo# -> getOpenFileUrl 매개변수로 Global.default_project_path 넣을 것
         self.pjpath_if_div.children()[0].addWidget(self.pjpath_if)
         self.pjpath_if_div.children()[0].addWidget(self.file_exp_btn)
         
         # 프로젝트 이름 입력 칸
         self.pjname_if_div.addWidget(QLabel("Project Name"))
         self.pjname_if=QLineEdit("myproject1")
         self.pjname_if_div.addWidget(self.pjname_if)
         
         # 타겟 URL 이름 입력 칸
         self.tgurl_if_div.addWidget(QLabel("Target Base URL"))
         self.tgurl_if=QLineEdit()
         self.tgurl_if_div.addWidget(self.tgurl_if)
         
         # 버튼 그룹
         self.cancel_btn=QPushButton("cancel")
         self.crt_btn=QPushButton("new project")
         self.cancel_btn.clicked.connect(self.onclickCancel)
         self.crt_btn.clicked.connect(self.onclickCreate)
         self.btn_div.addWidget(self.cancel_btn)
         self.btn_div.addWidget(self.crt_btn)
         
         # 전체 창
         self.this=QBoxLayout(QBoxLayout.TopToBottom)
         self.this.addLayout(self.pjpath_if_div)
         self.this.addLayout(self.pjname_if_div)
         self.this.addLayout(self.tgurl_if_div)
         self.this.addLayout(self.btn_div)
         self.setLayout(self.this)
         

     def onclickCancel(self):
         self.is_created=False
         self.close()
         return False
     
     def onclickCreate(self):
         if not File.createProject(self.pjpath_if.text(), self.pjname_if.text(), self.tgurl_if.text()):
             #todo# 이미 존재하는 이름이라고 알림 띄우기
             self.is_created=False
             return False
         else:
             self.is_created=True
             self.close()
             return True

  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainController()
    sys.exit(app.exec())
