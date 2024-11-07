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
        self.last_highlighted_project=""  # ���������� ���̶���Ʈ�� ������Ʈ �̸�
        self.last_highlighted_request=""  # ���������� ���̶���Ʈ�� ��û �̸�
        # -> ���� ������Ʈ �ľǿ� ���

        self.left_div_widget=None

        Global.main=self

        self.initUI()
    

    # UI �ʱ� ����
    def initUI(self):
        self.initMenu()
        self.initTab()
        
        self.setCentralWidget(self.main_tabs)  # ������Ʈ ���� �� �Ǹ� ǥ��(���̵�� ��ǥ��)
        
        # â ����
        self.setWindowTitle('APIHACK')
        self.setGeometry(960, 540, 480, 270) # ũ��, ��ġ ����
        self.show()


    # �޴� �� ����
    def initMenu(self):
        # �޴� �� ����
        self.menubar=QMenuBar()
        self.setMenuBar(self.menubar)
        self.menu_list={}
        
        ## ���� �޴� ����
        self.menu_list["File"]=self.menubar.addMenu("File")
        # ���� ���� �ɼ� ����
        self.menu_list["File"].addAction("New..", QKeySequence(Qt.CTRL | Qt.Key_N))
        self.menu_list["File"].children()[1].triggered.connect(self.createProject)  # �Լ� ����
        # ���� �ҷ����� �ɼ� ����
        self.menu_list["File"].addAction("Open..", QKeySequence(Qt.CTRL | Qt.Key_O))
        self.menu_list["File"].children()[2].triggered.connect(self.openProject)  # �Լ� ����
        # ���м�
        self.menu_list["File"].addAction("").setSeparator(True)
        # ���� ���� �ɼ� ����
        self.menu_list["File"].addAction("Save", QKeySequence(Qt.CTRL | Qt.Key_S))
        self.menu_list["File"].children()[4].triggered.connect(self.saveCurProject)  # �Լ� ����

    # �� ����
    def initTab(self):
        # �� ����
        self.main_tabs=QTabWidget()

        ## Ȩ ��
        self.home_tab=QWidget()
        self.main_tabs.addTab(self.home_tab, "HOME")
        self.home_tab_content=QBoxLayout(QBoxLayout.TopToBottom, self.home_tab)
        # �ؽ�Ʈ ǥ��
        self.home_tab_content.addWidget(QLabel("Start Hack With ***"))
        self.home_tab_content.addWidget(QLabel("Start new project or open existing projects"))
        # ��ư ����
        self.crt_pj_btn=QPushButton("new project")
        self.open_pj_btn=QPushButton("open project")
        self.crt_pj_btn.clicked.connect(self.createProject)
        self.open_pj_btn.clicked.connect(self.openProject)
        self.btn_div=QBoxLayout(QBoxLayout.LeftToRight)
        self.btn_div.addWidget(self.crt_pj_btn)
        self.btn_div.addWidget(self.open_pj_btn)
        self.home_tab_content.addLayout(self.btn_div)  # �� ���뿡 �߰�

        ## ���ڴ� ��
        self.decoder_tab=QWidget()
        self.main_tabs.addTab(self.decoder_tab, "Decoder")
        Decoder(self.decoder_tab)

    # ������Ʈ ����, �ҷ����� �� �� �籸��
    def reInitTab(self, project_name):
        if not self.is_tab_reinited:  # ���� �籸�� ����
            self.main_tabs.removeTab(0)  # Ȩ �� ����

            ## ��û ��
            self.request_tab=QWidget()
            self.main_tabs.insertTab(0, self.request_tab, "Request")
            Global.req=Request(self.request_tab)

            ## ���� ��
            self.variables_tab=QWidget()
            self.main_tabs.insertTab(1, self.variables_tab, "Variables")
            Global.var=Variables(self.variables_tab)

            ## ���� ��
            self.response_tab=QWidget()
            self.main_tabs.insertTab(2, self.response_tab, "Response")
            self.response_tab.setObjectName("response_tab")
            Global.res=Response(self.response_tab)
        
        else:  # �籸�� ��(���� ����� ������Ʈ�� ����)
            self.saveCurProject()  # ������Ʈ ��ȯ �� ���� ������Ʈ ����

        self.main_tabs.setCurrentIndex(1)  # ��û ������ �� ����
        self.is_tab_reinited=True

        tmp_request=list(Global.projects_data[project_name]["requests"].keys())[0]
        self.last_highlighted_project=project_name
        self.last_highlighted_request=tmp_request
        Global.req.initRequest(project_name, tmp_request) # ��û �� ����
        Global.var.initVariables(project_name) # ���� �� ����
        

    # ������Ʈ ����/�ҷ����� �� ���̵�� ����/������Ʈ + ������Ʈ ����/*����* ��� �� ��� 
    def initLeft(self, project_name, insert_pos=-1):
        if self.left_div_widget==None:  # ���� ���̵� �䰡 ���� ��
            self.left_div_widget=QWidget()
            self.left_div=QVBoxLayout(self.left_div_widget)
            self.left_div_widget.setObjectName("left")

            self.rightClickListener(self.left_div_widget).connect(self.viewContextMenu)

            # ���̵� �� ����
            self.body_div=QWidget()
            self.body=QHBoxLayout(self.body_div)
            self.body.addWidget(self.left_div_widget)
            self.body.addWidget(self.main_tabs)
            self.setCentralWidget(self.body_div)
            
        ## ��� ����
        # ������Ʈ
        if insert_pos==-1:  # �̹� ������Ʈ�� ���� ����
            new_project=QLabel(project_name)  # ���� ǥ�� ������ �ֱ�
            new_project.setObjectName("open")
            self.left_div.addWidget(new_project)
            self.leftClickListener(new_project).connect(lambda :self.viewSubItems(new_project))  # ������Ʈ ��Ŭ�� �� ���� ��� ǥ��
            self.rightClickListener(new_project).connect(self.viewContextMenu)  # ������Ʈ ��Ŭ�� �� ��Ŭ�� �޴� ǥ��
            
            self.focusLabel(new_project)

        # ��û
        for request_name in Global.projects_data[project_name]["requests"].keys():
            new_request=(QLabel(request_name))
            new_request.setObjectName(project_name)

            if insert_pos==-1:
                self.left_div.addWidget(new_request)
            else:
                self.left_div.insertWidget(insert_pos, new_request)
                insert_pos+=1

            self.leftClickListener(new_request).connect(self.viewRequest)  # ��û ��Ŭ�� �� ���� ǥ��
            self.rightClickListener(new_request).connect(self.viewContextMenu)  # ��û ��Ŭ�� �� ��Ŭ�� �޴� ǥ��

        # ����� ���� ����
        new_saves=QLabel("saved")
        new_saves.setObjectName(project_name+"/open")

        if insert_pos==-1:
            self.left_div.addWidget(new_saves)
        else:
            self.left_div.insertWidget(insert_pos, new_saves)
            insert_pos+=1
        
        self.leftClickListener(new_saves).connect(lambda :self.viewSubItems(new_saves))  # ��Ŭ�� ��
        self.rightClickListener(new_saves).connect(self.viewContextMenu)  # ��Ŭ�� �� ��Ŭ�� �޴� ǥ��

        # ����� ����
        save_file_names=[]
        for save_files in os.walk(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved"):  # ���̺� ���� ���� ���� ��ȸ
            save_file_names.extend(save_files[2])  # �̸� ����

        for i in range(len(save_file_names)):
            save_file_name=save_file_names[i].split('.')
            extension=save_file_name[-1]  # Ȯ����
            save_file_name='.'.join(save_file_name[:len(save_file_name)-1])  # ���� �̸� ����(Ȯ���� ����)

            print(save_file_name, extension)

            if extension=="rsv":
                new_save=QLabel(save_file_name)
                new_save.setObjectName(project_name+"/saved")
                
                if insert_pos==-1:
                    self.left_div.addWidget(new_save)
                else:
                    self.left_div.insertWidget(insert_pos, new_save)
                    insert_pos+=1

                self.leftClickListener(new_save).connect(self.viewContent)  # ����� ���� ��Ŭ�� �� ���� ǥ��
                self.rightClickListener(new_save).connect(self.viewContextMenu)  # ����� ���� ��Ŭ�� �� ��Ŭ�� �޴� ǥ��


    # ���̵��� ��� Ŭ�� �� ���̶���Ʈ ǥ��
    # ������Ʈ, ��û QLabel�� ����
    def focusLabel(self, obj:QLabel):
        ### ���� ���̶���Ʈ ����
        if not (self.last_highlighted_project=="" and self.last_highlighted_request==""):  # ���� ���̶���Ʈ �Ǿ��ִ� ������Ʈ ���� ����
            ## ���̶���Ʈ�� ������Ʈ Ž��
            project_labels=list(obj.parent().findChildren(QLabel, "open"))  # �����ִ� ������Ʈ Ž��
            project_labels.extend(list(obj.parent().findChildren(QLabel, "close")))  # �����ִ� ������Ʈ Ž��

            for project_label in project_labels:  # ������Ʈ Ž��
                if project_label.text()==self.last_highlighted_project:  # ���̶���Ʈ�� ������Ʈ ã��
                    project_label.setStyleSheet("")  # ���̶���Ʈ ����
                    break

            self.last_highlighted_project=""

            if self.last_highlighted_request!="":  # �ֱ� ���̶���Ʈ �� ������Ʈ�� "��û"��
                request_labels=list(obj.parent().findChildren(QLabel, self.last_highlighted_project))  # ������Ʈ�� ���� ��û Ž��

                for request_label in request_labels:  # ������Ʈ Ž��
                    if request_label.text()==self.last_highlighted_request:  # ���̶���Ʈ�� ��û ã��
                        request_label.setStyleSheet("")  # ���̶���Ʈ ����
                        break

        ### ���̶���Ʈ �߰�
        if not (obj.objectName()=="open" or obj.objectName()=="close"):  # ��û ���ý�
            project_labels=list(obj.parent().findChildren(QLabel, "open"))  # �����ִ� ������Ʈ Ž��
            project_labels.extend(list(obj.parent().findChildren(QLabel, "close")))  # �����ִ� ������Ʈ Ž��
        
            for project_label in project_labels:  # ���� ���̶���Ʈ �� ��û�� ������Ʈ Ž��
                if project_label.text()==obj.objectName():
                    project_label.setStyleSheet("background-color:gray;")  # ������Ʈ ���̶���Ʈ
                    break
            
            self.last_highlighted_request=obj.text()  # ���� ���̶���Ʈ�� ��û �̸� ����
            self.last_highlighted_project=obj.objectName()  # ���� ���̶���Ʈ�� ������Ʈ �̸� ����
        else:  # ������Ʈ ���ý�
            self.last_highlighted_project=obj.text()  # ���� ���̶���Ʈ�� ������Ʈ �̸� ����

        obj.setStyleSheet("background-color:gray;")  # ���̶���Ʈ

    # ��Ŭ�� �� ���� ������ ���̱�/�����
    # ������Ʈ, ���� ������ ����
    def viewSubItems(self, obj:QLabel):
        if obj.objectName()=="open":  # ������Ʈ �������� ��; ����
            if obj.text()!=self.last_highlighted_project:  # ���̶���Ʈ�� ����
                # -> not (������Ʈ�� �ֱ� ���� or ������Ʈ�� ���� ��û�� �ֱ� ���õ�)
                self.focusLabel(obj)  # ������Ʈ ���̶���Ʈ
                return  # ����

            items=obj.parent().children()
            delete_obj=[]

            for i in range(len(items)):  # ������ ��� Ž��
                if items[i].objectName().split('/')[0]==obj.text():
                    delete_obj.append(items[i])  # ������ ��� �ӽ� ����
                    print(items[i])

            for i in range(len(delete_obj)):  # ����
                delete_obj[i].deleteLater()
                delete_obj[i].setParent(None)
            
            obj.setObjectName("close")  # ������Ʈ ����

        elif obj.objectName()=="close":  # ������Ʈ �������� ��; ����
            self.initLeft(obj.text(), insert_pos=self.left_div.indexOf(obj)+1)

            obj.setObjectName("open")  # ������Ʈ ��

            if obj.text()!=self.last_highlighted_project:  # ���̶���Ʈ�� ����
                self.focusLabel(obj)

        elif obj.objectName().split('/')[1]=="open":  # ���� ���� �������� ��; ����
            items=obj.parent().children()
            project_name=obj.objectName().split('/')[0]
            print(project_name)
            delete_obj=[]

            for i in range(len(items)):  # ������ ��� Ž��
                if items[i].objectName()==project_name+"/saved":
                    delete_obj.append(items[i])  # ������ ��� �ӽ� ����

            for i in range(len(delete_obj)):  # ����
                delete_obj[i].deleteLater()
                delete_obj[i].setParent(None)

            obj.setObjectName(project_name+"/close")  # ���� ����

        elif obj.objectName().split('/')[1]=="close":  # ���� ���� �������� ��; ����
            insert_pos=self.left_div.indexOf(obj)+1
            project_name=obj.objectName().split('/')[0]
            save_file_names=[]

            for save_files in os.walk(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved"):  # ���̺� ���� ���� ���� ��ȸ
                save_file_names.extend(save_files[2])  # �̸� ����

            for i in range(len(save_file_names)):
                save_file_name=save_file_names[i].split('.')
                extension=save_file_name[-1]  # Ȯ����
                save_file_name='.'.join(save_file_name[:len(save_file_name)-1])  # ���� �̸� ����(Ȯ���� ����)

                print(save_file_name, extension)
                    
                if extension=="rsv":
                    new_save=QLabel(save_file_name)
                    new_save.setObjectName(project_name+"/saved")
                
                    self.left_div.insertWidget(insert_pos, new_save)  # ����
                    insert_pos+=1
                            
                    self.leftClickListener(new_save).connect(self.viewContent)  # ����� ���� ��Ŭ�� �� ���� ǥ��
                    self.rightClickListener(new_save).connect(self.viewContextMenu)  # ����� ���� ��Ŭ�� �� ��Ŭ�� �޴� ǥ��
                        
            obj.setObjectName(project_name+"/open")  # ���� ��

    # ���� ���� ���̱�
    def viewContent(self):
        project_name=self.last_left_clicked_object.objectName().split('/')[0]
        saved_name=self.last_left_clicked_object.text()

        Response.ResponseView(project_name=project_name.split('/')[0], saved_name=saved_name)
        print("Main.viewContent : "+ saved_name)

    # ��û ����
    def viewRequest(self):
        self.saveCurProject()  # ��û ��ȯ �� ���� ������Ʈ ����

        self.focusLabel(self.last_left_clicked_object)  # ���̶���Ʈ
        
        self.main_tabs.setCurrentIndex(0)  # �� ��ȯ

        Global.req.target.setText(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][0])
        Global.req.rest_dropdown.setCurrentIndex(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][1])
        Global.req.header.setPlainText(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][2])
        Global.req.payloads.setPlainText(Global.projects_data[self.last_highlighted_project]["requests"][self.last_highlighted_request][3])


    # �� ��û ����
    def newRequest(self):
        new_request_dialog=QInputDialog()

        name, ok=new_request_dialog.getText(self, "", "New Request", text=File.setNameAuto("", self.last_right_clicked_object.text(), 'q'), flags=Qt.WindowType.FramelessWindowHint)

        #todo# ��û �̸� ��ġ�� �� Ȯ��

        if ok:
            self.saveCurProject()  # ��û ��ȯ �� ���� ������Ʈ ����

            if self.last_right_clicked_object.objectName()=="close":  # ������Ʈ ���� ����
                self.viewSubItems(self.last_right_clicked_object)  # ������Ʈ ����

            children=self.last_right_clicked_object.parent().children()

            # ���� ��ġ Ž�� �� ����
            for i in range(2, len(children)):  # 2: ���̵� �� ���ΰ� ��Ŭ�� Ʈ���� ����
                if children[i].objectName().split('/')[0]==self.last_right_clicked_object.text() and\
                     (children[i].objectName().split('/')[1]=="open" or children[i].objectName().split('/')[1]=="close"):  # �ش� ������Ʈ�� saved ���� ã��
                    Global.projects_data[self.last_right_clicked_object.text()]["requests"][name]={}  # #todo#�⺻ ��û ���� ����

                    new_request=QLabel(name)
                    new_request.setObjectName(self.last_right_clicked_object.text())  # ������Ʈ �̸����� ������Ʈ �̸� ����
                    self.left_div.insertWidget(i-2, new_request)  # -2: ���̵� �� ���ΰ� ��Ŭ�� Ʈ���� ����
                    self.leftClickListener(new_request).connect(self.viewRequest)  # ��û ��Ŭ�� �� ���� ǥ��
                    self.rightClickListener(new_request).connect(self.viewContextMenu)  # ��û ��Ŭ�� �� ��Ŭ�� �޴� ǥ��

                    break

            self.viewRequest(self.last_right_clicked_object.text(), name)
            
        self.focusLabel(new_request)  # ���̶���Ʈ
        File.saveProject(self.last_right_clicked_object.text())  # ����

    # ������Ʈ, ����� ����, ��û �̸� ����
    def rename(self):
        rename_dialog=QInputDialog()

        if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ �� ��
            name, ok=rename_dialog.getText(self, "", "Rename Project", flags=Qt.WindowType.FramelessWindowHint)
        else:
            name, ok=rename_dialog.getText(self, "", "Rename", flags=Qt.WindowType.FramelessWindowHint)

        #todo# �̸� ��ġ�� �� Ȯ��(���/�̸� <-�� �����ϴ���)

        if ok:
            if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ�� ��
                Global.projects_data[name]=Global.projects_data[self.last_right_clicked_object.text()]  # ������ ����
                Global.projects_data[name]["project_name"]=name  # ������ �̸� ����
                shutil.move(Global.projects_data[name]["last_path"]+'/'+self.last_right_clicked_object.text(), Global.projects_data[name]["last_path"]+'/'+name)  # ������Ʈ ���� �̸�����
                shutil.move(Global.projects_data[name]["last_path"]+'/'+name+'/'+self.last_right_clicked_object.text()+".ahp", Global.projects_data[name]["last_path"]+'/'+name+'/'+name+".ahp")
                # -> ������Ʈ ���� �̸� ����
                del Global.projects_data[self.last_right_clicked_object.text()]  # ���� ������ ����

                # ���̵� ���� ���� ���(��û, ����) objectName �����ϱ�
                children=self.last_right_clicked_object.parent().children()

                for i in range(len(children)):
                    tag=children[i].objectName().split('/')

                    if tag[0]==self.last_right_clicked_object.text():
                        if len(tag)==1:  # ��û
                            children[i].setObjectName(name)
                        else:  # ���� ����, ����
                            children[i].setObjectName(name+'/'+tag[1])  # ������ ��� ����/���� ���� ����

                self.last_right_clicked_object.setText(name)  # ���̵� ���� ������Ʈ �̸� ����

            elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # ��û�� ��
                project_name=self.last_right_clicked_object.objectName().split('/')[0]  # ������Ʈ �̸����� ������Ʈ �̸� ��������

                Global.projects_data[project_name]["requests"][name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]  # ������ ����
                del Global.projects_data[self.last_right_clicked_object.text()]  # ���� ������ ����

                self.last_right_clicked_object.setText(name)  # ���̵� ���� ������Ʈ �̸� ����

            else:  # ����� ������ ��
                project_name=self.last_right_clicked_object.objectName().split('/')[0]  # ������Ʈ �̸����� ������Ʈ �̸� ��������

                shutil.move(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+self.last_right_clicked_object.text()+'.rsv', \
                    Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+name+'.rsv')  # ����� ���� �̸� ����

                self.last_right_clicked_object.setText(name)  # ���̵� ���� ������Ʈ �̸� ����

        else:
            print("cancel")

    # ����� ����, ��û ����
    def duplicate(self):
        if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ�� ��
            project_name=self.last_right_clicked_object.text()
            project_path=Global.projects_data[project_name]['last_path']
            new_name=File.setNameAuto(project_name, "", 'p')

            # ���� ����
            shutil.copy(project_path+'/'+project_name, project_path+'/'+new_name)  # ������Ʈ ���� ����
            shutil.move(project_path+'/'+project_name+'/'+project_name+".ahp", project_path+'/'+new_name+'/'+new_name+".ahp")  # ������Ʈ ���� �̸� ����
            Global.projects_data[new_name]=Global.projects_data[project_name]  # ������ ����
            Global.projects_data[new_name]["project_name"]=new_name

            self.initLeft(new_name)

        elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # ��û�� ��
            project_name=self.last_right_clicked_object.objectName()
            new_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 'q')

            # �� ��û ����
            Global.projects_data[project_name]["requests"][new_name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]
            # -> ������ ����

            new_request=QLabel(new_name)
            new_request.setObjectName(project_name)
            insert_pos=self.left_div.indexOf(self.last_right_clicked_object)+1
            self.left_div.insertWidget(insert_pos, new_request)  # ����Ʈ�� ����
            self.leftClickListener(new_request).connect(self.viewRequest)  #��û ��Ŭ�� �� ���� ǥ��
            self.rightClickListener(new_request).connect(self.viewContextMenu)  # ��û ��Ŭ�� �� ��Ŭ�� �޴� ǥ��

            self.focusLabel(new_save)
            File.saveProject(project_name)

        else:  # ����� ������ ��
            project_name=self.last_right_clicked_object.objectName().split('/')[0]
            project_path=Global.projects_data[project_name]['last_path']+'/'+project_name
            new_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 's')

            shutil.copy(project_path+"/saved/"+self.last_right_clicked_object.text()+".rsv", project_path+"/saved/"+new_name+".rsv")  # ���� ���� ����
            
            new_save=QLabel(new_name)
            new_save.setObjectName(project_name+"/saved")
            insert_pos=self.left_div.indexOf(self.last_right_clicked_object)+1
            self.left_div.insertWidget(insert_pos, new_save)  # ����Ʈ�� ����
            self.leftClickListener(new_save).connect(self.viewContent)  # ����� ���� ��Ŭ�� �� ���� ǥ��
            self.rightClickListener(new_save).connect(self.viewContextMenu)  # ����� ���� ��Ŭ�� �� ��Ŭ�� �޴� ǥ��

            self.focusLabel(new_save)

    # ������Ʈ, ����� ����, ��û ����
    def delete(self):
        if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ�� ��
            are_you_sure=QMessageBox()
            are_you_sure.setText("Delete Project File?")
            are_you_sure.setStandardButtons(QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.No|QMessageBox.StandardButton.Yes)
            answer=are_you_sure.exec()

            if answer!=QMessageBox.StandardButton.Cancel:
                # ���̵� ���� ���� ���(��û, ����) ����
                children=self.last_right_clicked_object.parent().children()
                delete_obj=[]

                for i in range(len(children)):  # Ž��
                    print(children[i].objectName())
                    if children[i].objectName().split('/')[0]==self.last_right_clicked_object.text():  # ���� ��û
                        delete_obj.append(children[i])  # ������ ������Ʈ �ӽ� ����

                for i in range(len(delete_obj)):  # ����
                    delete_obj[i].deleteLater()
                    delete_obj[i].setParent(None)

                if answer==QMessageBox.StandardButton.Yes:  # ���ϱ��� ���� ����
                    print(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())
                    shutil.rmtree(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())  # ������Ʈ ���� ����

                del Global.projects_data[self.last_right_clicked_object.text()]  # ������Ʈ ������ ����

                # ���̵� �信�� ������Ʈ ����
                self.last_right_clicked_object.deleteLater()
                self.last_right_clicked_object.setParent(None)

        elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # ��û�� ��
            project_name=self.last_right_clicked_object.objectName()  # ������Ʈ �̸� ��������
            name=self.last_right_clicked_object.text()  # ��û �̸� ��������

            del Global.projects_data[project_name]["requests"][name]  # ��û ������ ����

            #todo#  ���� ���� Request�̰� ������ ��û�� �����ִ� �����϶� �� ��ȯ
            #todo#  �� ������Ʈ���� ��û �ּ� 1������ ���� ��
            
            # ���̵� �信�� ����
            self.last_right_clicked_object.deleteLater()
            self.last_right_clicked_object.setParent(None)
            
        else:  # ����� ������ ��
            project_name=self.last_right_clicked_object.objectName().split('/')[0]  # ������Ʈ �̸� ��������
            name=self.last_right_clicked_object.text()  # ����� ���� �̸� ��������

            os.remove(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+name+".rsv")  # ����� ���� ����

            #todo#  �ش� ������ �˾� ���·� �������� �� ����

            # ���̵� �信�� ����
            self.last_right_clicked_object.deleteLater()
            self.last_right_clicked_object.setParent(None)

    # ����� ���� ��ü ����
    def deleteAllSave(self):
        are_you_sure=QMessageBox.question(self, "", "Delete All Save?", QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.Yes)

        if are_you_sure==QMessageBox.StandardButton.Yes:
            children=self.last_right_clicked_object.parent().children()
            delete_obj=[]
            
            project_name=self.last_right_clicked_object.objectName().split('/')[0]  # ������Ʈ �̸����� ������Ʈ �̸� ��������

            for i in range(len(children)):
                if children[i].objectName()==project_name+"/saved":  # ���� ����� ����
                    delete_obj.append(children[i])
                    os.remove(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+children[i].text()+".rsv")  # ���� ����

            for i in range(len(delete_obj)):  # ���̵� �信�� ����
                delete_obj[i].deleteLater()
                delete_obj[i].setParent(None)
        
                
    # ���� ������ ������Ʈ ����
    def saveCurProject(self):
        Global.var.getTabInfo()
        Global.req.getTabInfo()
        File.saveProject(self.last_highlighted_project)

    ## ������Ʈ �߰�
    # ������Ʈ ���� �˾� ����
    def createProject(self):
        print("create project")
        pop=CreateProjectPopup()

        if pop.is_created:
            self.initLeft(pop.pjname_if.text())  # ���̵� �� ����
            self.reInitTab(pop.pjname_if.text())

    # ������Ʈ �ҷ����� �˾� ����(���� Ž����)
    def openProject(self):
        print("open project")
        path= QFileDialog.getOpenFileName(self, 'Open file', './')

        if path[0]:
            path=path[0].split('/')
            project_path='/'.join(path[:len(path)-2])
            project_name=path[-1]
            
            print(project_path, project_name)

            if not project_name.split('.')[-1]=="ahp":  # ������Ʈ ������ �ƴ� ��
                print("not project file")
            else:
                is_project_opened=File.openProject(project_path, project_name.split('.')[0])

                if not is_project_opened:
                    self.initLeft(project_name.split('.')[0])  # ���̵�� ������Ʈ ��Ͽ� �߰�
                    self.reInitTab(project_name.split('.')[0])  # �� �籸��



