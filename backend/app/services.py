import hashlib, json
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, time, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy import select, func
from .models import *
from .config import today



def require(db, cls, ident):
    obj = db.get(cls, ident)
    if not obj:
        raise HTTPException(404, 'Không tìm thấy dữ liệu.')
    return obj

def approval_revision(obj):
    import hashlib, json
    fields = ('code','name','category_id','unit_id','information','source','prescription_required','active')
    return hashlib.sha256(json.dumps({k:getattr(obj,k) for k in fields},sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def row(obj):
    result = {c.name:getattr(obj,c.name) for c in obj.__table__.columns if c.name != 'password_hash'}
    if isinstance(obj, Medicine): result['approval_revision'] = approval_revision(obj)
    return result


def movement(db, batch, user, delta, kind, reason='', invoice_id=None):
    db.add(Movement(batch_id=batch.id, user_id=user.id, delta=delta, balance=batch.quantity, kind=kind, reason=reason, invoice_id=invoice_id))

def batch_rows(db, q='', category_id=None, expiry_before=None, available=False):
    stmt = select(Batch, Medicine, Unit, Supplier).join(Medicine, Batch.medicine_id == Medicine.id).join(Unit, Medicine.unit_id == Unit.id).join(Supplier, Batch.supplier_id == Supplier.id)
    if q:
        stmt = stmt.where(Medicine.name.ilike(f'%{q}%') | Medicine.code.ilike(f'%{q}%') | Batch.code.ilike(f'%{q}%'))
    if category_id:
        stmt = stmt.where(Medicine.category_id == category_id)
    if expiry_before:
        stmt = stmt.where(Batch.expiry_date <= expiry_before)
    if available:
        stmt = stmt.where(Batch.quantity > 0, Batch.expiry_date > today(), Medicine.active.is_(True))
    return [{**row(b), 'medicine_name': m.name, 'medicine_code': m.code, 'unit': u.name, 'supplier_name': s.name, 'prescription_required': m.prescription_required, 'days_left': (b.expiry_date-today()).days} for b,m,u,s in db.execute(stmt.order_by(Batch.expiry_date, Batch.id))]

def alerts(db, days=90):
    batches = [b for b in batch_rows(db, expiry_before=today()+timedelta(days=days)) if b['quantity'] > 0]
    counts = defaultdict(int)
    for b in batch_rows(db, available=True):
        counts[b['medicine_id']] += b['quantity']
    low = [{**row(m), 'available_stock': counts[m.id]} for m in db.scalars(select(Medicine).where(Medicine.active.is_(True))) if counts[m.id] < m.min_stock]
    return {'expiry': batches, 'low_stock': low, 'as_of': today()}


def paid_sales_summary(db, start, end):
    """Return one canonical paid-sales calculation for reports and AI.

    Revenue is reconstructed from the historical invoice line items whenever
    they are present (quantity × sale_price at the time of sale).  The stored
    invoice total is only a fallback for legacy rows without line items.  Using
    this helper from both the Reports screen and An Tâm AI prevents the two
    places from showing different revenue for the same date range.
    """
    if start > end:
        raise HTTPException(422, 'Ngày bắt đầu phải trước ngày kết thúc.')

    from zoneinfo import ZoneInfo

    zone = ZoneInfo('Asia/Ho_Chi_Minh')
    lower = datetime.combine(start, time.min, zone).astimezone(timezone.utc)
    upper = datetime.combine(end + timedelta(days=1), time.min, zone).astimezone(timezone.utc)
    invoices = list(db.scalars(
        select(Invoice)
        .where(Invoice.status == 'paid', Invoice.created_at >= lower, Invoice.created_at < upper)
        .order_by(Invoice.created_at, Invoice.id)
    ))

    if not invoices:
        return {
            'start': start,
            'end': end,
            'revenue': Decimal(0),
            'invoice_count': 0,
            'invoices': [],
        }

    invoice_ids = [invoice.id for invoice in invoices]
    item_rows = db.execute(
        select(
            InvoiceItem.invoice_id,
            func.sum(InvoiceItem.quantity * InvoiceItem.sale_price),
        )
        .where(InvoiceItem.invoice_id.in_(invoice_ids))
        .group_by(InvoiceItem.invoice_id)
    ).all()
    item_totals = {invoice_id: (total or Decimal(0)) for invoice_id, total in item_rows}

    details = []
    revenue = Decimal(0)
    for invoice in invoices:
        # Line items are the detailed historical sale record.  Keep support for
        # legacy/imported invoices that might not have item rows.
        calculated_total = item_totals.get(invoice.id)
        effective_total = calculated_total if calculated_total is not None else invoice.total
        revenue += effective_total
        details.append({
            'id': invoice.id,
            'created_at': invoice.created_at,
            'total': effective_total,
            'stored_total': invoice.total,
        })

    return {
        'start': start,
        'end': end,
        'revenue': revenue,
        'invoice_count': len(invoices),
        'invoices': details,
    }

def invoice_detail(db, invoice):
    return {**row(invoice), 'items': [row(i) for i in db.scalars(select(InvoiceItem).where(InvoiceItem.invoice_id == invoice.id))], 'seller': require(db, User, invoice.user_id).name}

def create_sale(db, data, user):
    fingerprint = hashlib.sha256(json.dumps(data.model_dump(mode='json', exclude={'request_key'}), sort_keys=True).encode()).hexdigest()
    # Serialize retries for the same operator; batch locks serialize different operators.
    db.scalar(select(User).where(User.id == user.id).with_for_update())
    previous = db.scalar(select(Invoice).where(Invoice.request_key == data.request_key))
    if previous:
        if previous.user_id != user.id or previous.request_hash != fingerprint:
            raise HTTPException(409, 'Mã thanh toán đã dùng cho yêu cầu khác.')
        return invoice_detail(db, previous)
    amounts = defaultdict(int)
    for item in data.items:
        amounts[item.batch_id] += item.quantity
    batches = list(db.scalars(select(Batch).where(Batch.id.in_(sorted(amounts))).order_by(Batch.id).with_for_update()))
    if len(batches) != len(amounts):
        raise HTTPException(404, 'Lô thuốc không tồn tại.')
    for item in data.items:
        current = next(b for b in batches if b.id == item.batch_id)
        if current.sale_price != item.expected_sale_price:
            raise HTTPException(409, f'Giá lô {current.code} đã thay đổi. Tải lại tồn kho và thêm lại thuốc vào giỏ.')
    total = Decimal('0')
    medicines = {}
    for batch in batches:
        medicine = require(db, Medicine, batch.medicine_id)
        medicines[batch.id] = medicine
        if not medicine.active or batch.expiry_date <= today():
            raise HTTPException(409, f'Lô {batch.code} hết hạn hoặc thuốc ngừng bán.')
        if batch.quantity < amounts[batch.id]:
            raise HTTPException(409, f'Lô {batch.code} chỉ còn {batch.quantity}.')
        if medicine.prescription_required and (user.role == 'cashier' or not data.prescription_ref):
            raise HTTPException(403, 'Thuốc kê đơn cần dược sĩ/quản lý kiểm tra và nhập mã đơn thuốc.')
        total += batch.sale_price * amounts[batch.id]
    invoice = Invoice(user_id=user.id, customer=data.customer or 'Khách lẻ', total=total, payment_method=data.payment_method, request_key=data.request_key, request_hash=fingerprint, prescription_ref=data.prescription_ref)
    db.add(invoice)
    db.flush()
    for batch in batches:
        qty = amounts[batch.id]
        medicine = medicines[batch.id]
        db.add(InvoiceItem(invoice_id=invoice.id, batch_id=batch.id, medicine_name=medicine.name, unit_name=require(db, Unit, medicine.unit_id).name, quantity=qty, sale_price=batch.sale_price, purchase_price=batch.purchase_price))
        batch.quantity -= qty
        movement(db, batch, user, -qty, 'sale', invoice_id=invoice.id)
    db.commit()
    return invoice_detail(db, invoice)

def cancel_sale(db, ident, reason, user):
    invoice = db.scalar(select(Invoice).where(Invoice.id == ident).with_for_update())
    if not invoice:
        raise HTTPException(404, 'Không tìm thấy hóa đơn.')
    if invoice.status == 'cancelled':
        return invoice_detail(db, invoice)
    items = list(db.scalars(select(InvoiceItem).where(InvoiceItem.invoice_id == ident)))
    quantities = {i.batch_id:i.quantity for i in items}
    for batch in db.scalars(select(Batch).where(Batch.id.in_(quantities)).order_by(Batch.id).with_for_update()):
        batch.quantity += quantities[batch.id]
        movement(db, batch, user, quantities[batch.id], 'cancel', reason, ident)
    invoice.status = 'cancelled'
    invoice.cancel_reason = reason
    invoice.cancelled_by = user.id
    db.commit()
    return invoice_detail(db, invoice)
