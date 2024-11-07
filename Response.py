#################### Imports ####################

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QAction, QMouseEvent
from PySide6.QtWidgets import QBoxLayout, QCheckBox, QHBoxLayout, QInputDialog, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

import System



###################### Main #####################

class Response():
    def __init__(self, parent):
        self.checked_row=[]

        self.resp_tab_content=QBoxLayout(QBoxLayout.LeftToRight, parent)
        self.resp_tab_content.setObjectName("resp_tab_content")
        self.initUI()


    def initUI(self):
        ## ���� ���̺� ����
        self.resp_table=QBoxLayout(QBoxLayout.TopToBottom)  # ���� ���̺�
        self.resp_table.setObjectName("resp_table")
        self.resp_table_label=QBoxLayout(QBoxLayout.LeftToRight)  # ���̺� ��
        self.resp_table_label.addWidget(QLabel("*"))
        self.resp_table_label.addWidget(QLabel("No."))
        self.resp_table_label.addWidget(QLabel("Response Code"))
        self.resp_table_label.addWidget(QLabel("Bytes"))
        self.resp_table_label.addWidget(QLabel("Response Time"))
        self.resp_table.addLayout(self.resp_table_label)  # ���̺� �� �߰�
        self.resp_tab_content.addLayout(self.resp_table, 5)  # �ǿ� ���̺� �߰�

        ## ���� ��ư ����
        self.table_filter_btn=QPushButton("#")
        #self.table_filter_btn.clicked.connect()  # ���� ��ȭâ ����
        self.resp_tab_content.addWidget(self.table_filter_btn, 1)

    # �� �� �߰�(������� �ſ��� ��������)
    def addRow(self, response_time) -> QWidget:
        self.checked_row.append(False)

        row_widget=QWidget()  # ���콺 �̺�Ʈ�� ����
        row_widget.setObjectName(str(len(System.Global.responses)-1))  # ���� �ʿ��� �̸�(���� -1)

        row=QBoxLayout(QBoxLayout.LeftToRight, row_widget)
        row.addWidget(QCheckBox())
        row.itemAt(0).widget().checkStateChanged.connect(lambda :self.checkRow(row_widget))
        row.addWidget(QLabel(str(len(System.Global.responses))))
        row.addWidget(QLabel(str(System.Global.responses[-1].status_code)))
        row.addWidget(QLabel(str(len(System.Global.responses[-1].content))))
        row.addWidget(QLabel(str(response_time)))

        self.rightClickListener(row_widget).connect(lambda :self.initContextMenu(row_widget))
        self.resp_table.addWidget(row_widget)
        

    # �� üũ(üũ�ڽ� Ŭ�� ��)
    def checkRow(self, obj):
        print(obj)
        index=int(obj.findChild(QLabel).text())-1
        self.checked_row[index]= not self.checked_row[index]
        print(self.checked_row, any(self.checked_row))

    # ��Ŭ���� �ߴ� �޴� ����
    def initContextMenu(self, obj):
        for action in obj.actions():  # ��Ŭ�� �޴� �ʱ�ȭ(��ü ����)
            obj.removeAction(action)

        obj.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

        # ���� �׼�
        save_action=QAction("Save", obj)
        save_action.triggered.connect(lambda :System.File.saveResponse(QInputDialog.getText\
            (self, "Response Save", "Input name", text=System.File.setNameAuto(), flags=Qt.WindowType.FramelessWindowHint)))
        obj.addAction(save_action)

        # ���� �׼�
        open_action=QAction("Open", obj)
        open_action.triggered.connect(lambda :self.ResponseView(index=int(obj.objectName())))
        obj.addAction(open_action)
        if any(self.checked_row):  # ���� �׸� ���� �׼�
            open_selected_action=QAction("Open Selected", obj)
            open_selected_action.triggered.connect(self.openMultipleView)
            obj.addAction(open_selected_action)
        
        obj.addAction("").setSeparator(True)  # ���м�
        
        # ���ڴ��� ������ �׼�
        send_decoder_action=QAction("Send To Decoder", obj)
        obj.addAction(send_decoder_action)

        # ���ڷ� ������ �׼�
        send_comparer_action=QAction("Send To Comparer", obj)
        obj.addAction(send_comparer_action)
        if any(self.checked_row):  # ���� �׸� ���ڷ� ������ �׼�
            send_comparer_action=QAction("Send To Comparer Selected", obj)
            obj.addAction(send_comparer_action)

        obj.addAction("").setSeparator(True)  # ���м�

        # ���� �׼�
        delete_action=QAction("Delete", obj)
        delete_action.triggered.connect(lambda :self.deleteRow(obj))
        obj.addAction(delete_action)
        if any(self.checked_row):  # ���� �׸� ���� �׼�
            delete_selected_action=QAction("Delete Selected", obj)
            obj.addAction(delete_selected_action)

            
    # ���� â ����
    def openMultipleView(self):
        for i in range(len(self.checked_row)):
            print(i, self.checked_row[i])
            if self.checked_row[i]:
                self.ResponseView(i)

    # �� ����
    def deleteRow(self, obj:QObject):
        obj.deleteLater()  # ������ �÷���
        obj.setParent(None)

                
