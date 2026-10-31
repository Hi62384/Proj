// Focus/key notifications and DOM pointer coordinates; no live browser access.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../chrome_extension/content.js',import.meta.url),'utf8');
const events=[];
class Event {constructor(type,init={}){this.type=type;Object.assign(this,init);}}
class Input {
 constructor(){Object.assign(this,{tagName:'INPUT',type:'text',name:'ordinary',id:'notes',autocomplete:'',placeholder:'Notes',innerText:'',parentElement:null,isConnected:true,disabled:false,checked:false,labels:[],isContentEditable:false,_value:''});}
 get value(){return this._value;}
 set value(value){assert.equal(this.focused,true,'Widget focus must initialize before its value changes');this._value=value;}
 getAttribute(){return null;}
 closest(){return null;}
 getBoundingClientRect(){return {x:20,y:40,width:100,height:30};}
 focus(){this.focused=true;}
 matches(){return false;}
 dispatchEvent(event){events.push(event);return true;}
}
const document={addEventListener(){},removeEventListener(){},querySelectorAll(){return []},body:{innerText:''}};
let timerYields=0;
const context=vm.createContext({document,location:{href:'https://example.org/edit',pathname:'/edit'},setTimeout(resolve){timerYields++;resolve();},chrome:{runtime:{onMessage:{addListener(){}}}},HTMLInputElement:Input,HTMLTextAreaElement:Input,InputEvent:Event,KeyboardEvent:Event,MouseEvent:Event,PointerEvent:Event,Event,URL,URLSearchParams,getComputedStyle:e=>({...e.style,display:'block',visibility:'visible'}),console});
context.window=context;
vm.runInContext(source.replace('chrome.runtime.onMessage.addListener(messageHandler);',`globalThis.test={action,dragSection,presentation,setup(e,end){grant={origin:new URL(location.href).origin.replace(/$/,location.href.startsWith('https:')?':443':':80')};elements=end?[e,end]:[e];observation='fresh';observedAt=Date.now();observedRevision=revision;signatures=elements.map(signature);}};`),context);
const input=new Input();context.test.setup(input);
context.test.action({observation:'fresh',element:0,action:'fill',text:'First line\nSecond line'});
assert.equal(input.value,'First line\nSecond line');assert.deepEqual(events.map(e=>e.type),['input','change','keyup']);assert.equal(events.at(-1).key,'Unidentified');assert.equal(events.some(e=>e.key==='Enter'),false,'Typing must never introduce form submission');
events.length=0;context.test.setup(input);
context.test.action({observation:'fresh',element:0,action:'click',method:'pointer'});
assert.equal(events.at(-1).type,'click');assert.equal(events.every(e=>e.clientX===70&&e.clientY===55),true,'Pointer notifications use the actual target center');
console.log('PASS: widget focus, multiline text, non-submit key notification and bounded pointer coordinates');

// A background tab may clamp each timer to one second. Keep the drag under
// the 15-second dispatch timeout while preserving all intermediate moves.
events.length=0;
const list={};
class Section extends Input {
 closest(selector){if(selector==='.js-section')return this;if(selector==='.js-draggable-sections-wrapper')return list;return null;}
 querySelector(){return this.handle;}
}
const from=new Section(),to=new Section();from.handle=new Input();
document.elementFromPoint=()=>to;
Object.assign(context.location,{href:'https://payhip.com/builder/public',origin:'https://payhip.com',pathname:'/builder/public'});
context.test.setup(from,to);
await context.test.dragSection({observation:'fresh',element:0,end_element:1});
assert.equal(timerYields,4,'Background drag must not wait on sixteen throttled timers');
assert.equal(events.filter(e=>e.type==='mousemove').length,16);
assert.equal(events.at(-1).type,'mouseup');
context.location.pathname='/products';context.test.setup(from,to);
await assert.rejects(context.test.dragSection({observation:'fresh',element:0,end_element:1}),/same Payhip draft list/);
console.log('PASS: bounded background drag and exact draft-page restriction');

const painted=new Input();painted.style={backgroundColor:'rgb(16, 43, 63)'};const transparent=new Input();transparent.style={backgroundColor:'rgba(0, 0, 0, 0)',color:'rgb(255, 255, 255)'};transparent.parentElement=painted;
assert.equal(context.test.presentation(transparent).ancestor_background,'rgb(16, 43, 63)');assert.equal(context.test.presentation(transparent).color,'rgb(255, 255, 255)');console.log('PASS: read-only ancestor paint metadata');
