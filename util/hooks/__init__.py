import types

from util.dict.attr_dict import ConstIotaAttrDict


class HookCarrier(object):
    events = ConstIotaAttrDict([
        'ENTER',
        'RETURN',
    ])
    method_hooks = {}

    def get_hooks(self, name, event):
        """获得勾子
        parameters:
            name: 勾子挂靠的方法名
            event: 触发勾子的事件
        """
        hk = self.method_hooks.get(name)
        if not hk:
            return []
        hooks = hk.get(event)
        return hooks

    def wrap(self, name):
        """用 wrapper 函数包裹 method, 并定义 event 和放置勾子"""
        method = getattr(self, name)
        if getattr(method, 'origin_method'):
            return self
        
        def wrapper(self, *args, **kwargs):
            # enter 事件
            hooks = self.get_hooks(name, self.events.ENTER)
            for hk in hooks:
                multi_results = hk(args, kwargs)
                if len(multi_results) != 2:
                    raise Exception("expect 2-element tuple, got %d from hook %s:%r" % (len(multi_results), name, hk))
                args, kwargs = multi_results

            results = method(*args, **kwargs)

            # return 事件
            hooks = self.get_hooks(name, self.events.RETURN)
            for hk in hooks:
                results = hk(args, kwargs, results)
            return results

        bound_method = types.MethodType(wrapper, self)
        bound_method.origin_method = method
        setattr(self, name, bound_method)
        return self

    def register(self, name, event, hook):
        """获得勾子
        parameters:
            name: 勾子挂靠的方法名
            event: 触发勾子的事件
            hook: 勾子
        """
        event_hooks = self.method_hooks.get(name, {})
        hooks = event_hooks.get(event, [])
        hooks.append(hook)

        self.wrap(name)

        event_hooks[event] = events
        self.method_hooks[name] = event_hooks
        return self

    def register_return(self, name, hook):
        return self.register(name, self.events.RETURN, hook)
