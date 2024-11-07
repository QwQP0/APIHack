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
        ## 응답 테이블 구성
        self.resp_table=QBoxLayout(QBoxLayout.TopToBottom)  # 응답 테이블
        self.resp_table.setObjectName("resp_table")
        self.resp_table_label=QBoxLayout(QBoxLayout.LeftToRight)  # 테이블 라벨
        self.resp_table_label.addWidget(QLabel("*"))
        self.resp_table_label.addWidget(QLabel("No."))
        self.resp_table_label.addWidget(QLabel("Response Code"))
        self.resp_table_label.addWidget(QLabel("Bytes"))
        self.resp_table_label.addWidget(QLabel("Response Time"))
        self.resp_table.addLayout(self.resp_table_label)  # 테이블에 라벨 추가
        self.resp_tab_content.addLayout(self.resp_table, 5)  # 탭에 테이블 추가

        ## 필터 버튼 구성
        self.table_filter_btn=QPushButton("#")
        #self.table_filter_btn.clicked.connect()  # 필터 대화창 열기
        self.resp_tab_content.addWidget(self.table_filter_btn, 1)

    # 한 줄 추가(응답받은 거에서 가져오기)
    def addRow(self, response_time) -> QWidget:
        self.checked_row.append(False)

        row_widget=QWidget()  # 마우스 이벤트용 위젯
        row_widget.setObjectName(str(len(System.Global.responses)-1))  # 열떄 필요한 이름(보정 -1)

        row=QBoxLayout(QBoxLayout.LeftToRight, row_widget)
        row.addWidget(QCheckBox())
        row.itemAt(0).widget().checkStateChanged.connect(lambda :self.checkRow(row_widget))
        row.addWidget(QLabel(str(len(System.Global.responses))))
        row.addWidget(QLabel(str(System.Global.responses[-1].status_code)))
        row.addWidget(QLabel(str(len(System.Global.responses[-1].content))))
        row.addWidget(QLabel(str(response_time)))

        self.rightClickListener(row_widget).connect(lambda :self.initContextMenu(row_widget))
        self.resp_table.addWidget(row_widget)
        

    # 행 체크(체크박스 클릭 시)
    def checkRow(self, obj):
        print(obj)
        index=int(obj.findChild(QLabel).text())-1
        self.checked_row[index]= not self.checked_row[index]
        print(self.checked_row, any(self.checked_row))

    # 우클릭시 뜨는 메뉴 구성
    def initContextMenu(self, obj):
        for action in obj.actions():  # 우클릭 메뉴 초기화(전체 삭제)
            obj.removeAction(action)

        obj.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

        # 저장 액션
        save_action=QAction("Save", obj)
        save_action.triggered.connect(lambda :System.File.saveResponse(QInputDialog.getText\
            (self, "Response Save", "Input name", text=System.File.setNameAuto(), flags=Qt.WindowType.FramelessWindowHint)))
        obj.addAction(save_action)

        # 열기 액션
        open_action=QAction("Open", obj)
        open_action.triggered.connect(lambda :self.ResponseView(index=int(obj.objectName())))
        obj.addAction(open_action)
        if any(self.checked_row):  # 선택 항목 열기 액션
            open_selected_action=QAction("Open Selected", obj)
            open_selected_action.triggered.connect(self.openMultipleView)
            obj.addAction(open_selected_action)
        
        obj.addAction("").setSeparator(True)  # 구분선
        
        # 디코더로 보내기 액션
        send_decoder_action=QAction("Send To Decoder", obj)
        obj.addAction(send_decoder_action)

        # 비교자로 보내기 액션
        send_comparer_action=QAction("Send To Comparer", obj)
        obj.addAction(send_comparer_action)
        if any(self.checked_row):  # 선택 항목 비교자로 보내기 액션
            send_comparer_action=QAction("Send To Comparer Selected", obj)
            obj.addAction(send_comparer_action)

        obj.addAction("").setSeparator(True)  # 구분선

        # 삭제 액션
        delete_action=QAction("Delete", obj)
        delete_action.triggered.connect(lambda :self.deleteRow(obj))
        obj.addAction(delete_action)
        if any(self.checked_row):  # 선택 항목 삭제 액션
            delete_selected_action=QAction("Delete Selected", obj)
            obj.addAction(delete_selected_action)

            
    # 여러 창 열기
    def openMultipleView(self):
        for i in range(len(self.checked_row)):
            print(i, self.checked_row[i])
            if self.checked_row[i]:
                self.ResponseView(i)

    # 행 삭제
    def deleteRow(self, obj:QObject):
        obj.deleteLater()  # 가비지 컬렉팅
        obj.setParent(None)

                
