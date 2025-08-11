# -*- coding: utf-8 -*-
# @Time        :2025/7/29 10:35
# @Author      :文刀水寿
# @File        : ot.py
"""
 @Description :
"""


# -*- coding: utf-8 -*-
# @Time        :2025/7/29 10:35
# @Author      :文刀水寿
# @File        : ot.py
"""
 @Description : 使用UTF-8字节长度计算的操作转换算法
"""


class Operation:
    def __init__(self, op_type, position, text=''):
        self.op_type = op_type  # 操作类型，如 'insert', 'delete'
        self.position = position  # 操作位置
        self.text = text  # 插入的文本（如果是插入操作）

    def __repr__(self):
        return f"Operation(op_type='{self.op_type}', position={self.position}, text='{self.text}')"


def transform(op1, op2):
    if op1.op_type == 'insert' and op2.op_type == 'insert':
        if op1.position < op2.position:
            # 使用UTF-8编码长度计算
            return op1, Operation(op2.op_type, op2.position + len(op1.text.encode('utf-8')), op2.text)
        elif op1.position > op2.position:
            # 使用UTF-8编码长度计算
            return Operation(op1.op_type, op1.position + len(op2.text.encode('utf-8')), op1.text), op2
        else:
            # 处理插入位置相同的情况
            return op1, Operation(op2.op_type, op2.position + len(op1.text.encode('utf-8')), op2.text)
    elif op1.op_type == 'delete' and op2.op_type == 'delete':
        if op1.position < op2.position:
            # 使用UTF-8编码长度计算
            if op1.position + len(op1.text.encode('utf-8')) > op2.position:
                # 使用UTF-8编码长度计算
                overlap = op1.position + len(op1.text.encode('utf-8')) - op2.position
                new_length = max(0, len(op2.text.encode('utf-8')) - overlap)
                return op1, Operation(op2.op_type, op1.position + len(op1.text.encode('utf-8')), op2.text)
            return op1, op2
        elif op1.position > op2.position:
            # 使用UTF-8编码长度计算
            if op2.position + len(op2.text.encode('utf-8')) > op1.position:
                # 使用UTF-8编码长度计算
                overlap = op2.position + len(op2.text.encode('utf-8')) - op1.position
                new_length = max(0, len(op1.text.encode('utf-8')) - overlap)
                return Operation(op1.op_type, op2.position + len(op2.text.encode('utf-8')), op1.text), op2
            return op1, op2
        else:
            # 处理删除位置相同的情况
            # 使用UTF-8编码长度计算
            length = min(len(op1.text.encode('utf-8')), len(op2.text.encode('utf-8')))
            return Operation(op1.op_type, op1.position, op1.text), Operation(op2.op_type, op2.position, op2.text)
    elif op1.op_type == 'insert' and op2.op_type == 'delete':
        if op1.position < op2.position:
            return op1, op2
        elif op1.position >= op2.position + len(op2.text.encode('utf-8')):
            # 使用UTF-8编码长度计算
            return Operation(op1.op_type, op1.position - len(op2.text.encode('utf-8')), op1.text), op2
        else:
            # 插入位置在删除范围内
            return None, op2
    elif op1.op_type == 'delete' and op2.op_type == 'insert':
        if op1.position < op2.position:
            # 使用UTF-8编码长度计算
            return op1, Operation(op2.op_type, op2.position - len(op1.text.encode('utf-8')), op2.text)
        elif op1.position >= op2.position:
            return op1, op2
        else:
            # 删除位置在插入范围内
            return op1, op2


def transform_operations(client_ops, server_ops):
    """将客户端操作序列转换到服务器最新状态"""
    for server_op in server_ops:
        new_client_ops = []
        for client_op in client_ops:
            client_op, _ = transform(client_op, server_op)
            if client_op:
                new_client_ops.append(client_op)
        client_ops = new_client_ops
    return client_ops

