import React,{useEffect,useRef,useState} from 'react';
import {Bot,Send,Square,Copy,RefreshCw,ThumbsUp,ThumbsDown,Database,Sparkles} from 'lucide-react';
import {send,streamApi} from './api';

const toolNames={medicine_search:'Thuốc',inventory_search:'Lô & tồn kho',expiry_alerts:'Hạn dùng',low_stock:'Tồn thấp',stock_risk:'Tồn kho & hóa đơn 30/90 ngày',procedures:'Tài liệu quy trình',sales_summary:'Báo cáo bán hàng',system_data:'Dữ liệu nghiệp vụ',dynamic_query:'Truy vấn tổng hợp chỉ đọc'};
export default function AIChat({user,MarkdownMessage}){
  const [messages,setMessages]=useState([]),[question,setQuestion]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState(''),[activity,setActivity]=useState(''),[copied,setCopied]=useState(null);
  const controller=useRef(null),lock=useRef(false),end=useRef(null),active=useRef(null),mounted=useRef(true);
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;controller.current?.abort();if(active.current)send(`/ai/session/${active.current}/stop`,'POST',{}).catch(()=>{})}},[]);
  useEffect(()=>{end.current?.scrollIntoView?.({behavior:'smooth',block:'end'})},[messages,activity]);
  function fresh(){if(lock.current)return;setMessages([]);setQuestion('');setError('')}
  async function ask(e,text,base){
    e?.preventDefault();const q=(text??question).trim();if(!q||lock.current)return;
    lock.current=true;setBusy(true);setError('');setActivity('Đang mở cuộc trò chuyện…');
    const id=crypto.randomUUID();const temp=id;
    const control=new AbortController();controller.current=control;
    try{
      if(control.signal.aborted)return;
      active.current=id;setQuestion('');
      setMessages([...(base??messages),{role:'user',content:q},{id:temp,role:'assistant',content:'',streaming:true}]);
      const update=fn=>setMessages(old=>old.map(m=>m.clientId===temp||m.id===temp?fn({...m,clientId:temp}):m));
      await streamApi(`/ai/session/${id}/stream`,{method:'POST',signal:control.signal,body:JSON.stringify({message:q,agent:true,history:(base??messages).filter(m=>m.content&&!m.streaming&&m.status!=='stopped'&&m.status!=='interrupted').slice(-12).map(m=>({role:m.role,content:m.content.slice(0,4000)}))})},event=>{
        if(!mounted.current)return;
        if(event.type==='message')update(m=>({...m,id:event.id}));
        if(event.type==='activity')setActivity(event.text);
        if(event.type==='meta'){update(m=>({...m,sources:event.sources,tools:event.used_tools,route:event.route}));setActivity('Đã tra cứu dữ liệu. Đang tạo câu trả lời…')}
        if(event.type==='model')update(m=>({...m,model:event.model}));
        if(event.type==='delta'){setActivity('');update(m=>({...m,content:m.content+event.text}))}
        if(event.type==='error'){setError(event.text);update(m=>({...m,status:'interrupted'}))}
        if(event.type==='done')update(m=>({...m,streaming:false,status:event.status==='stopped'?'stopped':'complete',model:event.model||m.model,route:String(event.status).startsWith('fallback')?'fallback':m.route}));
      });
    }catch(e){if(e.name!=='AbortError')setError(e.message);setMessages(old=>old.map(m=>m.clientId===temp||m.id===temp?{...m,streaming:false,status:e.name==='AbortError'?'stopped':'interrupted'}:m))}
    finally{active.current=null;controller.current=null;lock.current=false;if(mounted.current){setMessages(old=>old.map(m=>(m.clientId===temp||m.id===temp)&&m.streaming?{...m,streaming:false,status:m.status||'interrupted'}:m));setBusy(false);setActivity('')}}
  }
  async function stop(){
    controller.current?.abort();
    const id=active.current;
    if(id)try{await send(`/ai/session/${id}/stop`,'POST',{})}catch(e){setError(e.message)}
  }
  async function regenerate(m){
    if(lock.current)return;
    const index=messages.findIndex(x=>x.id===m.id);
    if(index<1||messages[index-1].role!=='user')return;
    await ask(null,messages[index-1].content,messages.slice(0,index-1));
  }
  function vote(m,value){setMessages(old=>old.map(x=>x.id===m.id?{...x,feedback:x.feedback===value?0:value}:x))}
  function cleanAssistantText(text){return String(text??'').replace(/^\s*\*\s+/gm,'- ').replace(/\*/g,'')}
  async function copy(m){try{await navigator.clipboard.writeText(cleanAssistantText(m.content));setCopied(m.id);setTimeout(()=>setCopied(null),1800)}catch{setError('Không thể sao chép tự động. Bạn có thể chọn nội dung và nhấn Ctrl+C.')}}
  const suggestions=['Tình hình Paracetamol thế nào?','Thuốc nào tồn nhiều, bán chậm và gần hết hạn?','Thuốc nào chênh lệch giá nhập giữa các lô nhiều nhất?','Quy trình xử lý lô hết hạn'];
  return <div className="ai-workspace session-only">
    <section className="chat-shell panel agent-chat">
      <div className="chat-head"><div className="ai-avatar"><Bot/></div><div><h2>An Tâm AI</h2><p>Tra cứu nội bộ</p></div><button type="button" className="new-chat" disabled={busy} onClick={fresh}>Làm mới</button><span className="agent-status">{busy?'Đang trả lời':'Sẵn sàng'}</span></div>
      <div className="chat-body" aria-live="polite">
        {!messages.length&&<div className="ai-welcome"><div className="ai-avatar"><Sparkles size={30}/></div><h2>Tôi có thể giúp gì cho {user.name}?</h2><p>Hỏi về thuốc, tồn kho, doanh thu hoặc quy trình. Bạn có thể tiếp tục hỏi về cùng một thuốc trong cuộc trò chuyện.</p><div className="welcome-prompts">{suggestions.map(s=><button key={s} disabled={busy} onClick={()=>ask(null,s)}>{s}<span>↗</span></button>)}</div></div>}
        {messages.map((m,i)=><div key={m.clientId||m.id||i} className={'chat-row '+m.role}><div className="chat-bubble">
          {m.role==='assistant'&&<div className="bubble-top"><div className="bubble-name"><Sparkles size={16}/> An Tâm AI</div><span className={'answer-mode '+(m.route||'direct')}>{m.route==='fallback'?'AI không khả dụng · dữ liệu đã tra cứu':m.model&&m.model!=='backend-direct'&&m.model!=='backend-fallback'?'AI · '+m.model:'Trợ lý nội bộ'}</span></div>}
          <div className="chat-text"><MarkdownMessage text={m.content}/></div>
          {m.streaming&&!m.content&&<p className="agent-working">{activity||'Đang chuẩn bị phản hồi…'}</p>}
          {m.tools?.length>0&&<div className="tool-chips"><b>Đã tra cứu:</b>{m.tools.map(t=><span key={t}><Database size={13}/>{toolNames[t]||t}</span>)}</div>}
          {m.sources?.length>0&&<details className="chat-sources"><summary>Nguồn dữ liệu · {m.sources.length}</summary><div>{m.sources.map((s,j)=><span key={s.id+j}><Database size={13}/>{s.title}<small>{s.reference}</small></span>)}</div></details>}
          {['stopped','interrupted','generating'].includes(m.status)&&!m.streaming&&<small className="response-stopped">{m.status==='stopped'?'Đã dừng trả lời.':'Phản hồi chưa hoàn tất.'}</small>}
          {m.role==='assistant'&&!m.streaming&&m.id&&<div className="answer-actions"><button onClick={()=>copy(m)} title="Sao chép"><Copy size={15}/>{copied===m.id?'Đã sao chép':'Sao chép'}</button><button disabled={busy} onClick={()=>regenerate(m)} title="Tạo lại câu trả lời"><RefreshCw size={15}/>Tạo lại</button><button aria-label="Hữu ích" aria-pressed={m.feedback===1} onClick={()=>vote(m,1)}><ThumbsUp size={15}/></button><button aria-label="Chưa hữu ích" aria-pressed={m.feedback===-1} onClick={()=>vote(m,-1)}><ThumbsDown size={15}/></button></div>}
        </div></div>)}<div ref={end}/>
      </div>
      {error&&<div className="error" role="alert">{error}</div>}
      <form className="chat-composer" onSubmit={ask}><textarea rows={2} maxLength={2000} placeholder="Nhắn tin cho An Tâm AI…" value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing){e.preventDefault();ask(e)}}}/>{busy?<button type="button" className="stop-button" onClick={stop}><Square size={17}/>Dừng trả lời</button>:<button className="send-button" disabled={!question.trim()} aria-label="Gửi"><Send size={20}/></button>}</form>
      <div className="chat-disclaimer">AI chỉ hỗ trợ tham khảo, không tư vấn dùng thuốc thay dược sĩ/bác sĩ.</div>
    </section>
  </div>
}
