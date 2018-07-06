import re
import shlex

ini = '''
[atlanta]
host1 123="45632" 567=890 #Comment
host2 a="b"

    # comment
[raleigh]
host1 port="45632" #Comment
host4 ansible_ssh_port=2233
host3

[southeast:children]
atlanta
raleigh

[southeast:vars]
some_server="foo.southeast.example.com" # comment
halon_system_timeout=30
self_destruct_countdown=60
escape_pods=2

[usa:children]
southeast
northeast

'''


def serializer(data):
    _json = {"_meta": {"hostvars": {}}}
    parser = re.compile(
                r'''^\[
                        ([^:\]\s]+)             # group name (see groupname below)
                        (?::(\w+))?             # optional : and tag name
                    \]
                    \s*                         # ignore trailing whitespace
                    (?:\#.*)?                   # and/or a comment till the
                    $                           # end of the line
                ''', re.X
    )

    state = None
    groupname = ''
    for row in data.split('\n'):
        row = row.strip()
        if row == '' or row.startswith(";") or row.startswith("#"):
            continue
        m = parser.match(row)
        if m:
            (groupname, state) = m.groups()
            state = state or 'hosts'
            if groupname not in _json:
                _json[groupname] = {}
        else:
            if state is None:
                raise ValueError('invalid data')
            a = shlex.split(row, comments=True)
            if state == 'children':
                _json[groupname].setdefault(state, []).append(a[0])
            elif state == 'vars':
                _json[groupname].setdefault(state, {})
                (var, val) = a[0].split("=")
                _json[groupname][state][var] = val
            elif state == 'hosts':
                host = a[0]
                _json[groupname].setdefault(state, []).append(host)
                if row.find(" ") != -1:
                    _json["_meta"]["hostvars"].setdefault(host, {})
                    for i in range(1, len(a)):
                        (var, val) = a[i].split("=")
                        _json["_meta"]["hostvars"][host][var] = val
    return _json
