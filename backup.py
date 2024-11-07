
			if len(var_value_stack)!=len(var_iterator_stack):  # 순회자만 넣고 변수는 아직 안넣음
				try:
					var_value_stack.append(next(var_iterator_stack[-1]))  # 다음 변수 기입
				except:  # 다음 변수 없음! -> 변수 순회 종료
					try:
						var_value_stack.pop()  # 이 변수 스택을 통한 경로 없음
						var_iterator_stack.pop()  # 순회가 끝난 스택
					except:
						return
			else:  # 다음 순회자 넣을 차례
				if len(var_value_stack)!=len(self.var_order):  # 세트 미완성
					var_name=self.var_order[len(var_value_stack)]  # 현재 순회할 변수의 정보 불러옴
					var_iterator_stack.append(self.traverseVar(var_name))  # 변수 순회자 추가
				
					var_value_stack.append(next(var_iterator_stack[-1]))  # 첫 변수 등록
				else:  # 세트 완성
					yield var_value_stack  # 세트 반환

					try:
						var_value_stack.pop()  # 백트랙
					except:
						return