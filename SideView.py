#################### Imports ####################


import os
import shutil
from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QHBoxLayout, QInputDialog, QLabel, QMenu, QMessageBox, QPushButton, QVBoxLayout

from System import Global, File, deleteObject



##################### Main ######################




class SideView():
	def __init__(self):
		self.side_view_content=QHBoxLayout()
		self.right_click_mouse_pos=None
		self.last_left_clicked_object:QLabel=None
		self.last_right_clicked_object:QLabel=None

		self.initUI()

		return


	## UI 구성
	# 기본 UI 구성
	def initUI(self, project_name:str=None, request_name:str=None):
		if project_name==None:  # 기본 UI 구성
			# 오브젝트 선언
			self.side_view_list=QVBoxLayout()
			self.hide_btn=QPushButton("<")

			# UI 구성
			self.side_view_content.addLayout(self.side_view_list)  # 목록 구역 조립
			self.side_view_content.addWidget(self.hide_btn)  # 숨김 버튼 조립

			# 이벤트 연결
			self.hide_btn.clicked.connect(self.onClickHide)
		else:  # 프로젝트 데이터 기반 UI 구성
			## 프로젝트 라벨
			self.initProjectLabel(project_name, self.side_view_list.count())  # 끝부분에 삽입(방금 연 프로젝트이므로)
			## 요청 라벨
			self.initRequestsLabel(project_name, self.side_view_list.count())  # 끝부분에 삽입(방금 연 프로젝트이므로)
			## 저장 폴더 라벨
			self.initSaveFolderLabel(project_name, self.side_view_list.count())  # 끝부분에 삽입(방금 연 프로젝트이므로)
			## 저장 파일 라벨
			self.initSaveFilesLabel(project_name, self.side_view_list.count())  # 끝부분에 삽입(방금 연 프로젝트이므로)

		return
	# 프로젝트 라벨삽입
	def initProjectLabel(self, project_name:str, index:int):
		self.initLabel(project_name, "open", index, "p")

		return
	# 요청 라벨 삽입
	def initRequestsLabel(self, project_name:str, index:int):
		for request_name in list(Global.projects_data[project_name]["requests"].keys()):
			self.initLabel(request_name, project_name, index, "q")
			index+=1  # 삽입 지점 변경

		return
	# 저장 폴더 라벨 삽입
	def initSaveFolderLabel(self, project_name:str, index:int):
		self.initLabel("saved", project_name+"/open", index, "f")

		return
	# 저장 파일 라벨 삽입
	def initSaveFilesLabel(self, project_name:str, index:int):
		save_file_names=[]
		for save_files in os.walk(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved"):  # 세이브 폴더 하위 파일 탐색
			save_file_names.extend(save_files[2])  # 이름 저장

		for i in range(len(save_file_names)):
			save_file_name=save_file_names[i].split('.')
			extension=save_file_name[-1]  # 확장자
			save_file_name='.'.join(save_file_name[:len(save_file_name)-1])  # 파일 이름(확장자 제외)

			if extension=="rsv":
				self.initLabel(save_file_name, project_name+"/saved", index, "s")
				index+=1  # 다음 삽입 지점 변경

		return
	# 라벨 삽입
	def initLabel(self, text:str, tag:str, index:int, label_type:str):
		new_label=QLabel(text)  # 텍스트 설정
		new_label.setObjectName(tag)  # 태그 설정

		## 이벤트 설정
		# 좌클릭
		if label_type=="p":  # 프로젝트
			self.leftClickListener(new_label).connect(self.viewSubItems)
		elif label_type=="q":  # 요청
			self.leftClickListener(new_label).connect(lambda: Global.main.loadProject(new_label.objectName(), new_label.text()))
		elif label_type=="f":  # 저장 폴더
			self.leftClickListener(new_label).connect(self.viewSubItems)
		elif label_type=="s":  # 저장 파일
			self.leftClickListener(new_label).connect(self.viewSaveFile)
		# 우클릭
		self.rightClickListener(new_label).connect(self.viewContextMenu)

		self.side_view_list.insertWidget(index, new_label)  # 라벨 삽입

		return


	### 이벤트, 상호작용
	## 좌클릭 상호작용
	# 접기/열기: 프로젝트, 저장 폴더
	def viewSubItems(self, obj:QLabel=None):
		if obj==None:
			obj=self.last_left_clicked_object

		if obj.text()!="saved":  # 프로젝트(저장 폴더 아님)
			if obj.objectName()=="open":  # 열려있음
				s, n=self.getLabelIndexByPj(obj.text())

				# 프로젝트 하위 라벨 삭제
				for i in range(n-1):  # -1: 프로젝트 라벨 제외
					print(i, self.side_view_list.itemAt(s+1).widget())
					deleteObject(self.side_view_list.itemAt(s+1).widget())

				obj.setObjectName("close")
			else:  # 닫혀있음
				s, n=self.getLabelIndexByPj(obj.text())
				self.initRequestsLabel(obj.text(), s+1)  # 요청 라벨(프로젝트 라벨 바로 다음에 삽입)
				s, n=self.getLabelIndexByPj(obj.text())
				self.initSaveFolderLabel(obj.text(), s+n)  # 저장 폴더 라벨
				self.initSaveFilesLabel(obj.text(), s+n+1)  # 저장 파일 라벨

				self.focusLabel(Global.cur_project_name, Global.cur_request_name)  # 하이라이트 적용(기존 하이라이트가 지워졌을 수 있으므로)

				obj.setObjectName("open")
		else:
			if obj.objectName().split('/')[1]=="open":  # 열려있음
				s, n=self.getLabelIndexByPj(obj.objectName().split('/')[0])

				for i in range(s+n-1, s, -1):  # 뒤에서부터 탐색
					if self.side_view_list.itemAt(i).widget().objectName().split('/')[1]=="saved":
						deleteObject(self.side_view_list.itemAt(i).widget())
					else:  # 저장 파일 라벨이 아니면 중단
						break
				
				obj.setObjectName(obj.objectName().split('/')[0]+"/close")
			else:  # 닫혀있음
				self.initSaveFilesLabel(obj.objectName().split('/')[0], self.getLabelIndexByText(obj.text(), obj.objectName()))

				obj.setObjectName(obj.objectName().split('/')[0]+"/open")

		return
	# 저장 파일 팝업: 저장 파일
	def viewSaveFile(self):
		return
	## 우클릭 상호작용
	# 우클릭 메뉴 집합
	def viewContextMenu(self):
		menu=QMenu(self.last_right_clicked_object, self.right_click_mouse_pos)

		if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트
			# 새 요청 생성
			create_request_action=QAction("New Request")
			create_request_action.triggered.connect(self.newRequest)
			menu.addAction(create_request_action)
			# 프로젝트 이름 변경
			rename_project_action=QAction("Rename")
			rename_project_action.triggered.connect(self.rename)
			menu.addAction(rename_project_action)
			# 프로젝트 닫기
			close_project_action=QAction("Close Project")
			close_project_action.triggered.connect(self.closeProject)
			menu.addAction(close_project_action)
			# 프로젝트 삭제
			delete_project_action=QAction("Delete")
			delete_project_action.triggered.connect(self.delete)
			menu.addAction(delete_project_action)
		elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # 요청
			# 요청 이름 변경
			rename_request_action=QAction("Rename")
			rename_request_action.triggered.connect(self.rename)
			menu.addAction(rename_request_action)
			# 요청 복제
			duplicate_request_action=QAction("Duplicate")
			duplicate_request_action.triggered.connect(self.duplicate)
			menu.addAction(duplicate_request_action)
			# 요청 삭제
			delete_request_action=QAction("Delete")
			delete_request_action.triggered.connect(self.delete)
			menu.addAction(delete_request_action)
		elif self.last_right_clicked_object.objectName().split('/')[1]=="saved":  # 저장된 응답
			# 응답 이름 변경
			rename_save_action=QAction("Rename")
			rename_save_action.triggered.connect(self.rename)
			menu.addAction(rename_save_action)
			# 응답 복제
			duplicate_save_action=QAction("Duplicate")
			duplicate_save_action.triggered.connect(self.duplicate)
			menu.addAction(duplicate_save_action)
			# 응답 삭제
			delete_save_action=QAction("Delete")
			delete_save_action.triggered.connect(self.delete)
			menu.addAction(delete_save_action)
		else:  # 저장 폴더
			# 저장한 응답 전체 삭제
			delete_all_save_action=QAction("Delete All")
			delete_all_save_action.triggered.connect(self.deleteAllSave)
			menu.addAction(delete_all_save_action)
		
		menu.exec(self.right_click_mouse_pos)

		return
	# 새 요청 생성: 프로젝트
	def newRequest(self):
		new_request_dialog=QInputDialog()

		name, ok=new_request_dialog.getText(Global.main, "", "New Request", text=File.setNameAuto("", self.last_right_clicked_object.text(), 'q'), flags=Qt.WindowType.FramelessWindowHint)

		#todo# 요청 이름 겹치는 지 확인

		if ok:
			if self.last_right_clicked_object.objectName()=="close":  # 프로젝트 접혀 있음
				self.viewSubItems(self.last_right_clicked_object)  # 프로젝트 열기

			i=self.getLabelIndexByText("saved", self.last_right_clicked_object.text()+"/open")  # 클릭한 프로젝트의 저장 폴더 라벨의 인덱스 불러옴
			
			Global.projects_data[self.last_right_clicked_object.text()]["requests"][name]={}  #todo#기본 요청 정보 저장

			self.initLabel(name, self.last_right_clicked_object.text(), i, "q")  # 라벨 삽입
			
		Global.main.loadProject(self.last_right_clicked_object.text(), name)  # 요청 로드

		return
	# 이름 바꾸기: 프로젝트, 요청, 저장 파일
	def rename(self):
		rename_dialog=QInputDialog()

		if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트 일 때
			name, ok=rename_dialog.getText(Global.main, "", "Rename Project", flags=Qt.WindowType.FramelessWindowHint)
		else:
			name, ok=rename_dialog.getText(Global.main, "", "Rename", flags=Qt.WindowType.FramelessWindowHint)

		#todo# 이름 겹치는 지 확인(경로/이름 <-이 존재하는지)

		if ok:
			if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트
				Global.projects_data[name]=Global.projects_data[self.last_right_clicked_object.text()]  # 데이터 복제
				shutil.move(Global.projects_data[name]["last_path"]+'/'+self.last_right_clicked_object.text(), Global.projects_data[name]["last_path"]+'/'+name)  # 프로젝트 폴더 이름변경
				shutil.move(Global.projects_data[name]["last_path"]+'/'+name+'/'+self.last_right_clicked_object.text()+".ahp", Global.projects_data[name]["last_path"]+'/'+name+'/'+name+".ahp")
				# -> 프로젝트 파일 이름 변경
				del Global.projects_data[self.last_right_clicked_object.text()]  # 원본 데이터 삭제

				# 사이드 뷰의 하위 요소(요청, 저장 폴더, 저장 파일) objectName 변경하기
				s, n=self.getLabelIndexByPj(self.last_right_clicked_object.text())

				for i in range(s+1, n-1):  # +1, -1: 프로젝트 라벨 제외
					obj=self.side_view_list.itemAt(i).widget()

					# objectName 변경
					if len(obj.objectName().split('/'))==1:
						obj.setObjectName(name)
					else:
						obj.setObjectName(name+"/"+obj.objectName().split('/')[1])
			elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # 요청
				project_name=self.last_right_clicked_object.objectName()  # 오브젝트 이름에서 프로젝트 이름 가져오기

				Global.projects_data[project_name]["requests"][name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]  # 데이터 복제
				del Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]  # 원본 데이터 삭제
			else:  # 저장 파일
				project_name=self.last_right_clicked_object.objectName().split('/')[0]  # 오브젝트 이름에서 프로젝트 이름 가져오기

				shutil.move(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+self.last_right_clicked_object.text()+'.rsv', \
					Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+name+'.rsv')  # 저장된 파일 이름 변경

			self.last_right_clicked_object.setText(name)  # 사이드 뷰의 오브젝트 이름 변경

		else:
			print("cancel")

		return
	# 복제: 요청, 저장 파일
	def duplicate(self):
		if len(self.last_right_clicked_object.objectName().split('/'))==1:  # 요청
			project_name=self.last_right_clicked_object.objectName()
			new_request_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 'q')

			# 새 요청 생성
			Global.projects_data[project_name]["requests"][new_request_name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]
			# -> 데이터 복제
			
			insert_pos=self.side_view_list.indexOf(self.last_right_clicked_object)+1
			self.initLabel(new_request_name, project_name, insert_pos, "q")  # 요청 라벨 삽입

			Global.main.loadProject(project_name, new_request_name)
		else:  # 저장 파일
			project_name=self.last_right_clicked_object.objectName().split('/')[0]
			project_path=Global.projects_data[project_name]['last_path']+'/'+project_name
			new_file_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 's')

			shutil.copy(project_path+"/saved/"+self.last_right_clicked_object.text()+".rsv", project_path+"/saved/"+new_file_name+".rsv")  # 저장 파일 복제
			
			insert_pos=self.side_view_list.indexOf(self.last_right_clicked_object)+1
			self.initLabel(new_file_name, project_name+"/saved", insert_pos, "s")  # 요청 라벨 삽입

		return
	# 삭제: 프로젝트, 요청, 저장 파일
	def delete(self):
		if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # 프로젝트
			are_you_sure=QMessageBox()
			are_you_sure.setText("Delete Project File?")
			are_you_sure.setStandardButtons(QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.No|QMessageBox.StandardButton.Yes)
			answer=are_you_sure.exec()

			if answer!=QMessageBox.StandardButton.Cancel:
				if answer==QMessageBox.StandardButton.Yes:  # 파일까지 삭제 선택
					print(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())
					shutil.rmtree(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())  # 프로젝트 폴더 삭제

				del Global.projects_data[self.last_right_clicked_object.text()]  # 프로젝트 데이터 삭제

				# 프로젝트 라벨과 하위 라벨 삭제
				s, n=self.getLabelIndexByPj(self.last_right_clicked_object.text())
				for i in range(s, n):
					deleteObject(self.side_view_list.itemAt(s).widget())
		elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # 요청
			project_name=self.last_right_clicked_object.objectName()  # 프로젝트 이름 가져오기
			request_name=self.last_right_clicked_object.text()  # 요청 이름 가져오기

			del Global.projects_data[project_name]["requests"][request_name]  # 요청 데이터 삭제

			#todo#  현재 탭이 Request이고 삭제한 요청이 열려있는 상태일때 탭 전환
			#todo#  각 프로젝트에서 요청 최소 1개씩은 남길 것
			
			deleteObject(self.last_right_clicked_object)  # 사이드 뷰에서 요청 라벨 삭제
		else:  # 저장 파일
			project_name=self.last_right_clicked_object.objectName().split('/')[0]  # 프로젝트 이름 가져오기
			file_name=self.last_right_clicked_object.text()  # 저장된 응답 이름 가져오기

			os.remove(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+file_name+".rsv")  # 저장된 파일 삭제

			#todo#  해당 응답이 팝업 상태로 열려있을 떄 종료
			
			deleteObject(self.last_right_clicked_object)  # 사이드 뷰에서 저장 파일 라벨 삭제

		return
	# 닫기: 프로젝트
	def closeProject(self):
		del Global.projects_data[self.last_right_clicked_object.text()]  # 프로젝트 데이터 삭제

		# 프로젝트 라벨과 하위 라벨 삭제
		s, n=self.getLabelIndexByPj(self.last_right_clicked_object.text())
		for i in range(s, n):
			deleteObject(self.side_view_list.itemAt(s).widget())

		return
	# 모든 저장 파일 삭제: 저장 폴더
	def deleteAllSave(self):
		are_you_sure=QMessageBox.question(self, "", "Delete All Save?", QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.Yes)

		if are_you_sure==QMessageBox.StandardButton.Yes:
			project_name=self.last_right_clicked_object.objectName().split('/')[0]  # 오브젝트 이름에서 프로젝트 이름 가져오기

			# 저장 파일 라벨 삭제
			if self.last_right_clicked_object.objectName()==project_name+"/open":  # 저장 폴더가 열려있음
				self.viewSubItems(self.last_right_clicked_object)  # 접힘 상태로 변경(라벨 삭제)
				self.last_right_clicked_object.setObjectName(project_name+"/open")  # 열기

			# 저장 파일 삭제
			shutil.rmtree(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved")  # 저장 폴더 삭제
			os.makedirs(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved", mode=711)  # 저장 폴더 생성

		return
	## 버튼 클릭이벤트
	# 사이드 뷰 숨김/보임
	def onClickHide(self):
		return


	# 하이라이트 변경
	def focusLabel(self, project_name:str, request_name:str):
		if Global.cur_request_name!="":
			# 기존 하이라이트 제거
			s, n=self.getLabelIndexByPj(Global.cur_project_name)
			self.side_view_list.itemAt(s).widget().setStyleSheet("")  # 프로젝트 라벨 하이라이트 제거
			if n!=1:  # 프로젝트 라벨이 접혀있지 않을 때
				for i in range(s, n):
					if self.side_view_list.itemAt(i).widget().text()==Global.cur_request_name:
						self.side_view_list.itemAt(i).widget().setStyleSheet("")  # 요청 라벨 하이라이트 제거
						break

		# 새 하이라이트 추가
		s, n=self.getLabelIndexByPj(project_name)
		self.side_view_list.itemAt(s).widget().setStyleSheet("background-color:#ccc")  # 프로젝트 라벨 하이라이트 제거
		for i in range(s, n):
			if self.side_view_list.itemAt(i).widget().text()==request_name:
				self.side_view_list.itemAt(i).widget().setStyleSheet("background-color:#aaa")  # 요청 라벨 하이라이트 제거
				break

		return


	# 프로젝트 이름으로 라벨 탐색 후 객체 인덱스 반환
	def getLabelIndexByPj(self, project_name:str) -> tuple:
		start=-1
		num=0

		for i in range(self.side_view_list.count()):
			obj=self.side_view_list.itemAt(i).widget()

			if obj.objectName()=="open" or obj.objectName()=="close":  # 프로젝트 라벨임
				if obj.text()==project_name:  # 찾는 프로젝트 라벨임
					start=i
					num=1
			else:  # 프로젝트 라벨 아님
				if obj.objectName().split('/')[0]==project_name:  # 찾는 프로젝트의 하위 라벨임
					num+=1
				else:
					if start!=-1:  # 프로젝트 라벨 이미 찾음(지나감)
						break

		# 프로젝트 라벨 인덱스, 찾는 라벨 개수 반환
		return start, num
	# 라벨 텍스트와 태그로 라벨 탐색 후 객체 인덱스 반환
	def getLabelIndexByText(self, label_text:str, label_tag:str) -> int:
		for i in range(self.side_view_list.count()):
			if self.side_view_list.itemAt(i).widget().text()==label_text and self.side_view_list.itemAt(i).widget().text()==label_tag:
				return i

		return -1


##################### EventListener ######################
	# 사이드 뷰 요소 좌클릭 감지
	def leftClickListener(self, widget) -> Signal:
		class Filter(QObject):
			clicked = Signal()

			def eventFilter(self, obj, event:QEvent):
				if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
					Global.sdv.last_left_clicked_object=obj
					self.clicked.emit()

				return super().eventFilter(obj, event)

		click_filter = Filter(widget)
		widget.installEventFilter(click_filter)
		return click_filter.clicked
	# 사이드 뷰 요소 우클릭 감지
	def rightClickListener(self, widget) -> Signal:
		class Filter(QObject):
			clicked = Signal()

			def eventFilter(self, obj, event:QEvent):
				if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
					Global.sdv.right_click_mouse_pos=event.globalPos()
					Global.sdv.last_right_clicked_object=obj
					self.clicked.emit()

				return super().eventFilter(obj, event)

		click_filter = Filter(widget)
		widget.installEventFilter(click_filter)
		return click_filter.clicked

