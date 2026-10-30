"""Single presentation status derived from requests, durable project and engine."""
import time

STATUSES=('Ready','Working','Waiting for User','Waiting for Approval','Completed','Stopped','Error')


def pending(requests,permissions,now=None):
    now=time.monotonic() if now is None else now
    return [r for r in requests if not r['event'].is_set() and r['generation']==permissions.generation and not permissions.halted.is_set() and now<=r.get('deadline',now+1)]


def resolve(task=None,project=None,requests=(),active=False):
    if requests:return 'Waiting for User' if any(r['args'].get('manual_step') for r in requests) else 'Waiting for Approval'
    if project:
        state=project['state'];counts=project.get('counts',{})
        if state=='running':return 'Working'
        if state in ('paused','cancelled'):return 'Stopped'
        if state=='blocked' or counts.get('failed') or counts.get('review') or counts.get('blocked'):return 'Error'
        if state=='completed':return 'Completed' if project.get('total',0)>0 and counts.get('completed',0)==project['total'] else 'Error'
        if state=='draft':return 'Working' if active else 'Ready'
    if active:return 'Working'
    state=(task or {}).get('status','Ready')
    if state in STATUSES:return state
    if state in ('Thinking','Acting'):return 'Working'
    if state=='Waiting for approval':return 'Waiting for Approval'
    if state.startswith(('Review','Error')):return 'Error'
    if state.startswith(('Paused','Stop')):return 'Stopped'
    return 'Ready'
