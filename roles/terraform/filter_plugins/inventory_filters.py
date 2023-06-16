from ansible.plugins.filter import core

def expand_nodes(mapping, defaults):
    """ Expands a dictionary defining hosts.

            mapping:

                key: hostname or hostrange of form "prefix[start-end]" (inclusive)
                value: dict or None, in which case defaults is used
            
            defaults: dict, used in place of mapping value if that is None
        
        Returns a dict with:
            keys: hostnames (expanded from hostranges if necessary).
            values: defaults overriden with mapping values
    """
    output = {}
    for k, v in mapping.items():
        if v is None:
            values = defaults
        else:
            values = core.combine(defaults, v)
        if '[' in k:
            prefix, tail = k.split('[')
            hostrange = tail.rstrip(']')
            start, end = (int(v) for v in hostrange.split('-'))
            for h in range(start, end + 1):
                host = prefix + str(h)
                output[host] = values
        else:
            output[k] = values
    return output

class FilterModule(object):

    def filters(self):
        return {
            'expand_nodes': expand_nodes
        }
