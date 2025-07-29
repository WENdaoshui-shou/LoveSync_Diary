# -*- coding: utf-8 -*-
# @Time        :2025/7/29 10:35
# @Author      :文刀水寿
# @File        : ot.py
"""
 @Description :
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
            return op1, Operation(op2.op_type, op2.position + len(op1.text), op2.text)
        elif op1.position > op2.position:
            return Operation(op1.op_type, op1.position + len(op2.text), op1.text), op2
        else:
            # 处理插入位置相同的情况
            return op1, Operation(op2.op_type, op2.position + len(op1.text), op2.text)
    elif op1.op_type == 'delete' and op2.op_type == 'delete':
        if op1.position < op2.position:
            if op1.position + len(op1.text) > op2.position:
                new_length = max(0, len(op2.text) - (op1.position + len(op1.text) - op2.position))
                return op1, Operation(op2.op_type, op1.position + len(op1.text), op2.text[new_length:])
            return op1, op2
        elif op1.position > op2.position:
            if op2.position + len(op2.text) > op1.position:
                new_length = max(0, len(op1.text) - (op2.position + len(op2.text) - op1.position))
                return Operation(op1.op_type, op2.position + len(op2.text), op1.text[new_length:]), op2
            return op1, op2
        else:
            # 处理删除位置相同的情况
            length = min(len(op1.text), len(op2.text))
            return Operation(op1.op_type, op1.position, op1.text[length:]), Operation(op2.op_type, op2.position,
                                                                                      op2.text[length:])
    elif op1.op_type == 'insert' and op2.op_type == 'delete':
        if op1.position < op2.position:
            return op1, op2
        elif op1.position >= op2.position + len(op2.text):
            return Operation(op1.op_type, op1.position - len(op2.text), op1.text), op2
        else:
            # 插入位置在删除范围内
            return None, op2
    elif op1.op_type == 'delete' and op2.op_type == 'insert':
        if op1.position < op2.position:
            return op1, Operation(op2.op_type, op2.position - len(op1.text), op2.text)
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