#################### EventListener ####################

    # 우클릭
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

    # 응답 내용
    class ResponseView():
        def __init__(self, project_name:str=None, saved_name:str=None, index:int=-1):
            self.index=index
            self.initUI()  # UI 구성

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

            ### 헤더 그룹
            ## raw-pretty 스위치
            # raw 버튼
            self.switch=QHBoxLayout()
            self.raw_switch=QPushButton("raw")
            self.raw_switch.setCheckable(True)
            self.raw_switch.setChecked(True)  # raw 상태로 기본 설정
            self.raw_switch.clicked.connect(self.switching_raw)
            self.switch.addWidget(self.raw_switch)
            # pretty 버튼
            self.pretty_switch=QPushButton("pretty")
            self.pretty_switch.setCheckable(True)
            self.pretty_switch.clicked.connect(self.switching_pretty)
            self.switch.addWidget(self.pretty_switch)

            self.header_div.addLayout(self.switch)  # 헤더 그룹에 스위치 추가

            ## 디코더로 보내기 버튼
            self.decoder_btn=QPushButton("Decoder")
            self.header_div.addWidget(self.decoder_btn)

            ## 비교자로 보내기 버튼
            self.comparer_btn=QPushButton("Comparer")
            self.header_div.addWidget(self.comparer_btn)

            ## 닫기 버튼
            self.close_btn=QPushButton("X")
            self.close_btn.clicked.connect(self.dialog.close)
            self.header_div.addWidget(self.close_btn)

            ### 바디 그룹
            self.contents=QTextEdit()
            self.contents.setReadOnly(True)  # 읽기 전용
            self.body_div.addWidget(self.contents)

            ### 전체 창
            self.window=QVBoxLayout()
            self.window.addLayout(self.header_div)
            self.window.addLayout(self.body_div)
            self.dialog.setLayout(self.window)
            self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            self.dialog.setFixedSize(1280, 720)

            # 드래그 이벤트 연결
            self.dialog.mousePressEvent=self.mousePressEvent
            self.dialog.mouseMoveEvent=self.mouseMoveEvent
            self.dialog.mouseReleaseEvent=self.mouseReleaseEvent
            
            # 실행
            self.dialog.show()
            self.dialog.destroyed.connect(lambda : print("close"))  # 닫을 때 close 출력


        def switching_raw(self):
            if self.raw_switch.isChecked():
                return

            # 포커스 변경
            self.raw_switch.setChecked(True)
            self.pretty_switch.setChecked(False)

            self.contents.setPlainText(self.contents.toPlainText())  # 텍스트 입력

        def switching_pretty(self):
            if self.pretty_switch.isChecked():
                return

            # 포커스 변경
            self.raw_switch.setChecked(False)
            self.pretty_switch.setChecked(True)

            self.contents.setPlainText(self.contents.toPlainText())  # 텍스트 입력

        ## 창 드래그
        def mousePressEvent(self, event: QMouseEvent) -> None:
            self.mouse_start_postion=event.globalPos()  # 클릭 위치 저장
            self.widget_position=self.dialog.pos()  # 창 위치 저장
        def mouseMoveEvent(self, event: QMouseEvent) -> None:
            if self.mouse_start_postion!=None:  # 클릭 되어있을 때
                # 계속 드래그
                self.dialog.move(self.widget_position.x()+event.globalPos().x()-self.mouse_start_postion.x(), \
                    self.widget_position.y()+event.globalPos().y()-self.mouse_start_postion.y())
        def mouseReleaseEvent(self, event: QMouseEvent) -> None:
            self.mouse_start_postion=None








