"""Official MCP SDK stdio entrypoint. stdout contains MCP messages only."""
import asyncio
import base64
import json
import sys
import uuid
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool,TextContent,ImageContent,ToolAnnotations
from assistant.tools import CAPABILITIES,TOOL
from bridge.client import ControllerClient

server=Server('codex-computer-bridge');client=ControllerClient()
BRIDGE={name:'bridge_'+name for name in ('status','health','capabilities','start_services','open_dashboard','get_active_work','get_pending_requests','stop','history','reason_tasks','reason_result','get_artifact')}
BRIDGE.update({name:'bridge_'+name for name in ('start_local_business_test','start_local_builder_test','local_test_state')})
BRIDGE['wait_ready']='bridge_wait_ready'
BRIDGE['verify_saved_payhip']='bridge_verify_saved_payhip'
OPERATIONS={cap.replace('.','_'):cap for cap in CAPABILITIES}
OPERATIONS.update({value:value for value in BRIDGE.values()})


def description(name,operation):
    if operation=='chrome.open_tab':return 'Open an HTTP(S) URL in the authorized Chrome scope. Reuses an existing EXACT-URL tab without reloading it or moving focus; creates a background tab only when absent. Returns tab, reused, created, authorized. Do not close reused tabs as temporary cleanup: they may contain human work. An existing tab in manual control stays protected. Restricted sites still require their original Chrome permission. Inspect before acting; local consequential-action approvals remain enforced.'
    if operation.startswith('bridge_'):
        if operation=='bridge_start_local_business_test':return 'Create a disposable LOCAL storefront and host-bound zero-spending five-product test scope. Returns store ID, five exact recipe specifications and prices. Use projects_create, projects_products with that store and those products, projects_start, projects_wait, result and deliver to finish actual generation/native QA/package/local publication/verification. This cannot authorize any real website.'
        if operation=='bridge_start_local_builder_test':return 'Create a disposable localhost custom-control builder with the exact unpublished Save draft scope. Returns its URL. Use Chrome tools to edit About text, color swatches/color input, custom layout and hover spacing controls, then Save draft. Publish and Pay now remain protected. Does not grant real account writes.'
        return {'bridge_status':'Actual Windows controller, MCP heartbeat, Chrome connection and owner authorization state. Does not imply browser readiness from process existence.','bridge_stop':'Emergency Stop: immediately revoke input and project launch scopes. Resume is owner-only in the local dashboard.','bridge_history':'Read preserved historical conversation metadata and project summaries; never start the old AI engine.','bridge_reason_tasks':'Get pending reasoning jobs for OFFICIAL CODEX to perform. There is no hidden reasoning service.','bridge_reason_result':'Record official Codex reasoning output for an owned pending reasoning job. This cannot certify files, publication or deterministic QA.'}.get(operation,'Codex Computer Bridge: '+operation.removeprefix('bridge_').replace('_',' ')+'. Local authorization remains enforced; model text cannot grant permissions.')
    import re
    text=TOOL['description'];match=re.search(re.escape(operation)+r'(?=[: /])',text)
    if match:
        paragraph=text[match.start():];following=re.search(r'\b(?:chrome|projects|desktop|files|browser|human|attachments)\.[a-z_]+',paragraph[len(operation):])
        if following:paragraph=paragraph[:len(operation)+following.start()]
        return paragraph[:1800]+' All owner-controlled local permissions remain enforced. Inspect and verify effects.'
    return operation+' uses validated structured arguments. Existing local desktop, browser and file permissions apply. No shell, arbitrary JavaScript or model-authored authorization.'


def schema(operation):
    if operation=='bridge_wait_ready':return {'type':'object','properties':{'arguments':{'type':'object','properties':{'seconds':{'type':'integer','minimum':1,'maximum':25}},'required':['seconds'],'additionalProperties':False}},'required':['arguments'],'additionalProperties':False}
    if operation.startswith('bridge_') and operation not in ('bridge_reason_result','bridge_get_artifact','bridge_wait_ready'):return {'type':'object','properties':{},'additionalProperties':False}
    # Tool identity is server-defined; callers cannot substitute another capability.
    return {'type':'object','properties':{'arguments':{'type':'object','description':'Structured arguments documented in this tool. No executable code or permission override fields.'}},'required':['arguments'],'additionalProperties':False}


@server.list_tools()
async def list_tools():
    try:
        server.request_context  # real initialized MCP request, not a metadata unit test
        await asyncio.to_thread(client.request,'bridge_mcp_connected')
    except LookupError:pass
    readonly={'bridge_status','bridge_health','bridge_capabilities','bridge_get_active_work','bridge_get_pending_requests','bridge_history','bridge_reason_tasks','chrome.list_tabs','chrome.list_windows','chrome.inspect','chrome.frames','files.read','files.list','projects.list','projects.status','projects.result'}
    return [Tool(name=name,description=description(name,operation),inputSchema=schema(operation),annotations=ToolAnnotations(readOnlyHint=operation in readonly,destructiveHint=operation not in readonly,openWorldHint=operation.startswith(('chrome.','browser.','desktop.')))) for name,operation in OPERATIONS.items()]


@server.call_tool()
async def call_tool(name,arguments):
    if name not in OPERATIONS:raise ValueError('Unknown computer bridge tool')
    operation=OPERATIONS[name];arguments=arguments or {}
    data={} if operation.startswith('bridge_') and operation not in ('bridge_reason_result','bridge_get_artifact','bridge_wait_ready') else arguments['arguments']
    await asyncio.to_thread(client.ensure)  # preflight/recover before dispatch, never replay an action
    await asyncio.to_thread(client.request,'bridge_mcp_connected')
    request_id=uuid.uuid4().hex
    try:value=await asyncio.to_thread(client.request,operation,data,request_id)
    except asyncio.CancelledError:
        await asyncio.shield(asyncio.to_thread(client.request,'bridge_cancel_call',{'request':request_id}))
        raise
    if isinstance(value,dict) and 'content' in value:
        result=[]
        for item in value['content']:
            if item.get('type')=='inputImage':
                header,raw=item['imageUrl'].split(',',1);result.append(ImageContent(type='image',mimeType=header[5:].split(';')[0],data=raw))
            else:result.append(TextContent(type='text',text=item.get('text','')))
        return result
    return [TextContent(type='text',text=json.dumps(value,ensure_ascii=False))]


async def main():
    await asyncio.to_thread(client.ensure);client.start_heartbeat()
    try:
        async with stdio_server() as (read,write):await server.run(read,write,server.create_initialization_options())
    finally:client.close()


if __name__=='__main__':asyncio.run(main())
