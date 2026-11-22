// YouTube Studio helpers (navigateur intégré). Après navigate vers …/videos/upload?d=ud :
// eval(localStorage.__up); eval(localStorage.__sch); eval(localStorage.__done);
// await __up('03/short1.mp4', title, desc, thumbPathOrNull); await __sch('24 nov. 2026','12:00'); await __done();
// Si localStorage vide, coller ce fichier dans la console (javascript_tool) une fois.
localStorage.setItem('__up', `window.__up=async(path,title,desc,thumb)=>{const W=ms=>new Promise(r=>setTimeout(r,ms)); const base='https://raw.githubusercontent.com/meralae0/quizrush-assets/main/episodes/';
const b=await (await fetch(base+path)).blob(); let inp; for(let k=0;k<20&&!(inp=document.querySelector('input[name=Filedata]'));k++) await W(500);
const dt=new DataTransfer(); dt.items.add(new File([b],path.split('/').pop(),{type:'video/mp4'})); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true}));
let boxes=[]; for(let k=0;k<40;k++){boxes=[...document.querySelectorAll('ytcp-uploads-dialog #textbox')]; if(boxes.length>=2) break; await W(500);} await W(2500);
const setT=(el,t)=>{el.focus(); document.execCommand('selectAll'); document.execCommand('insertText',false,t); el.dispatchEvent(new Event('input',{bubbles:true}));};
boxes=[...document.querySelectorAll('ytcp-uploads-dialog #textbox')]; setT(boxes[0],title); setT(boxes[1],desc);
if(thumb){const tb=await (await fetch(base+thumb)).blob(); const ti=document.querySelector('ytcp-uploads-dialog input[type=file][accept*=image]'); if(ti){const d2=new DataTransfer(); d2.items.add(new File([tb],'thumb.jpg',{type:'image/jpeg'})); ti.files=d2.files; ti.dispatchEvent(new Event('change',{bubbles:true}));}}
document.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]')?.click(); await W(1500);
boxes=[...document.querySelectorAll('ytcp-uploads-dialog #textbox')]; if(boxes[0].innerText.trim()!==title){setT(boxes[0],title);}
document.querySelector('#step-badge-3').click(); await W(2000);
const sch=[...document.querySelectorAll('ytcp-uploads-dialog *')].find(e=>e.children.length==0&&e.textContent.trim()==='Programmer'&&!e.closest('ytcp-button')); sch&&sch.click(); await W(1500);
return 'ok title='+boxes[0].innerText.trim().slice(0,40)+' sch='+!!sch;};`);
localStorage.setItem('__sch', `window.__sch=async(date,time)=>{const W=ms=>new Promise(r=>setTimeout(r,ms)); const dlg=document.querySelector('ytcp-uploads-dialog');
const trig=dlg.querySelector('ytcp-datetime-picker ytcp-text-dropdown-trigger, #datepicker-trigger'); trig.click(); await W(800);
const di=document.querySelector('ytcp-date-picker tp-yt-paper-input input'); di.focus(); di.select(); document.execCommand('insertText',false,date); di.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:13,bubbles:true})); di.dispatchEvent(new Event('change',{bubbles:true})); await W(800);
document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',keyCode:27,bubbles:true}));
const ti=[...dlg.querySelectorAll('ytcp-datetime-picker input')].find(i=>/^\\d\\d:\\d\\d$/.test(i.value)); ti.focus(); ti.select(); document.execCommand('insertText',false,time); ti.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:13,bubbles:true})); ti.dispatchEvent(new Event('change',{bubbles:true})); ti.blur(); await W(800);
return trig.innerText.trim()+' '+ti.value;};`);
localStorage.setItem('__done', `window.__done=async()=>{const W=ms=>new Promise(r=>setTimeout(r,ms)); document.querySelector('ytcp-uploads-dialog #done-button').click(); await W(2500);
const ok=[...document.querySelectorAll('ytcp-button, button')].find(b=>b.offsetParent&&/^OK$/i.test(b.innerText.trim())); ok&&ok.click(); await W(2500);
const l=document.body.innerText.match(/https:\\/\\/(youtu\\.be|youtube\\.com\\/shorts)\\/[\\w-]+/)?.[0];
const cl=[...document.querySelectorAll('ytcp-button')].find(b=>b.offsetParent&&/^Fermer$/.test(b.innerText.trim())); cl&&cl.click(); return l;};`);
