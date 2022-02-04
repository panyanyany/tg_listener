

class UnitConverterFactory(object):

    def __init__(self, unit_level):
        self.unit_level = unit_level
        self.unit_seq = [unit for unit, step in unit_level]

    def get_units(self):
        return self.unit_seq

    def convert(self, num, src_unit, dst_unit):
        src_idx = self.unit_seq.index(src_unit.lower())
        dst_idx = self.unit_seq.index(dst_unit.lower())

        step = 1 if src_idx <= dst_idx else -1
        # print('enter:', src_idx, dst_idx, step)
        for i in range(src_idx, dst_idx, step):
            if step > 0:
                num /= self.unit_level[i][1]
            else:
                num *= self.unit_level[i-1][1]
        return num

    def top(self, num, src_unit):
        i = 0
        units = self.get_units()
        for unit in units:
            i += 1
            if unit.lower() == src_unit.lower():
                break
        last_num = num
        last_unit = src_unit
        for unit in units[i:]:
            val = self.convert(last_num, last_unit, unit)
            if val < 1:
                break
            last_num = val
            last_unit = unit
        return last_num, last_unit

Storage = UnitConverterFactory([
    ('mb', 1024),
    ('gb', 1024),
    ('tb', None),
])

Speed = UnitConverterFactory([
    ('mbps', 1000),
    ('gbps', 1000),
    ('tbps', None),
])