#################### EventListener ####################

    # ���̵� �� ��Ŭ�� ����
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

    # ���̵� �� ��Ŭ�� ����
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
        
     # UI �ʱ� ����
     def initUI(self):
         self.pjpath_if_div=QVBoxLayout()
         self.pjname_if_div=QVBoxLayout()
         self.tgurl_if_div=QVBoxLayout()
         self.btn_div=QHBoxLayout()
         
         # ������Ʈ ��� �Է� ĭ
         self.pjpath_if_div.addWidget(QLabel("Project Path"))
         self.pjpath_if_div.addLayout(QHBoxLayout())
         self.pjpath_if=QLineEdit(Global.default_project_path)
         self.pjpath_if.textChanged.connect(lambda :self.pjname_if.setText(File.setNameAuto("", self.pjpath_if.text(), 'p')))
         self.file_exp_btn=QPushButton("\\")
         self.file_exp_btn.clicked.connect(lambda :self.pjpath_if.setText(QFileDialog.getExistingDirectory(parent=self, caption="Set Directory")))
         # -> �⺻ ���� ��� ����
         #todo# -> getOpenFileUrl �Ű������� Global.default_project_path ���� ��
         self.pjpath_if_div.children()[0].addWidget(self.pjpath_if)
         self.pjpath_if_div.children()[0].addWidget(self.file_exp_btn)
         
         # ������Ʈ �̸� �Է� ĭ
         self.pjname_if_div.addWidget(QLabel("Project Name"))
         self.pjname_if=QLineEdit("myproject1")
         self.pjname_if_div.addWidget(self.pjname_if)
         
         # Ÿ�� URL �̸� �Է� ĭ
         self.tgurl_if_div.addWidget(QLabel("Target Base URL"))
         self.tgurl_if=QLineEdit()
         self.tgurl_if_div.addWidget(self.tgurl_if)
         
         # ��ư �׷�
         self.cancel_btn=QPushButton("cancel")
         self.crt_btn=QPushButton("new project")
         self.cancel_btn.clicked.connect(self.onclickCancel)
         self.crt_btn.clicked.connect(self.onclickCreate)
         self.btn_div.addWidget(self.cancel_btn)
         self.btn_div.addWidget(self.crt_btn)
         
         # ��ü â
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
             #todo# �̹� �����ϴ� �̸��̶�� �˸� ����
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
