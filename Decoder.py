#################### Imports ####################

import base64
import System

from PySide6.QtWidgets import QBoxLayout, QComboBox, QLabel, QPushButton, QTextEdit

###################### Main #####################

class Decoder():
    def __init__(self, parent):
        self.sequence_text_list=[]
        self.sequence_fuction_list=[]
        
        self.decoder_tab_content=QBoxLayout(QBoxLayout.TopToBottom, parent)
        self.initUI()

    def initUI(self):
        self.decoder_tab_content.addLayout(self.initInput(1))  # �Է� ���� �߰�
        self.crt_seq_btn=QPushButton("+")
        self.crt_seq_btn.clicked.connect(lambda: self.addSequence(len(self.sequence_text_list)+1))
        self.decoder_tab_content.addWidget(self.crt_seq_btn)

        self.addSequence(2)

    # ���� �߰�( + ��ư )
    def addSequence(self, seq_num):
        self.decoder_tab_content.insertLayout((seq_num-1)*2-1, self.initFunction(seq_num))  # ��� ���� �߰�
        self.decoder_tab_content.insertLayout((seq_num-1)*2, self.initInput(seq_num))  # �Է� ���� �߰�

    # �Է� ������ �߰�
    def initInput(self, seq_num):
        sequence_div=QBoxLayout(QBoxLayout.LeftToRight)
        sequence_div.addWidget(QLabel(str(seq_num)))

        if len(self.sequence_text_list)==0 or self.sequence_text_list[-1]=="":  # ù���� �Է� ������ or ���� �Է� ������ �������
            self.sequence_text_list.append("")
            sequence_div.addWidget(QTextEdit(""))  # ����ִ� �Է� �������� ����
            
        else:
            self.sequence_fuction_list.append(System.CONST.DECODER_DEFAULT_FUNCTION)
            self.sequence_text_list.append(\
                        getattr(self.Transformer, System.CONST.DECODER_DEFAULT_FUNCTION[0].name+"To"+System.CONST.DECODER_DEFAULT_FUNCTION[1].name)\
                        (self.sequence_text_list[-1]))  # ���� �ؽ�Ʈ ��ȯ
            sequence_div.addWidget(QTextEdit(self.sequence_text_list[-1]))  # �Է� ���� ����
            
        sequence_div.itemAt(1).widget().textChanged.connect(lambda: self.whenInputChanges(sequence_div, sequence_div.itemAt(1).widget().text()))
        # -> �ؽ�Ʈ ���� �� Ʈ���ŵǴ� �Լ� ����

        return sequence_div

    # ��� ������ �߰�
    def initFunction(self, seq_num):
        function_div=QBoxLayout(QBoxLayout.LeftToRight)
        function_mode=QComboBox()  # ���: ���ڵ�/���ڵ�
        for mode in System.CONST.DECODER_MODE:
            function_mode.addItem(mode.name)  # �߰�
        function_mode.currentTextChanged.connect(lambda: self.whenFunctionChanges(function_div, function_mode.currentText(), function_crypt.currentText()))

        function_crypt=QComboBox()  # ��ȣȭ
        for crypt in System.CONST.DECODER_CRYPT:
            function_crypt.addItem(crypt.name)  # �߰�
        function_crypt.currentTextChanged.connect(lambda: self.whenFunctionChanges(function_div, function_mode.currentText(), function_crypt.currentText()))

        function_div.addWidget(function_mode)
        function_div.addWidget(QLabel(" to "))
        function_div.addWidget(function_crypt)

        self.sequence_fuction_list.append(System.CONST.DECODER_DEFAULT_FUNCTION)

        return function_div

    # �Է� ���� ���� �� Ʈ����
    def whenInputChanges(self, touched_object:QBoxLayout, text:str):
        children=self.decoder_tab_content.children()  # �Է� ����, ��� ���� ����Ʈ
        triggered=False

        print(self.sequence_text_list)
        print(self.sequence_fuction_list)

        for i in range(0, len(children), 2):
            if touched_object==children[i]:  # ��� ������ �Է� ���� �϶�
                self.sequence_text_list[i//2]=text
                triggered=True
            else:
                if triggered:
                    self.sequence_text_list[i//2]=\
                        getattr(self.Transformer, self.sequence_fuction_list[i//2-1][0].name+"To"+self.sequence_fuction_list[i//2-1][1].name)\
                        (self.sequence_text_list[i//2-1])  # ���� �ؽ�Ʈ ��ȯ
                    children[i].itemAt(1).widget().setText(self.sequence_text_list[i//2])  # �ؽ�Ʈ ����
                else:
                    # disable_sequences(touched_object)  �� ���� ���� ��Ȱ��ȭ �ϱ�
                    pass


    # ��� ���� ���� �� Ʈ����
    def whenFunctionChanges(self, touched_object:QBoxLayout, mode:str, crypt:str):
        children=self.decoder_tab_content.children()  # �Է� ����, ��� ���� ����Ʈ
        triggered=False

        print(self.sequence_text_list)
        print(self.sequence_fuction_list)

        for i in range(1, len(children), 2):
            if touched_object==children[i] or triggered:  # ��� ������ ��� ���� �϶�
                print(i, 'asdfefefe')
                triggered=True
                
                self.sequence_fuction_list[i//2-1]=[System.CONST.DECODER_MODE[children[i].itemAt(0).widget().currentText()], System.CONST.DECODER_CRYPT[children[i].itemAt(2).widget().currentText()]]
                # -> �Լ� ����
                self.sequence_text_list[(i+1)//2]=\
                    getattr(self.Transformer, self.sequence_fuction_list[i//2-1][0].name+"To"+self.sequence_fuction_list[i//2-1][1].name)\
                    (self.sequence_text_list[(i-1)//2])  # ���� �ؽ�Ʈ�� ��ȯ
                children[i+1].itemAt(1).widget().setText(str(self.sequence_text_list[(i+1)//2]))  # �ؽ�Ʈ ����

        print(self.sequence_text_list)
        print(self.sequence_fuction_list)

    class Transformer:
        def ENCODEToBASE_64(strr:str):
            return base64.b64encode(strr.encode("UTF-8")).decode("UTF-8")
        def DECODEToBASE_64(strr:str):
            return base64.b64decode(strr.encode("UTF-8")+ b'=' * (-len(strr) % 4)).decode("UTF-8")





