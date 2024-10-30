#################### Imports ####################


from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout



##################### Main ######################



class Comparer:
    def __init__(self, parent):
        self.comparer_tab_content=QHBoxLayout(parent)

        self.initUI()  # UI 구성

    # 기본 UI 구성
    def initUI(self):
        ## UI 생성
        # 입력 구역 1
        input_div_1=QVBoxLayout()
        input_field_1=QTextEdit()  # 입력 칸
        label_div_1=QHBoxLayout()
        name_label_1=QLabel("name 1")  # 이름 라벨  #debug#텍스트 지우기
        length_label_1=QLabel("0 byte")  # 길이 라벨
        # 입력 구역 2
        input_div_2=QVBoxLayout()
        input_field_2=QTextEdit()  # 입력 칸
        label_div_2=QHBoxLayout()
        name_label_2=QLabel("name 2")  # 이름 라벨  #debug#텍스트 지우기
        length_label_2=QLabel("0 byte")  # 길이 라벨

        ## UI 조립
        # 입력 구역 1
        input_div_1.addLayout(label_div_1)
        input_div_1.addWidget(input_field_1)
        label_div_1.addWidget(name_label_1)
        label_div_1.addWidget(length_label_1)
        # 입력 구역 2
        input_div_2.addLayout(label_div_2)
        input_div_2.addWidget(input_field_2)
        label_div_2.addWidget(length_label_2)
        label_div_2.addWidget(name_label_2)

        self.comparer_tab_content.addLayout(input_div_1)
        self.comparer_tab_content.addLayout(input_div_2)

        #todo#트리거 연결

        return

        

