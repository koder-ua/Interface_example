import inspect

def check_signature_acceptable(iface_func, impl_func, iface_no_self=False):
    # check, that impl_func can be called with any set off arguments
    # with acceptable for iface_func
    
    iface_argspec = inspect.getargspec(iface_func)
    impl_argspec = inspect.getargspec(impl_func)
    
    if iface_no_self:
        if iface_argspec.args[0] != 'self':
            iface_argspec.args.insert(0, 'self')
    
    if iface_argspec.varargs is not None and impl_argspec.varargs is None:
        raise AssertionError("{0} have varargs, while {1} - not".
                                format(iface_func, impl_func))
                       
    if iface_argspec.keywords is not None and impl_argspec.keywords is None:
        raise AssertionError("{0} have kwargs, while {1} - not".
                                format(iface_func, impl_func))
    
    if iface_argspec.defaults is None:
        iface_dlen = 0
    else:
        iface_dlen = len(iface_argspec.defaults)
    
    if impl_argspec.defaults is None:
        impl_dlen = 0
    else:
        impl_dlen = len(impl_argspec.defaults)
    
    if iface_dlen > impl_dlen:
        raise AssertionError("{0} have {1} defaults, while {2} - {3}".
                                format(iface_func, 
                                       iface_dlen,
                                       impl_func,
                                       impl_dlen))
    
    if len(iface_argspec.args) > len(impl_argspec.args):
        if impl_argspec.keywords is None or \
           impl_argspec.varargs is None:
            raise AssertionError("{0} have less arguments, than {1} and varargs or kwargs isn't present".
                                format(impl_func, iface_func))
    
    if len(iface_argspec.args) < len(impl_argspec.args) - \
                                    (impl_dlen - iface_dlen):
        raise AssertionError("{0} have more arguments, than {1}".
                            format(impl_func, iface_func))
        
                                        
    mlen = min(len(iface_argspec.args), len(impl_argspec.args))
    
    if iface_argspec.args[:mlen] != impl_argspec.args[:mlen]:
            raise AssertionError(
                "Argument names for {0} and {1} is incompatible".
                                format(iface_func, impl_func))
        
    if iface_argspec.defaults:
        iface_defaults = dict(
                        zip(
                            iface_argspec.args[-len(iface_argspec.defaults):],
                            iface_argspec.defaults))
    else:             
        iface_defaults = {}           
        
    if impl_argspec.defaults:
        impl_defaults = dict(
                        zip(
                            impl_argspec.args[-len(impl_argspec.defaults):],
                            impl_argspec.defaults))
    else:
        impl_defaults = {}
    
    for k,v in iface_defaults.items():
        if k not in impl_defaults or impl_defaults[k] != v:
            raise AssertionError(
                "Defaults names for {0} and {1} is incompatible".
                                format(iface_func, impl_func))
        
        
