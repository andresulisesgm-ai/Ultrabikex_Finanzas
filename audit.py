from datetime import datetime, timezone, timedelta

TZ_VE = timezone(timedelta(hours=-4))


def registrar_auditoria(db, usuario, modulo, accion, detalle=''):
    """Registra una acción de auditoría en audit_log sin interrumpir la operación principal."""
    try:
        fecha_hora = datetime.now(TZ_VE).strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            'INSERT INTO audit_log (fecha_hora, usuario, modulo, accion, detalle) VALUES (?, ?, ?, ?, ?)',
            (fecha_hora, usuario or 'sistema', modulo, accion, str(detalle or '')[:1000]),
        )
        db.commit()
    except Exception:
        pass
