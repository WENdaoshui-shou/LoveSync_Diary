class Operation:
    """操作基类"""
    pass

class Insert(Operation):
    """插入操作"""
    def __init__(self, position, text):
        self.position = position
        self.text = text
    
    def __repr__(self):
        return f"Insert({self.position}, '{self.text}')"

class Delete(Operation):
    """删除操作"""
    def __init__(self, position, length):
        self.position = position
        self.length = length
    
    def __repr__(self):
        return f"Delete({self.position}, {self.length})"

class OTEngine:
    """Operational Transformation引擎"""
    
    @staticmethod
    def apply(operation, text):
        """应用操作到文本"""
        if isinstance(operation, Insert):
            return text[:operation.position] + operation.text + text[operation.position:]
        elif isinstance(operation, Delete):
            return text[:operation.position] + text[operation.position + operation.length:]
        return text
    
    @staticmethod
    def transform(operation1, operation2):
        """转换两个操作，使它们可以按任意顺序应用"""
        if isinstance(operation1, Insert) and isinstance(operation2, Insert):
            # 两个插入操作
            if operation1.position <= operation2.position:
                return operation1, Insert(operation2.position + len(operation1.text), operation2.text)
            else:
                return Insert(operation1.position + len(operation2.text), operation1.text), operation2
        
        elif isinstance(operation1, Insert) and isinstance(operation2, Delete):
            # 插入操作和删除操作
            if operation1.position <= operation2.position:
                return operation1, Delete(operation2.position + len(operation1.text), operation2.length)
            else:
                return Insert(operation1.position - operation2.length, operation1.text), operation2
        
        elif isinstance(operation1, Delete) and isinstance(operation2, Insert):
            # 删除操作和插入操作
            if operation1.position < operation2.position:
                return operation1, Insert(operation2.position - operation1.length, operation2.text)
            else:
                return operation1, operation2
        
        elif isinstance(operation1, Delete) and isinstance(operation2, Delete):
            # 两个删除操作
            if operation1.position + operation1.length <= operation2.position:
                return operation1, Delete(operation2.position - operation1.length, operation2.length)
            elif operation2.position + operation2.length <= operation1.position:
                return operation1, operation2
            else:
                # 重叠的删除操作
                new_op1_length = max(0, operation1.position + operation1.length - operation2.position)
                new_op2_length = max(0, operation2.position + operation2.length - operation1.position - operation1.length)
                return Delete(operation1.position, new_op1_length), Delete(operation1.position, new_op2_length)
        
        return operation1, operation2
    
    @staticmethod
    def compose(operation1, operation2):
        """组合两个操作，返回一个等效的操作"""
        if isinstance(operation1, Insert) and isinstance(operation2, Insert):
            # 两个插入操作
            if operation1.position <= operation2.position:
                return Insert(operation1.position, operation1.text + operation2.text)
            else:
                return Insert(operation2.position, operation2.text + operation1.text)
        
        elif isinstance(operation1, Insert) and isinstance(operation2, Delete):
            # 插入操作后删除操作
            if operation2.position < operation1.position:
                return Delete(operation2.position, operation2.length)
            elif operation2.position < operation1.position + len(operation1.text):
                new_text = operation1.text[:operation2.position - operation1.position] + operation1.text[operation2.position - operation1.position + operation2.length:]
                return Insert(operation1.position, new_text)
            else:
                return Delete(operation2.position - len(operation1.text), operation2.length)
        
        elif isinstance(operation1, Delete) and isinstance(operation2, Insert):
            # 删除操作后插入操作
            if operation2.position < operation1.position:
                return Delete(operation1.position, operation1.length)
            else:
                return Delete(operation1.position, operation1.length)
        
        elif isinstance(operation1, Delete) and isinstance(operation2, Delete):
            # 两个删除操作
            if operation1.position + operation1.length <= operation2.position:
                return Delete(operation1.position, operation1.length + operation2.length)
            elif operation2.position + operation2.length <= operation1.position:
                return Delete(operation2.position, operation2.length + operation1.length)
            else:
                # 重叠的删除操作
                new_position = min(operation1.position, operation2.position)
                new_length = max(operation1.position + operation1.length, operation2.position + operation2.length) - new_position
                return Delete(new_position, new_length)
        
        return operation2

    @staticmethod
    def generate_operation(old_text, new_text):
        """根据文本变化生成操作"""
        # 简单实现：找出第一个不同的位置
        min_len = min(len(old_text), len(new_text))
        i = 0
        while i < min_len and old_text[i] == new_text[i]:
            i += 1
        
        # 文本前缀相同，检查后缀
        if i == min_len:
            if len(old_text) > len(new_text):
                # 删除操作
                return Delete(i, len(old_text) - len(new_text))
            else:
                # 插入操作
                return Insert(i, new_text[i:])
        
        # 找到不同的位置，检查是插入还是删除
        # 简单实现：假设是插入或删除单个字符
        if len(new_text) > len(old_text):
            # 插入操作
            return Insert(i, new_text[i])
        else:
            # 删除操作
            return Delete(i, 1)