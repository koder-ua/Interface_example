import types
import functools

from cheсk_func_iface import acceptable_interface

RUNTIME_CHECK = True

def get_method(class_name, func):
    @functools.wraps(func)
    def some_method(self, *dt, **mp):
        raise NotImplemented(
            "Error : interface function call - {0}.{1}".format(class_name, 
                                                               func.__name__))
    return some_method


class InterfaceMeta(type):
    def __new__(cls, name, bases, cdict):
        interface_methods = {}
        new_methods = {}
        
        for vname, val in cdict.items():
            if isinstance(val, (types.LambdaType, types.FunctionType)):
                new_methods[name] = get_method(name, val)
                interface_methods[vname] = val
        
        cdict.update(new_methods)
        
        res = {}
        for bcls in bases:
            res.update(getattr(bcls, '__interface_methods__', {}))
        
        res.update(interface_methods)
        cdict['__interface_methods__'] = res
        
        return super(InterfaceMeta, cls).__new__(cls, name, bases, cdict)


def check_and_call(check_func, real_func):
    if RUNTIME_CHECK:
        def closure(self, *dt, **mp):
            check_func(*dt, **mp)
            return real_func(self, *dt, **mp)
        closure.interface_checked = True
        return closure
    else:
        return real_func
    
        
class ImplementsMeta(type):
    def __new__(cls, name, bases, cdict):
        implements = cdict.get('__implements__', [])
        if implements != []:
            idict = {}
            
            for interface in implements:
                idict.update(interface.__interface_methods__)
                
            for vname, val in cdict.items():
                if isinstance(val, (types.LambdaType, types.FunctionType)):
                    if vname in idict:
                        acceptable_interface(idict[vname], val, 
                                             iface_no_self=True)
                        cdict[vname] = check_and_call(idict[vname],val)

        new_tp = super(ImplementsMeta, cls).__new__(cls, name, bases, cdict)
        # check, that object implements all methods, declared in implemented 
        # interfaces
        if implements != []:
            for meth_name in idict:
                val = getattr(new_tp, meth_name, None)
                if not isinstance(val, (types.LambdaType, types.FunctionType, types.UnboundMethodType)):
                    raise ValueError("Method {0} is not implemented".\
                                    format(meth_name))
                elif not getattr(val, 'interface_checked', False):
                    acceptable_interface(idict[meth_name], val, 
                                         iface_no_self=True)
        
        return new_tp
        
class ImplementsBase(object):
    __metaclass__ = ImplementsMeta

class Interface(object):
    __metaclass__ = InterfaceMeta 


        
        
