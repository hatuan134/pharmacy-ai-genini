"""Opt-in live smoke check: synthetic data only, no pharmacy DB reads."""
import os,sys,json,time
from pathlib import Path
from datetime import datetime,timezone
from types import SimpleNamespace

root=Path(__file__).resolve().parents[1]
os.chdir(root/'backend')
sys.path.insert(0,str(root/'backend'))
from app.config import settings
from app.schemas import AIChatRequest
from app.ai import _gemini_stream_events
if not settings.gemini_api_key:
    raise SystemExit('Chưa cấu hình GEMINI_API_KEY trong backend/.env.')
request=AIChatRequest(message='Tóm tắt thông tin thuốc giả lập, nhắc rõ không thay dược sĩ. Đây chỉ là kiểm thử kết nối.',history=[],agent=True)
results=[{'tool':'medicine_search','data':[{'id':0,'code':'DEMO-ONLY','name':'Thuốc mô phỏng kiểm thử','information':'Dữ liệu giả lập đã xác nhận: bảo quản theo nhãn sản phẩm. Không có thông tin liều dùng.','source':'Fixture kiểm thử, không phải hồ sơ thật'}]}]
started=time.monotonic();report={'time_utc':datetime.now(timezone.utc).isoformat(),'synthetic_only':True,'status':'failed','model':None,'first_token_seconds':None,'answer':''}
for kind,value in _gemini_stream_events(request,SimpleNamespace(role='manager'),results):
    if kind=='model':report['model']=value
    elif kind=='delta':
        if report['first_token_seconds'] is None:report['first_token_seconds']=round(time.monotonic()-started,2)
        report['answer']+=value
    elif kind=='error':report['error']=value
report['total_seconds']=round(time.monotonic()-started,2)
if report['answer'] and 'error' not in report:report['status']='passed_connection_only'
folder=root/'evidence';folder.mkdir(exist_ok=True)
output=folder/'gemini_live_result.json';output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Đã lưu evidence/gemini_live_result.json; trạng thái:',report['status'])
print('Đây chỉ là kiểm tra kết nối/streaming. Cần đọc và đánh giá nội dung trả lời riêng.')
raise SystemExit(0 if report['status']=='passed_connection_only' else 1)
