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
        ## ���� ���̺� ��
        self.var_table_label=QHBoxLayout()
        self.var_table_label.addWidget(QLabel("*"))
        self.var_table_label.addWidget(QLabel("Name"))
        self.var_table_label.addWidget(QLabel("Type"))
        self.var_table_label.addWidget(QLabel("Range"))
        self.var_table_label.addWidget(QLabel("Fix"))
        self.variables_tab_content.addLayout(self.var_table_label)

        ## + ��ư �߰�
        self.var_add_row_btn=QPushButton("+")
        self.var_add_row_btn.clicked.connect(lambda :self.addRow())
        self.variables_tab_content.addWidget(self.var_add_row_btn)

    # �� �� �߰�
    def addRow(self, saved_var=["", "", "", ""]):
        row=QHBoxLayout()
        row.addWidget(QCheckBox())
            
        for i in range(4):
            row.addWidget(QLineEdit(saved_var[i]))
        
        print("add Var")

        self.variables_tab_content.insertLayout(len(self.variables_tab_content.children()), row)


    # ���� ������Ʈ�� ���� ����
    def initVariables(self, project_name):
        children=self.variables_tab_content.children()
        delete_obj=[]

        print(children)
      
        ## ���� ���� �� ����
        for i in range(1, len(children)):
            delete_obj.append(children[i])
            for j in range(5):  # ������ üũ�ڽ�, �Է�â ����
                delete_obj.append(children[i].itemAt(j).widget())
            
        for i in range(len(delete_obj)):  # ������Ʈ ����
            delete_obj[i].deleteLater()
            delete_obj[i].setParent(None)
            
        saved_vars=list(Global.projects_data[project_name]["variables"].keys())
        
        ## ����� ���� �߰�
        for i in range(len(saved_vars)):
            self.addRow([saved_vars[i]]+Global.projects_data[project_name]["variables"][saved_vars[i]])

    # ���� �� ���� ���� ���� ��ȯ
    def getTabInfo(self):
        var_list=list(self.variables_tab_content.findChildren(QHBoxLayout))
        Global.projects_data[Global.main.last_highlighted_project]["variables"]={}  # ���� ���� �� �ʱ�ȭ

        for i in range(1, len(var_list)):
            var_name=var_list[i].itemAt(1).widget().text()
            var_type=var_list[i].itemAt(2).widget().text()
            var_range=var_list[i].itemAt(3).widget().text()
            var_fix=var_list[i].itemAt(4).widget().text()

            Global.projects_data[Global.main.last_highlighted_project]["variables"][var_name]=[var_type, var_range, var_fix]  # ���� �Է�


    # ���� �ν� �� ��ȸ
    # ��ũ, ���, ���̷ε忡 ���Ե� ����(������� ����) �ľ�
    def getPlainText(link:str, header:str, payloads:str):
        var_names=[]
        
        ## ��ũ
        link_vars, link_non_vars=Variables.separateVar(link)  
        var_names.extend(link_vars)
        ## ���
        header_vars, header_non_vars=Variables.separateVar(header)  
        var_names.extend(header_vars)
        ## ���̷ε�
        payloads_vars, payloads_non_vars=Variables.separateVar(payloads)  
        var_names.extend(payloads_vars)

        var_order=Variables.setVarOrder(var_names)  # ���� ��ȸ ���� ����

        iterator=Variables.stackVars(var_order)  # ��ȸ��
        for var_value in iterator:  # ��ȸ
            var_values={}

            for i in range(len(var_value)):
                var_values[var_order[i]]=var_value[i]

            new_link=Variables.rebuildText(link_vars, link_non_vars, var_values)
            new_header=Variables.rebuildText(header_vars, header_non_vars, var_values)
            new_payloads=Variables.rebuildText(payloads_vars, payloads_non_vars, var_values)
            yield new_link, new_header, new_payloads

    # �ؽ�Ʈ �� ���� �̸� �ν�
    def separateVar(text:str):
        var_names=[]  # ����
        var_name=""  # ���� �̸� �����
        non_var=[]  # 
        non_var_s=0  #

        ## ��ũ
        i=0
        while i<len(text):
            if text[i]=='{':
                if i+3<len(text) and text[i:i+3]=="{{$":  # ���� �̸� ����
                    i+=3
                    var_name=text[i]
            elif text[i]=='}':
                if i+1<len(text) and text[i+1]=='}':  # ���� �̸� ��
                    if var_name!="":
                        non_var.append(text[non_var_s:(i+1)-5-len(var_name)+1])  # (���� �̸��� ������ �ε���)-(��ȣ, $ ����)-(���� �̸� ���� ����)+(����)
                        # -> ������ �ƴ� �κ� ����
                        var_names.append(var_name)  # ���� �̸� ����
                        var_name=""  # �ʱ�ȭ
                        non_var_s=(i+1)+1  # ���� �̸� } ���κ� + ���� �ε���
                        # -> ���� ������ ����
            else:
                if var_name!="":  # ���� �̸� �Է���
                    var_name+=text[i]

            i+=1

        if non_var_s!=len(text):
            non_var.append(text[non_var_s:])

        return var_names, non_var

    # ���� ��ȸ ���� ����(link �� ����)
    def setVarOrder(var_names:list):
        var_names=deque(var_names)
        defined_var=set()
        var_order=[]

        while len(var_names):
            var_name=var_names.popleft()
            links=Variables.getLinks(var_name)

            if len(links)==0:  # ��ũ ����
                var_order.append(var_name)  # ������ ����
                defined_var.add(var_name)
            else:
                isbreaked=False
                for i in range(len(links)):
                    if not links[i] in defined_var:  # ��ũ�� ������ ���� �������� ����
                        isbreaked=True
                        break

                if isbreaked:
                    var_names.append(var_name)
                else:
                    var_order.append(var_name)  # ������ ����
                    defined_var.add(var_name)

        return var_order

    # �ٸ� ������ ����Ǿ� �ִ��� �˻�
    def getLinks(var_name:str):
        var_values=Global.projects_data[Global.main.last_highlighted_project]["variables"][var_name]  # ���� ���� �ҷ���/  �̸� : Ÿ��/��/������

        if var_values[2]=="":  # ������ ����
            links, tmp=Variables.separateVar(var_values[1])  # ���� ���� �ٸ� ������ ����Ǿ� �ִ��� �˻�
        else:  # ������ ����
            links, tmp=Variables.separateVar(var_values[2])  # ���� �������� �ٸ� ������ ����Ǿ� �ִ��� �˻�

        return links

    # ������ �ؽ�Ʈ ������
    def rebuildText(var_names:list, non_vars:list, var_value:dict):
        res=""

        for i in range(len(var_names)):
            res+=non_vars[i]
            res+=str(var_value[var_names[i]])

        if len(non_vars)>len(var_names):
            res+=non_vars[-1]

        return res


    # ��ü ���� ��ȸ
    def stackVars(var_order):
        var_value_stack=[]
        var_iterator_stack=[]

        while True:
            if len(var_value_stack)!=len(var_iterator_stack):  # ��ȸ�ڸ� �ְ� ������ ���� �ȳ���
                try:
                    var_value_stack.append(next(var_iterator_stack[-1]))  # ���� ���� ����
                except:  # ���� ���� ����! -> ���� ��ȸ ����
                    try:
                        var_value_stack.pop()  # �� ���� ������ ���� ��� ����
                        var_iterator_stack.pop()  # ��ȸ�� ���� ����
                    except:
                        return
            else:  # ���� ��ȸ�� ���� ����
                if len(var_value_stack)!=len(var_order):  # ��Ʈ �̿ϼ�
                    var_name=var_order[len(var_value_stack)]  # ���� ��ȸ�� ������ ���� �ҷ���
                    var_iterator_stack.append(Variables.traverseVar(var_name))  # ���� ��ȸ�� �߰�
                
                    var_value_stack.append(next(var_iterator_stack[-1]))  # ù ���� ���

                else:  # ��Ʈ �ϼ�
                    yield var_value_stack  # ��Ʈ ��ȯ

                    try:
                        var_value_stack.pop()  # ��Ʈ��
                    except:
                        return

    # ���� ���� ��ȸ
    def traverseVar(var_name):
        var_info=Global.projects_data[Global.main.last_highlighted_project]["variables"][var_name]
         
        #todo# ��ũ �� �����ϱ�
        if var_info[2]!="":  # ������ ����
            yield var_info[2]
        else:  # ������ ����
            ### ���� Ÿ��
            if var_info[0]=="Number":  ## �Ǽ�
                yield "error"
            elif var_info[0]=="List":  ## ����Ʈ
                for ret in var_info[1].split(','):    
                    yield ret
            elif var_info[0]=="String":  ## ���ڿ�
                yield "error"
            elif var_info[0]=="Hex":  ## 16����
                yield "error"


