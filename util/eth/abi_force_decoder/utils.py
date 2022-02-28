import json
from itertools import permutations, product


def get_signatures_from_abi(filename) -> list:
    with open(filename) as fp:
        content = fp.read()

    items = json.loads(content)
    fns = []
    for item in items:
        if item['type'] != 'function':
            continue
        fn_args = []
        for arg in item['inputs']:
            internal_type = arg['internalType']
            _type = arg['type']
            name = arg['name']
            fn_args.append(f"{internal_type} {name}")

        fn = f"{item['name']}({', '.join(fn_args)})"
        fns.append(fn)
    return fns


def fn_signature_compose(names: [str], arg_sigs: [str]):
    """组合生成不重复的函数签名: fn_signature_compose(['mint', 'claim'], ['uint num', 'uint256 num'])"""
    transformed_names = []
    for name in names:
        n = str(name).replace(' ', '')
        transformed_names.append(n)
        n = str(name).lower().replace(' ', '')
        transformed_names.append(n)
        n = str(name).title().replace(' ', '')
        transformed_names.append(n)

    transformed_names = list(set(transformed_names))
    transformed_names.sort()
    # print(transformed_names)

    items = product(transformed_names, arg_sigs)
    for item in items:
        line = f'{item[0]}({item[1]})'
        yield line
