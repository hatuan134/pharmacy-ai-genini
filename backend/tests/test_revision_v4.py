import json
from uuid import uuid4
from sqlalchemy import select,func
from app import ai,agent
from app.models import Medicine,User,AILog,AIConversation,AIMessage
from app.schemas import AIChatRequest


def test_approval_permissions_stale_revision_and_invalidation(setup):
    c,S,ids,tokens=setup
    m=c.get('/api/medicines').json()[0]
    c.cookies.set('session',tokens['cashier'])
    assert c.post(f'/api/medicines/{m["id"]}/approval',json={'approved':True,'revision':m['approval_revision']}).status_code==403
    c.cookies.set('session',tokens['pharmacist'])
    result=c.post(f'/api/medicines/{m["id"]}/approval',json={'approved':True,'revision':m['approval_revision']})
    assert result.status_code==200 and result.json()['approved_by']
    fields=['code','name','category_id','unit_id','min_stock','prescription_required','active','information','source']
    payload={k:m[k] for k in fields};payload['information']='Nội dung thay đổi'
    result=c.put(f'/api/medicines/{m["id"]}',json=payload)
    assert result.status_code==200 and not result.json()['approved']
    assert c.post(f'/api/medicines/{m["id"]}/approval',json={'approved':True,'revision':m['approval_revision']}).status_code==409
    current=result.json()
    assert c.post(f'/api/medicines/{m["id"]}/approval',json={'approved':True,'revision':current['approval_revision']}).status_code==200


def test_unapproved_text_never_in_tool_or_legacy_summary(setup):
    c,S,ids,_=setup
    with S() as db:
        m=db.get(Medicine,ids['medicine']);m.approved=False;m.information='UNAPPROVED_SENTINEL';db.commit()
        rows,sources=ai._tool_medicine_search(db,m.code)
        assert rows==[] and sources==[]
    assert c.post('/api/ai/ask',json={'mode':'summary','medicine_id':ids['medicine']}).status_code==422


def test_summary_keeps_medicine_tool_not_inventory_only(setup,monkeypatch):
    _,S,ids,_=setup
    monkeypatch.setattr(agent,'generate_json',lambda *a,**kw:{'calls':[{'name':'inventory_search','query':'M1'}]})
    with S() as db:
        user=db.scalar(select(User).where(User.role=='manager'))
        result=agent.prepare(db,AIChatRequest(message='Tóm tắt thông tin M1',agent=True),user)
        found=next(x for x in result['results'] if x['tool']=='medicine_search')
        assert found['data'][0]['information']==' '.join(db.get(Medicine,ids['medicine']).information.split())
        m=db.get(Medicine,ids['medicine']);m.approved=False;db.commit()
        result=agent.prepare(db,AIChatRequest(message='Tóm tắt thông tin M1',agent=True),user)
        assert result['terminal'] and 'chưa được duyệt' in result['message']


def test_session_chat_no_persistence_no_title_and_removed_history(setup,monkeypatch):
    c,S,ids,_=setup
    from app.config import settings
    monkeypatch.setattr(settings,'gemini_api_key','')
    response=c.post(f'/api/ai/session/{uuid4()}/stream',json={'message':'Quy trình nhập lô?','history':[]})
    assert response.status_code==200
    events=[json.loads(line) for line in response.text.splitlines()]
    assert not any(x['type']=='title' for x in events)
    assert 'không khả dụng' in ''.join(x.get('text','') for x in events)
    with S() as db:
        for model in [AILog,AIMessage,AIConversation]:assert db.scalar(select(func.count()).select_from(model))==0
    assert c.get('/api/ai/conversations').status_code==404


def test_stop_is_owner_scoped_and_cleans_registry(setup,monkeypatch):
    from app.conversations import _running
    c,S,ids,tokens=setup
    def fake(db,request,user):
        yield json.dumps({'type':'delta','text':'first'})+'\n'
        for owner,event in _running.values():event.set()
        yield json.dumps({'type':'delta','text':'second'})+'\n'
    monkeypatch.setattr(ai,'chat_stream',fake)
    result=c.post(f'/api/ai/session/{uuid4()}/stream',json={'message':'test'})
    assert 'first' in result.text and 'second' not in result.text and not _running
    from threading import Event
    key=str(uuid4());event=Event();_running[key]=(999,event)
    try:
        c.post(f'/api/ai/session/{key}/stop',json={})
        assert not event.is_set()
    finally:_running.pop(key,None)


def test_approval_migration_once_only(setup):
    from app.migrations import apply
    _,S,ids,_=setup
    with S() as db:
        apply(db);db.expire_all()
        m=db.get(Medicine,ids['medicine']);assert not m.approved
        m.approved=True;db.commit()
        apply(db);db.expire_all();assert db.get(Medicine,ids['medicine']).approved
