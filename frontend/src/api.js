export async function api(path, options={}) {
  const response = await fetch('/api'+path, {credentials:'include', ...options, headers:{'Content-Type':'application/json','X-Requested-With':'pharmacy',...options.headers}});
  const data = await response.json().catch(()=>({detail:'Máy chủ không phản hồi đúng. Kiểm tra cửa sổ backend.'}));
  if (!response.ok) {
    if(response.status === 401 && path !== '/auth/login') window.dispatchEvent(new Event('session-expired'));
    const message = Array.isArray(data.detail) ? data.detail.map(x=>`${x.loc.slice(1).join('.')}: ${x.msg}`).join('; ') : data.detail;
    const error = new Error(message || 'Không thể thực hiện thao tác.');
    error.status = response.status;
    throw error;
  }
  return data;
}

export async function streamApi(path, options={}, onEvent=()=>{}) {
  const response = await fetch('/api'+path, {
    credentials:'include',
    ...options,
    headers:{'Content-Type':'application/json','X-Requested-With':'pharmacy',...options.headers}
  });
  if (!response.ok) {
    const data = await response.json().catch(()=>({detail:'Máy chủ không phản hồi đúng. Kiểm tra cửa sổ backend.'}));
    if(response.status === 401 && path !== '/auth/login') window.dispatchEvent(new Event('session-expired'));
    const message = Array.isArray(data.detail) ? data.detail.map(x=>`${x.loc.slice(1).join('.')}: ${x.msg}`).join('; ') : data.detail;
    const error = new Error(message || 'Không thể thực hiện thao tác.');
    error.status = response.status;
    throw error;
  }
  if (!response.body) throw new Error('Trình duyệt không hỗ trợ phản hồi streaming.');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer='';
  while(true){
    const {value,done}=await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), {stream:!done});
    const lines=buffer.split(/\r?\n/);
    buffer=lines.pop() || '';
    for(const line of lines){
      if(!line.trim())continue;
      try{onEvent(JSON.parse(line))}catch(e){console.warn('AI stream packet không hợp lệ',e,line)}
    }
    if(done)break;
  }
  if(buffer.trim()){
    try{onEvent(JSON.parse(buffer))}catch(e){console.warn('AI stream packet cuối không hợp lệ',e,buffer)}
  }
}

export const send = (path, method, value) => api(path,{method,body:JSON.stringify(value)});
export const money = value => new Intl.NumberFormat('vi-VN',{style:'currency',currency:'VND',maximumFractionDigits:0}).format(Number(value || 0));
export const date = value => value ? new Date(value.length === 10 ? value+'T12:00:00' : value).toLocaleDateString('vi-VN') : '—';
export const localToday = () => new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
