
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
				if len(var_value_stack)!=len(self.var_order):  # ��Ʈ �̿ϼ�
					var_name=self.var_order[len(var_value_stack)]  # ���� ��ȸ�� ������ ���� �ҷ���
					var_iterator_stack.append(self.traverseVar(var_name))  # ���� ��ȸ�� �߰�
				
					var_value_stack.append(next(var_iterator_stack[-1]))  # ù ���� ���
				else:  # ��Ʈ �ϼ�
					yield var_value_stack  # ��Ʈ ��ȯ

					try:
						var_value_stack.pop()  # ��Ʈ��
					except:
						return