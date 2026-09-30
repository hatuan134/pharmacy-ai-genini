"""Vietnam calendar windows, inclusive dates; never approximate months as 30 days."""
import re
from datetime import timedelta, date
from .config import today

def window(question, anchor=None):
    from .ai import plain
    s = plain(question); now = anchor or today()
    end = now
    pairs = re.search(r'tu\s+(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\s+(?:den|toi|-)\s*(\d{1,2})/(\d{1,2})(?:/(\d{4}))?', s)
    if pairs:
        d,m,y,d2,m2,y2 = pairs.groups()
        start=date(int(y or y2 or now.year),int(m),int(d));end=date(int(y2 or y or now.year),int(m2),int(d2))
        if end < start: raise ValueError('Ngày kết thúc phải sau ngày bắt đầu.')
        return start,end
    n = re.search(r'(\d{1,3})\s*ngay\s*(qua|toi|gan day)',s)
    if n:
        days=max(1,min(365,int(n[1])))
        return (now,now+timedelta(days=days)) if n[2]=='toi' else (now-timedelta(days=days-1),now)
    if 'hom qua' in s: return now-timedelta(days=1),now-timedelta(days=1)
    if 'hom nay' in s: return now,now
    if 'tuan truoc' in s:
        end=now-timedelta(days=now.weekday()+1);return end-timedelta(days=6),end
    if 'tuan nay' in s: return now-timedelta(days=now.weekday()),now
    if 'thang truoc' in s:
        end=now.replace(day=1)-timedelta(days=1);return end.replace(day=1),end
    if 'thang nay' in s: return now.replace(day=1),now
    if 'quy nay' in s: return date(now.year,3*((now.month-1)//3)+1,1),now
    return now-timedelta(days=29),now
