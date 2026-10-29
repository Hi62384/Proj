"""Strict Chrome native-message framing. Never write diagnostics to stdout."""
import json
import struct

VERSION=1
MAX_MESSAGE=1024*1024-1


class ProtocolError(ValueError):
    pass


def read_exact(stream,size):
    chunks=[]
    while size:
        chunk=stream.read(size)
        if not chunk:raise ProtocolError('Truncated native message')
        chunks.append(chunk);size-=len(chunk)
    return b''.join(chunks)


def read_message(stream):
    first=stream.read(1)
    if not first:return None
    size=struct.unpack('<I',first+read_exact(stream,3))[0]
    if not 0<size<=MAX_MESSAGE:raise ProtocolError('Native message exceeds the supported bound')
    try:
        def unique(pairs):
            value={}
            for key,item in pairs:
                if key in value:raise ProtocolError('Duplicate message field')
                value[key]=item
            return value
        value=json.loads(read_exact(stream,size).decode('utf-8'),object_pairs_hook=unique,
                         parse_constant=lambda _:(_ for _ in ()).throw(ProtocolError('Nonfinite JSON number')))
    except (UnicodeError,ValueError,RecursionError) as error:raise ProtocolError('Invalid native JSON message') from error
    if not isinstance(value,dict):raise ProtocolError('Native message must be an object')
    return value


def write_message(stream,value):
    if not isinstance(value,dict):raise ProtocolError('Native message must be an object')
    try:raw=json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
    except (ValueError,TypeError,RecursionError) as error:raise ProtocolError('Invalid native JSON message') from error
    if not 0<len(raw)<=MAX_MESSAGE:raise ProtocolError('Native message exceeds the supported bound')
    stream.write(struct.pack('<I',len(raw))+raw);stream.flush()
