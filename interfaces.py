import types
import inspect
import functools

from check_func_iface import check_signature_acceptable

RUNTIME_CHECK = True

def get_method(class_name, func):
    @functools.wraps(func)
    def some_method(self, *dt, **mp):
        raise NotImplemented(
            "Error : interface function call - {0}.{1}".format(class_name, 
                                                               func.__name__))
    return some_method

def is_callable(obj):
    return isinstance(obj, (types.LambdaType, 
                            types.FunctionType, 
                            types.UnboundMethodType))

def do_check_me(func):
    func.do_check_me = True
    return func

def do_not_check_me(func):
    func.do_not_check_me = True
    return func

def should_check(vname, val):
    if vname.startswith('__') and \
            vname.endswith('__') and  \
                not getattr(val, 'do_check_me', False):
        return False
    return not getattr(val, 'do_not_check_me', False)

class InterfaceMeta(type):
    no_check = "__me_no_check__"

    def __new__(cls, name, bases, cdict):
        if name != cls.no_check:
            interface_methods = {}
            new_methods = {}
            
            for vname, val in cdict.items():
                if is_callable(val) and should_check(vname, val):
                    new_methods[name] = get_method(vname, val)
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

        if inspect.getargspec(check_func).args[0] == 'self':
            check_func.selfable = True
        else:
            check_func.selfable = False

        def closure(self, *dt, **mp):
            if getattr(check_func, 'selfable', False):
                obj = check_func(self, *dt, **mp)
            else:
                obj = check_func(*dt, **mp)
            
            if isinstance(obj, types.GeneratorType):
                obj.next()
            
            res = real_func(self, *dt, **mp)

            if isinstance(obj, types.GeneratorType):
                try:
                    obj.send(res)
                except StopIteration:
                    pass
                else:
                    raise AssertionError("Somethig wrong with check func")
            
            return res

        closure.__real_func__ = real_func
        return closure
    else:
        return real_func
    
incpt_ifaces = """Incompatible interfaces set: {0}. They have the same called methods {1}"""

class ImplementsMeta(type):
    no_check = InterfaceMeta.no_check

    @classmethod
    def check_interfaces_consistency(cls, all_interfaces):
        fdict = {}
        fnames_set = set()
        fname_to_iface = {}
        for interface in all_interfaces:
            fnames = set(interface.__interface_methods__.keys())
            for name in fnames.intersection(fnames_set):
                curr_method = interface.__interface_methods__[name]
                try:
                    check_signature_acceptable(fdict[name], curr_method)
                except AssertionError:
                    err = AssertionError(
                        "Interfaces {0} and {1} is inconsistent".format(
                                interface, 
                                fname_to_iface[name]))
                    err.iface1 = interface
                    err.iface2 = fname_to_iface[name]
            fnames_set.update(fnames)
            fdict.update(interface.__interface_methods__)
            fname_to_iface.update(dict((name, interface) for name in fnames))

    def __new__(cls, name, bases, cdict):
        
        # tempo class - recursive call
        if name == cls.no_check:
            return super(ImplementsMeta, cls).__new__(cls, name, bases, cdict)

        tempo_cls = type.__new__(type, cls.no_check , bases, cdict)
        
        # check interface set consistency - no duplicated functions from
        # different inheritance path's
        if '__all_interfaces__' not in cdict:
            all_interfaces = set()
            for curr_cls in tempo_cls.mro():
                all_interfaces.update(getattr(curr_cls, '__implements__', []))
            all_interfaces = list(all_interfaces)
        else:
            all_interfaces = cdict['__all_interfaces__']
        
        if not cdict.get('__no_interfaces_consistency_check__', False):
            cls.check_interfaces_consistency(all_interfaces)

        # get all interfaces method and track interface for each method
        # iterate over interfaces in reverse order
        # last resent interfaces should replace 
        # older signatures
        imethods = {}
        imethods_from_iface = {}
        for iface in all_interfaces[::-1]:
            ims = iface.__interface_methods__
            imethods.update(ims)
            imethods_from_iface.update(dict((name, iface) 
                                        for name in ims.keys()))
        
        # check, that all not checked before functions have signatures,
        # which consistent to interfaces signatures

        for fname, iface_func in imethods.items():
            impl_func = getattr(tempo_cls, fname, None)
            if impl_func is None:
                raise AssertionError("Method {0} is not implemented".\
                                format(fname))
            # if checked and checked over correct interface
            signature_checked_over = getattr(impl_func, 
                                             '__signature_checked__', None)
            if signature_checked_over != imethods_from_iface[fname]:
                # check and update all new functions to checked functions
                # and ones from based, not updated before

                # take original function, without check wrapper
                impl_func = getattr(impl_func, '__real_func__', impl_func)
                impl_func = getattr(impl_func, 'im_func', impl_func)

                check_signature_acceptable(iface_func, impl_func,
                                           iface_no_self=True)
                
                cdict[fname] = check_and_call(iface_func, impl_func)
                cdict[fname].__signature_checked__ = signature_checked_over
        
        cdict['__all_interfaces__'] = all_interfaces
                
        # create class
        new_cls = super(ImplementsMeta, cls).__new__(cls, name, bases, cdict)
        
        # call __after_init_check__ check's of interfaces 
        for iface in all_interfaces:
            if hasattr(iface, "__after_init_check__"):
                iface.__after_init_check__(new_cls)
                    
        return new_cls
        
class ImplementsBase(object):
    __metaclass__ = ImplementsMeta

class Interface(object):
    __metaclass__ = InterfaceMeta 


        
        
