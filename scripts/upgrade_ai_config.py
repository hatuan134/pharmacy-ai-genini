"""Update only AI model settings, preserving DB, session secret and API key."""
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'backend'/'.env'
if not path.exists():
    raise SystemExit('Chưa có backend/.env. Chạy py scripts/setup.py trước, rồi cấu hình database và Gemini.')
values={
 'GEMINI_MODEL':'gemini-3.5-flash-lite',
 'GEMINI_FALLBACK_MODELS':'gemini-3.1-flash-lite,gemini-2.5-flash-lite',
 'GEMINI_RETRY_ATTEMPTS':'1',
}
lines=path.read_text(encoding='utf-8-sig').splitlines();seen=set();output=[]
for line in lines:
    key=line.split('=',1)[0].strip()
    if key in values:
        if key not in seen:output.append(key+'='+values[key]);seen.add(key)
    else:output.append(line)
for key,value in values.items():
    if key not in seen:output.append(key+'='+value)
path.write_text('\n'.join(output)+'\n',encoding='utf-8')
print('Đã cập nhật model AI. Giữ nguyên API key và cấu hình database.')
