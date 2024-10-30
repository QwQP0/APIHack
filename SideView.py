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


	## UI ����
	# �⺻ UI ����
	def initUI(self, project_name:str=None, request_name:str=None):
		if project_name==None:  # �⺻ UI ����
			# ������Ʈ ����
			self.side_view_list=QVBoxLayout()
			self.hide_btn=QPushButton("<")

			# UI ����
			self.side_view_content.addLayout(self.side_view_list)  # ��� ���� ����
			self.side_view_content.addWidget(self.hide_btn)  # ���� ��ư ����

			# �̺�Ʈ ����
			self.hide_btn.clicked.connect(self.onClickHide)
		else:  # ������Ʈ ������ ��� UI ����
			## ������Ʈ ��
			self.initProjectLabel(project_name, self.side_view_list.count())  # ���κп� ����(��� �� ������Ʈ�̹Ƿ�)
			## ��û ��
			self.initRequestsLabel(project_name, self.side_view_list.count())  # ���κп� ����(��� �� ������Ʈ�̹Ƿ�)
			## ���� ���� ��
			self.initSaveFolderLabel(project_name, self.side_view_list.count())  # ���κп� ����(��� �� ������Ʈ�̹Ƿ�)
			## ���� ���� ��
			self.initSaveFilesLabel(project_name, self.side_view_list.count())  # ���κп� ����(��� �� ������Ʈ�̹Ƿ�)

		return
	# ������Ʈ �󺧻���
	def initProjectLabel(self, project_name:str, index:int):
		self.initLabel(project_name, "open", index, "p")

		return
	# ��û �� ����
	def initRequestsLabel(self, project_name:str, index:int):
		for request_name in list(Global.projects_data[project_name]["requests"].keys()):
			self.initLabel(request_name, project_name, index, "q")
			index+=1  # ���� ���� ����

		return
	# ���� ���� �� ����
	def initSaveFolderLabel(self, project_name:str, index:int):
		self.initLabel("saved", project_name+"/open", index, "f")

		return
	# ���� ���� �� ����
	def initSaveFilesLabel(self, project_name:str, index:int):
		save_file_names=[]
		for save_files in os.walk(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved"):  # ���̺� ���� ���� ���� Ž��
			save_file_names.extend(save_files[2])  # �̸� ����

		for i in range(len(save_file_names)):
			save_file_name=save_file_names[i].split('.')
			extension=save_file_name[-1]  # Ȯ����
			save_file_name='.'.join(save_file_name[:len(save_file_name)-1])  # ���� �̸�(Ȯ���� ����)

			if extension=="rsv":
				self.initLabel(save_file_name, project_name+"/saved", index, "s")
				index+=1  # ���� ���� ���� ����

		return
	# �� ����
	def initLabel(self, text:str, tag:str, index:int, label_type:str):
		new_label=QLabel(text)  # �ؽ�Ʈ ����
		new_label.setObjectName(tag)  # �±� ����

		## �̺�Ʈ ����
		# ��Ŭ��
		if label_type=="p":  # ������Ʈ
			self.leftClickListener(new_label).connect(self.viewSubItems)
		elif label_type=="q":  # ��û
			self.leftClickListener(new_label).connect(lambda: Global.main.loadProject(new_label.objectName(), new_label.text()))
		elif label_type=="f":  # ���� ����
			self.leftClickListener(new_label).connect(self.viewSubItems)
		elif label_type=="s":  # ���� ����
			self.leftClickListener(new_label).connect(self.viewSaveFile)
		# ��Ŭ��
		self.rightClickListener(new_label).connect(self.viewContextMenu)

		self.side_view_list.insertWidget(index, new_label)  # �� ����

		return


	### �̺�Ʈ, ��ȣ�ۿ�
	## ��Ŭ�� ��ȣ�ۿ�
	# ����/����: ������Ʈ, ���� ����
	def viewSubItems(self, obj:QLabel=None):
		if obj==None:
			obj=self.last_left_clicked_object

		if obj.text()!="saved":  # ������Ʈ(���� ���� �ƴ�)
			if obj.objectName()=="open":  # ��������
				s, n=self.getLabelIndexByPj(obj.text())

				# ������Ʈ ���� �� ����
				for i in range(n-1):  # -1: ������Ʈ �� ����
					print(i, self.side_view_list.itemAt(s+1).widget())
					deleteObject(self.side_view_list.itemAt(s+1).widget())

				obj.setObjectName("close")
			else:  # ��������
				s, n=self.getLabelIndexByPj(obj.text())
				self.initRequestsLabel(obj.text(), s+1)  # ��û ��(������Ʈ �� �ٷ� ������ ����)
				s, n=self.getLabelIndexByPj(obj.text())
				self.initSaveFolderLabel(obj.text(), s+n)  # ���� ���� ��
				self.initSaveFilesLabel(obj.text(), s+n+1)  # ���� ���� ��

				self.focusLabel(Global.cur_project_name, Global.cur_request_name)  # ���̶���Ʈ ����(���� ���̶���Ʈ�� �������� �� �����Ƿ�)

				obj.setObjectName("open")
		else:
			if obj.objectName().split('/')[1]=="open":  # ��������
				s, n=self.getLabelIndexByPj(obj.objectName().split('/')[0])

				for i in range(s+n-1, s, -1):  # �ڿ������� Ž��
					if self.side_view_list.itemAt(i).widget().objectName().split('/')[1]=="saved":
						deleteObject(self.side_view_list.itemAt(i).widget())
					else:  # ���� ���� ���� �ƴϸ� �ߴ�
						break
				
				obj.setObjectName(obj.objectName().split('/')[0]+"/close")
			else:  # ��������
				self.initSaveFilesLabel(obj.objectName().split('/')[0], self.getLabelIndexByText(obj.text(), obj.objectName()))

				obj.setObjectName(obj.objectName().split('/')[0]+"/open")

		return
	# ���� ���� �˾�: ���� ����
	def viewSaveFile(self):
		return
	## ��Ŭ�� ��ȣ�ۿ�
	# ��Ŭ�� �޴� ����
	def viewContextMenu(self):
		menu=QMenu(self.last_right_clicked_object, self.right_click_mouse_pos)

		if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ
			# �� ��û ����
			create_request_action=QAction("New Request")
			create_request_action.triggered.connect(self.newRequest)
			menu.addAction(create_request_action)
			# ������Ʈ �̸� ����
			rename_project_action=QAction("Rename")
			rename_project_action.triggered.connect(self.rename)
			menu.addAction(rename_project_action)
			# ������Ʈ �ݱ�
			close_project_action=QAction("Close Project")
			close_project_action.triggered.connect(self.closeProject)
			menu.addAction(close_project_action)
			# ������Ʈ ����
			delete_project_action=QAction("Delete")
			delete_project_action.triggered.connect(self.delete)
			menu.addAction(delete_project_action)
		elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # ��û
			# ��û �̸� ����
			rename_request_action=QAction("Rename")
			rename_request_action.triggered.connect(self.rename)
			menu.addAction(rename_request_action)
			# ��û ����
			duplicate_request_action=QAction("Duplicate")
			duplicate_request_action.triggered.connect(self.duplicate)
			menu.addAction(duplicate_request_action)
			# ��û ����
			delete_request_action=QAction("Delete")
			delete_request_action.triggered.connect(self.delete)
			menu.addAction(delete_request_action)
		elif self.last_right_clicked_object.objectName().split('/')[1]=="saved":  # ����� ����
			# ���� �̸� ����
			rename_save_action=QAction("Rename")
			rename_save_action.triggered.connect(self.rename)
			menu.addAction(rename_save_action)
			# ���� ����
			duplicate_save_action=QAction("Duplicate")
			duplicate_save_action.triggered.connect(self.duplicate)
			menu.addAction(duplicate_save_action)
			# ���� ����
			delete_save_action=QAction("Delete")
			delete_save_action.triggered.connect(self.delete)
			menu.addAction(delete_save_action)
		else:  # ���� ����
			# ������ ���� ��ü ����
			delete_all_save_action=QAction("Delete All")
			delete_all_save_action.triggered.connect(self.deleteAllSave)
			menu.addAction(delete_all_save_action)
		
		menu.exec(self.right_click_mouse_pos)

		return
	# �� ��û ����: ������Ʈ
	def newRequest(self):
		new_request_dialog=QInputDialog()

		name, ok=new_request_dialog.getText(Global.main, "", "New Request", text=File.setNameAuto("", self.last_right_clicked_object.text(), 'q'), flags=Qt.WindowType.FramelessWindowHint)

		#todo# ��û �̸� ��ġ�� �� Ȯ��

		if ok:
			if self.last_right_clicked_object.objectName()=="close":  # ������Ʈ ���� ����
				self.viewSubItems(self.last_right_clicked_object)  # ������Ʈ ����

			i=self.getLabelIndexByText("saved", self.last_right_clicked_object.text()+"/open")  # Ŭ���� ������Ʈ�� ���� ���� ���� �ε��� �ҷ���
			
			Global.projects_data[self.last_right_clicked_object.text()]["requests"][name]={}  #todo#�⺻ ��û ���� ����

			self.initLabel(name, self.last_right_clicked_object.text(), i, "q")  # �� ����
			
		Global.main.loadProject(self.last_right_clicked_object.text(), name)  # ��û �ε�

		return
	# �̸� �ٲٱ�: ������Ʈ, ��û, ���� ����
	def rename(self):
		rename_dialog=QInputDialog()

		if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ �� ��
			name, ok=rename_dialog.getText(Global.main, "", "Rename Project", flags=Qt.WindowType.FramelessWindowHint)
		else:
			name, ok=rename_dialog.getText(Global.main, "", "Rename", flags=Qt.WindowType.FramelessWindowHint)

		#todo# �̸� ��ġ�� �� Ȯ��(���/�̸� <-�� �����ϴ���)

		if ok:
			if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ
				Global.projects_data[name]=Global.projects_data[self.last_right_clicked_object.text()]  # ������ ����
				shutil.move(Global.projects_data[name]["last_path"]+'/'+self.last_right_clicked_object.text(), Global.projects_data[name]["last_path"]+'/'+name)  # ������Ʈ ���� �̸�����
				shutil.move(Global.projects_data[name]["last_path"]+'/'+name+'/'+self.last_right_clicked_object.text()+".ahp", Global.projects_data[name]["last_path"]+'/'+name+'/'+name+".ahp")
				# -> ������Ʈ ���� �̸� ����
				del Global.projects_data[self.last_right_clicked_object.text()]  # ���� ������ ����

				# ���̵� ���� ���� ���(��û, ���� ����, ���� ����) objectName �����ϱ�
				s, n=self.getLabelIndexByPj(self.last_right_clicked_object.text())

				for i in range(s+1, n-1):  # +1, -1: ������Ʈ �� ����
					obj=self.side_view_list.itemAt(i).widget()

					# objectName ����
					if len(obj.objectName().split('/'))==1:
						obj.setObjectName(name)
					else:
						obj.setObjectName(name+"/"+obj.objectName().split('/')[1])
			elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # ��û
				project_name=self.last_right_clicked_object.objectName()  # ������Ʈ �̸����� ������Ʈ �̸� ��������

				Global.projects_data[project_name]["requests"][name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]  # ������ ����
				del Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]  # ���� ������ ����
			else:  # ���� ����
				project_name=self.last_right_clicked_object.objectName().split('/')[0]  # ������Ʈ �̸����� ������Ʈ �̸� ��������

				shutil.move(Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+self.last_right_clicked_object.text()+'.rsv', \
					Global.projects_data[project_name]["last_path"]+'/'+project_name+'/saved/'+name+'.rsv')  # ����� ���� �̸� ����

			self.last_right_clicked_object.setText(name)  # ���̵� ���� ������Ʈ �̸� ����

		else:
			print("cancel")

		return
	# ����: ��û, ���� ����
	def duplicate(self):
		if len(self.last_right_clicked_object.objectName().split('/'))==1:  # ��û
			project_name=self.last_right_clicked_object.objectName()
			new_request_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 'q')

			# �� ��û ����
			Global.projects_data[project_name]["requests"][new_request_name]=Global.projects_data[project_name]["requests"][self.last_right_clicked_object.text()]
			# -> ������ ����
			
			insert_pos=self.side_view_list.indexOf(self.last_right_clicked_object)+1
			self.initLabel(new_request_name, project_name, insert_pos, "q")  # ��û �� ����

			Global.main.loadProject(project_name, new_request_name)
		else:  # ���� ����
			project_name=self.last_right_clicked_object.objectName().split('/')[0]
			project_path=Global.projects_data[project_name]['last_path']+'/'+project_name
			new_file_name=File.setNameAuto(self.last_right_clicked_object.text(), project_name, 's')

			shutil.copy(project_path+"/saved/"+self.last_right_clicked_object.text()+".rsv", project_path+"/saved/"+new_file_name+".rsv")  # ���� ���� ����
			
			insert_pos=self.side_view_list.indexOf(self.last_right_clicked_object)+1
			self.initLabel(new_file_name, project_name+"/saved", insert_pos, "s")  # ��û �� ����

		return
	# ����: ������Ʈ, ��û, ���� ����
	def delete(self):
		if self.last_right_clicked_object.objectName()=="open" or self.last_right_clicked_object.objectName()=="close":  # ������Ʈ
			are_you_sure=QMessageBox()
			are_you_sure.setText("Delete Project File?")
			are_you_sure.setStandardButtons(QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.No|QMessageBox.StandardButton.Yes)
			answer=are_you_sure.exec()

			if answer!=QMessageBox.StandardButton.Cancel:
				if answer==QMessageBox.StandardButton.Yes:  # ���ϱ��� ���� ����
					print(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())
					shutil.rmtree(Global.projects_data[self.last_right_clicked_object.text()]["last_path"]+'/'+self.last_right_clicked_object.text())  # ������Ʈ ���� ����

				del Global.projects_data[self.last_right_clicked_object.text()]  # ������Ʈ ������ ����

				# ������Ʈ �󺧰� ���� �� ����
				s, n=self.getLabelIndexByPj(self.last_right_clicked_object.text())
				for i in range(s, n):
					deleteObject(self.side_view_list.itemAt(s).widget())
		elif len(self.last_right_clicked_object.objectName().split('/'))==1:  # ��û
			project_name=self.last_right_clicked_object.objectName()  # ������Ʈ �̸� ��������
			request_name=self.last_right_clicked_object.text()  # ��û �̸� ��������

			del Global.projects_data[project_name]["requests"][request_name]  # ��û ������ ����

			#todo#  ���� ���� Request�̰� ������ ��û�� �����ִ� �����϶� �� ��ȯ
			#todo#  �� ������Ʈ���� ��û �ּ� 1������ ���� ��
			
			deleteObject(self.last_right_clicked_object)  # ���̵� �信�� ��û �� ����
		else:  # ���� ����
			project_name=self.last_right_clicked_object.objectName().split('/')[0]  # ������Ʈ �̸� ��������
			file_name=self.last_right_clicked_object.text()  # ����� ���� �̸� ��������

			os.remove(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved/"+file_name+".rsv")  # ����� ���� ����

			#todo#  �ش� ������ �˾� ���·� �������� �� ����
			
			deleteObject(self.last_right_clicked_object)  # ���̵� �信�� ���� ���� �� ����

		return
	# �ݱ�: ������Ʈ
	def closeProject(self):
		del Global.projects_data[self.last_right_clicked_object.text()]  # ������Ʈ ������ ����

		# ������Ʈ �󺧰� ���� �� ����
		s, n=self.getLabelIndexByPj(self.last_right_clicked_object.text())
		for i in range(s, n):
			deleteObject(self.side_view_list.itemAt(s).widget())

		return
	# ��� ���� ���� ����: ���� ����
	def deleteAllSave(self):
		are_you_sure=QMessageBox.question(self, "", "Delete All Save?", QMessageBox.StandardButton.Cancel|QMessageBox.StandardButton.Yes)

		if are_you_sure==QMessageBox.StandardButton.Yes:
			project_name=self.last_right_clicked_object.objectName().split('/')[0]  # ������Ʈ �̸����� ������Ʈ �̸� ��������

			# ���� ���� �� ����
			if self.last_right_clicked_object.objectName()==project_name+"/open":  # ���� ������ ��������
				self.viewSubItems(self.last_right_clicked_object)  # ���� ���·� ����(�� ����)
				self.last_right_clicked_object.setObjectName(project_name+"/open")  # ����

			# ���� ���� ����
			shutil.rmtree(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved")  # ���� ���� ����
			os.makedirs(Global.projects_data[project_name]["last_path"]+'/'+project_name+"/saved", mode=711)  # ���� ���� ����

		return
	## ��ư Ŭ���̺�Ʈ
	# ���̵� �� ����/����
	def onClickHide(self):
		return


	# ���̶���Ʈ ����
	def focusLabel(self, project_name:str, request_name:str):
		if Global.cur_request_name!="":
			# ���� ���̶���Ʈ ����
			s, n=self.getLabelIndexByPj(Global.cur_project_name)
			self.side_view_list.itemAt(s).widget().setStyleSheet("")  # ������Ʈ �� ���̶���Ʈ ����
			if n!=1:  # ������Ʈ ���� �������� ���� ��
				for i in range(s, n):
					if self.side_view_list.itemAt(i).widget().text()==Global.cur_request_name:
						self.side_view_list.itemAt(i).widget().setStyleSheet("")  # ��û �� ���̶���Ʈ ����
						break

		# �� ���̶���Ʈ �߰�
		s, n=self.getLabelIndexByPj(project_name)
		self.side_view_list.itemAt(s).widget().setStyleSheet("background-color:#ccc")  # ������Ʈ �� ���̶���Ʈ ����
		for i in range(s, n):
			if self.side_view_list.itemAt(i).widget().text()==request_name:
				self.side_view_list.itemAt(i).widget().setStyleSheet("background-color:#aaa")  # ��û �� ���̶���Ʈ ����
				break

		return


	# ������Ʈ �̸����� �� Ž�� �� ��ü �ε��� ��ȯ
	def getLabelIndexByPj(self, project_name:str) -> tuple:
		start=-1
		num=0

		for i in range(self.side_view_list.count()):
			obj=self.side_view_list.itemAt(i).widget()

			if obj.objectName()=="open" or obj.objectName()=="close":  # ������Ʈ ����
				if obj.text()==project_name:  # ã�� ������Ʈ ����
					start=i
					num=1
			else:  # ������Ʈ �� �ƴ�
				if obj.objectName().split('/')[0]==project_name:  # ã�� ������Ʈ�� ���� ����
					num+=1
				else:
					if start!=-1:  # ������Ʈ �� �̹� ã��(������)
						break

		# ������Ʈ �� �ε���, ã�� �� ���� ��ȯ
		return start, num
	# �� �ؽ�Ʈ�� �±׷� �� Ž�� �� ��ü �ε��� ��ȯ
	def getLabelIndexByText(self, label_text:str, label_tag:str) -> int:
		for i in range(self.side_view_list.count()):
			if self.side_view_list.itemAt(i).widget().text()==label_text and self.side_view_list.itemAt(i).widget().text()==label_tag:
				return i

		return -1


##################### EventListener ######################
	# ���̵� �� ��� ��Ŭ�� ����
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
	# ���̵� �� ��� ��Ŭ�� ����
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

