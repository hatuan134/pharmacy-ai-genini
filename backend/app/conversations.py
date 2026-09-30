"""Ephemeral generation control only. No conversation storage or titles."""
import json
from threading import Event, Lock
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from .auth import ai_user
from .db import get_db
from .schemas import AIChatRequest
from . import ai

router=APIRouter(prefix='/api/ai/session')
_running={}
_lock=Lock()

@router.post('/{request_id}/stop')
def stop(request_id:UUID,user=Depends(ai_user)):
    with _lock:
        entry=_running.get(str(request_id))
        if entry and entry[0]==user.id:entry[1].set()
    return {'status':'stopping'}

@router.post('/{request_id}/stream')
def stream(request_id:UUID,data:AIChatRequest,user=Depends(ai_user),db=Depends(get_db)):
    from .main import rate_limit
    rate_limit('ai-session:'+str(user.id),15,60)
    key=str(request_id);event=Event()
    with _lock:
        if key in _running:raise HTTPException(409,'Yêu cầu đang được xử lý.')
        _running[key]=(user.id,event)
    data.agent=True
    data._cancelled=event.is_set
    def packets():
        gen=None
        try:
            gen=ai.chat_stream(db,data,user)
            for raw in gen:
                if event.is_set():
                    yield json.dumps({'type':'done','status':'stopped'})+'\n'
                    return
                yield raw
        except GeneratorExit:raise
        except Exception:
            yield json.dumps({'type':'error','text':'Phản hồi bị gián đoạn. Bạn có thể tạo lại câu trả lời.'},ensure_ascii=False)+'\n'
        finally:
            if gen:gen.close()
            db.close()
            with _lock:_running.pop(key,None)
    return StreamingResponse(packets(),media_type='application/x-ndjson',headers={'X-Accel-Buffering':'no','Cache-Control':'no-store'})
