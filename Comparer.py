#################### Imports ####################


from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout



##################### Main ######################



class Comparer:
    def __init__(self, parent):
        self.comparer_tab_content=QHBoxLayout(parent)

        self.initUI()  # UI ����

    # �⺻ UI ����
    def initUI(self):
        ## UI ����
        # �Է� ���� 1
        input_div_1=QVBoxLayout()
        input_field_1=QTextEdit()  # �Է� ĭ
        label_div_1=QHBoxLayout()
        name_label_1=QLabel("name 1")  # �̸� ��  #debug#�ؽ�Ʈ �����
        length_label_1=QLabel("0 byte")  # ���� ��
        # �Է� ���� 2
        input_div_2=QVBoxLayout()
        input_field_2=QTextEdit()  # �Է� ĭ
        label_div_2=QHBoxLayout()
        name_label_2=QLabel("name 2")  # �̸� ��  #debug#�ؽ�Ʈ �����
        length_label_2=QLabel("0 byte")  # ���� ��

        ## UI ����
        # �Է� ���� 1
        input_div_1.addLayout(label_div_1)
        input_div_1.addWidget(input_field_1)
        label_div_1.addWidget(name_label_1)
        label_div_1.addWidget(length_label_1)
        # �Է� ���� 2
        input_div_2.addLayout(label_div_2)
        input_div_2.addWidget(input_field_2)
        label_div_2.addWidget(length_label_2)
        label_div_2.addWidget(name_label_2)

        self.comparer_tab_content.addLayout(input_div_1)
        self.comparer_tab_content.addLayout(input_div_2)

        #todo#Ʈ���� ����

        return

        

