# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

import inspect


def terracing(msg):
    # list of FrameInfo(frame, filename, lineno, function, code_context, index)
    frame_list = inspect.stack()

    # frame_list = frame_list[1:] # remove `terracing` itself
    # frame_list = frame_list[:-1] # remove `module`

    leading_chars = '  '
    leading_shift = -1
    leading_cnt = len(frame_list) + leading_shift

    caller_shift = 1

    # frame_obj = frame_list[0][0]
    # output = '%s%s' % (leading_chars*leading_cnt, msg)
    """
    for i, frame_info in enumerate(frame_list):
        caller_name = frame_info[3] # using frame_info.function in py3
        i += 1
        print(i*'-', caller_name)
    """
    return {
        'leading': leading_chars*leading_cnt,
        'msg': msg,
        'caller': frame_list[caller_shift][3],
    }
