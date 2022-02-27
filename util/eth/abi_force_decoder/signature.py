import re
from dataclasses import dataclass

# 匹配整个函数
re_fun = re.compile(r'(?P<fun_name>[\w\d_]+)\((?P<fun_body>.*?)\)')
# 匹配函数中的参数
re_arg = re.compile(r'(?P<arg>[^,)]+)+')


@dataclass
class FunctionInput:
    """函数中的参数"""
    internal_type: str
    type: str
    name: str


@dataclass
class FunctionSignature:
    inputs: [FunctionInput]
    name: str
    type: str = 'function'


def new_fn_signature_from_str(line: str) -> FunctionSignature:
    """从文本中提取函数签名，例：new_fn_signature_from_str('mint(uint256 amount)')
    :rtype: FunctionSignature
    """
    m = re_fun.search(line)
    fn_name = m.group('fun_name')
    fn_body = m.group('fun_body')

    fn_args = re_arg.findall(fn_body)
    fn_inputs: [FunctionInput] = []
    for fn_arg in fn_args:
        fn_arg = str(fn_arg).strip()
        pieces = fn_arg.split(' ')
        fn_inputs.append(FunctionInput(pieces[0], pieces[0], pieces[1]))

    fn_sig: FunctionSignature = FunctionSignature(fn_inputs, fn_name)
    return fn_sig