#################### EventListener ####################

    # ��Ŭ��
    def rightClickListener(self, widget) -> Signal:
        class Filter(QObject):
            clicked = Signal()

            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
                    self.clicked.emit()
                return super().eventFilter(obj, event)

        right_click_filter = Filter(widget)
        widget.installEventFilter(right_click_filter)
        return right_click_filter.clicked


####################### Dialog #######################

    # ���� ����
    class ResponseView():
        def __init__(self, project_name:str=None, saved_name:str=None, index:int=-1):
            self.index=index
            self.initUI()  # UI ����

            if self.index==-1:
                self.project_name=project_name
                self.saved_name=saved_name
                self.project_path=System.Global.projects_data[project_name]["last_path"]
                saved_data=open(self.project_path+'/'+self.project_name+'/saved/'+self.saved_name+".rsv")
                self.contents.setPlainText(saved_data.read())
                saved_data.close()
            else:
                self.contents.setPlainText(System.Global.responses[self.index].text)


        def initUI(self):
            self.dialog=QWidget()
            self.header_div=QHBoxLayout()
            self.body_div=QHBoxLayout()

            ### ��� �׷�
            ## raw-pretty ����ġ
            # raw ��ư
            self.switch=QHBoxLayout()
            self.raw_switch=QPushButton("raw")
            self.raw_switch.setCheckable(True)
            self.raw_switch.setChecked(True)  # raw ���·� �⺻ ����
            self.raw_switch.clicked.connect(self.switching_raw)
            self.switch.addWidget(self.raw_switch)
            # pretty ��ư
            self.pretty_switch=QPushButton("pretty")
            self.pretty_switch.setCheckable(True)
            self.pretty_switch.clicked.connect(self.switching_pretty)
            self.switch.addWidget(self.pretty_switch)

            self.header_div.addLayout(self.switch)  # ��� �׷쿡 ����ġ �߰�

            ## ���ڴ��� ������ ��ư
            self.decoder_btn=QPushButton("Decoder")
            self.header_div.addWidget(self.decoder_btn)

            ## ���ڷ� ������ ��ư
            self.comparer_btn=QPushButton("Comparer")
            self.header_div.addWidget(self.comparer_btn)

            ## �ݱ� ��ư
            self.close_btn=QPushButton("X")
            self.close_btn.clicked.connect(self.dialog.close)
            self.header_div.addWidget(self.close_btn)

            ### �ٵ� �׷�
            self.contents=QTextEdit()
            self.contents.setReadOnly(True)  # �б� ����
            self.body_div.addWidget(self.contents)

            ### ��ü â
            self.window=QVBoxLayout()
            self.window.addLayout(self.header_div)
            self.window.addLayout(self.body_div)
            self.dialog.setLayout(self.window)
            self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            self.dialog.setFixedSize(1280, 720)

            # �巡�� �̺�Ʈ ����
            self.dialog.mousePressEvent=self.mousePressEvent
            self.dialog.mouseMoveEvent=self.mouseMoveEvent
            self.dialog.mouseReleaseEvent=self.mouseReleaseEvent
            
            # ����
            self.dialog.show()
            self.dialog.destroyed.connect(lambda : print("close"))  # ���� �� close ���


        def switching_raw(self):
            if self.raw_switch.isChecked():
                return

            # ��Ŀ�� ����
            self.raw_switch.setChecked(True)
            self.pretty_switch.setChecked(False)

            self.contents.setPlainText(self.contents.toPlainText())  # �ؽ�Ʈ �Է�

        def switching_pretty(self):
            if self.pretty_switch.isChecked():
                return

            # ��Ŀ�� ����
            self.raw_switch.setChecked(False)
            self.pretty_switch.setChecked(True)

            self.contents.setPlainText(self.contents.toPlainText())  # �ؽ�Ʈ �Է�

        ## â �巡��
        def mousePressEvent(self, event: QMouseEvent) -> None:
            self.mouse_start_postion=event.globalPos()  # Ŭ�� ��ġ ����
            self.widget_position=self.dialog.pos()  # â ��ġ ����
        def mouseMoveEvent(self, event: QMouseEvent) -> None:
            if self.mouse_start_postion!=None:  # Ŭ�� �Ǿ����� ��
                # ��� �巡��
                self.dialog.move(self.widget_position.x()+event.globalPos().x()-self.mouse_start_postion.x(), \
                    self.widget_position.y()+event.globalPos().y()-self.mouse_start_postion.y())
        def mouseReleaseEvent(self, event: QMouseEvent) -> None:
            self.mouse_start_postion=None








