"""
generador_receta.py
Genera la receta médica en PDF usando ReportLab.
Colocar en: consulta/generador_receta.py
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas as pdfcanvas


# ── Colores del consultorio ────────────────────────────────────────────────────
VERDE        = colors.HexColor('#1a7a4a')
VERDE_CLARO  = colors.HexColor('#e8f5ee')
GRIS_TEXTO   = colors.HexColor('#333333')
GRIS_SUAVE   = colors.HexColor('#666666')
GRIS_LINEA   = colors.HexColor('#dddddd')
AZUL_DATO    = colors.HexColor('#1565c0')


# ── Datos del consultorio (editar según el consultorio real) ───────────────────
CONSULTORIO = {
    'nombre':     'Consultorio Médico',
    'direccion':  'Av. San Martín 1234, Mendoza',
    'telefono':   'Tel: 0261-4123456',
    'email':      'consultas@clinica.com',
    'ciudad':     'Mendoza, Argentina',
    'logo':       None,   # ruta a imagen PNG/JPG, o None si no hay logo
}


def generar_receta_pdf(historia):
    """
    Recibe un objeto HistoriaClinica y devuelve los bytes del PDF.
    Uso en la vista:
        pdf_bytes = generar_receta_pdf(historia)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receta_{historia.pk}.pdf"'
        return response
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2*cm,
    )

    story = []
    styles = getSampleStyleSheet()

    # ── Estilos personalizados ─────────────────────────────────────────────────
    estilo_titulo = ParagraphStyle(
        'titulo',
        parent=styles['Normal'],
        fontSize=18,
        textColor=VERDE,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    estilo_subtitulo = ParagraphStyle(
        'subtitulo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=GRIS_SUAVE,
        fontName='Helvetica',
        alignment=TA_LEFT,
    )
    estilo_seccion = ParagraphStyle(
        'seccion',
        parent=styles['Normal'],
        fontSize=8,
        textColor=VERDE,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=4,
        textTransform='uppercase',
    )
    estilo_normal = ParagraphStyle(
        'normal_clinica',
        parent=styles['Normal'],
        fontSize=10,
        textColor=GRIS_TEXTO,
        fontName='Helvetica',
        leading=14,
    )
    estilo_dato = ParagraphStyle(
        'dato',
        parent=styles['Normal'],
        fontSize=10,
        textColor=GRIS_TEXTO,
        fontName='Helvetica',
        leading=16,
    )
    estilo_med_nombre = ParagraphStyle(
        'med_nombre',
        parent=styles['Normal'],
        fontSize=11,
        textColor=GRIS_TEXTO,
        fontName='Helvetica-Bold',
        leading=14,
    )
    estilo_med_detalle = ParagraphStyle(
        'med_detalle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=GRIS_SUAVE,
        fontName='Helvetica',
        leading=13,
    )
    estilo_firma = ParagraphStyle(
        'firma',
        parent=styles['Normal'],
        fontSize=9,
        textColor=GRIS_SUAVE,
        fontName='Helvetica',
        alignment=TA_CENTER,
    )

    paciente = historia.turno.paciente
    medico   = historia.medico

    # ══════════════════════════════════════════════════════════════════════════
    # CABECERA
    # ══════════════════════════════════════════════════════════════════════════
    cabecera_data = [[
        Paragraph(CONSULTORIO['nombre'], estilo_titulo),
        Paragraph(
            f"{CONSULTORIO['direccion']}<br/>"
            f"{CONSULTORIO['telefono']}<br/>"
            f"{CONSULTORIO['email']}",
            ParagraphStyle('info_der', parent=estilo_subtitulo, alignment=TA_RIGHT)
        )
    ]]
    tabla_cabecera = Table(cabecera_data, colWidths=[9*cm, 8*cm])
    tabla_cabecera.setStyle(TableStyle([
        ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
    ]))
    story.append(tabla_cabecera)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width='100%', thickness=2, color=VERDE, spaceAfter=0.4*cm))

    # Título del documento
    story.append(Paragraph(
        f"<font color='#{VERDE.hexval()[2:]}' size='13'><b>RECETA MÉDICA</b></font>  "
        f"<font color='#{GRIS_SUAVE.hexval()[2:]}' size='9'>N° {historia.pk:06d}</font>",
        ParagraphStyle('titulo_doc', parent=styles['Normal'], fontSize=13,
                       fontName='Helvetica-Bold', spaceAfter=8)
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # DATOS DEL MÉDICO Y PACIENTE (dos columnas)
    # ══════════════════════════════════════════════════════════════════════════
    especialidad = getattr(medico, 'especialidad', '') or ''
    matricula    = getattr(medico, 'matricula', '') or ''

    bloque_medico = [
        Paragraph('<b>MÉDICO PRESCRIPTOR</b>', estilo_seccion),
        Paragraph(f"Dr/a. {medico.get_full_name()}", estilo_med_nombre),
        Paragraph(especialidad, estilo_med_detalle) if especialidad else Spacer(1, 1),
        Paragraph(f"Matrícula: {matricula}", estilo_med_detalle) if matricula else Spacer(1, 1),
        Paragraph(historia.fecha_hora.strftime('%d/%m/%Y'), estilo_med_detalle),
    ]

    obra_social = paciente.obra_social or 'Particular'
    nro_afiliado = paciente.nro_afiliado or '—'
    bloque_paciente = [
        Paragraph('<b>PACIENTE</b>', estilo_seccion),
        Paragraph(f"<b>{paciente.nombre_completo.upper()}</b>", estilo_med_nombre),
        Paragraph(f"DNI: {paciente.dni}  ·  Edad: {paciente.edad} años", estilo_med_detalle),
        Paragraph(f"Obra social: {obra_social}", estilo_med_detalle),
        Paragraph(f"N° afiliado: {nro_afiliado}", estilo_med_detalle) if paciente.nro_afiliado else Spacer(1,1),
    ]

    tabla_info = Table(
        [[bloque_medico, bloque_paciente]],
        colWidths=[8.5*cm, 8.5*cm]
    )
    tabla_info.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND',   (0, 0), (0, 0),   VERDE_CLARO),
        ('BACKGROUND',   (1, 0), (1, 0),   colors.HexColor('#f0f4ff')),
        ('ROUNDEDCORNERS', [6]),
        ('BOX',          (0, 0), (0, 0),   0.5, GRIS_LINEA),
        ('BOX',          (1, 0), (1, 0),   0.5, GRIS_LINEA),
        ('LEFTPADDING',  (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
    ]))
    story.append(tabla_info)
    story.append(Spacer(1, 0.5*cm))

    # ══════════════════════════════════════════════════════════════════════════
    # DIAGNÓSTICO
    # ══════════════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_LINEA))
    story.append(Paragraph('Diagnóstico', estilo_seccion))

    dx_texto = historia.diagnostico_principal
    if historia.cie10:
        dx_texto += f" <font color='#{GRIS_SUAVE.hexval()[2:]}' size='9'>(CIE-10: {historia.cie10})</font>"
    story.append(Paragraph(dx_texto, estilo_dato))

    if historia.diagnosticos_secundarios:
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(historia.diagnosticos_secundarios, estilo_normal))

    # ══════════════════════════════════════════════════════════════════════════
    # MEDICAMENTOS (receta)
    # ══════════════════════════════════════════════════════════════════════════
    items_receta = historia.receta_items.all()

    if items_receta:
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_LINEA))
        story.append(Paragraph('Medicamentos prescriptos', estilo_seccion))

        for i, item in enumerate(items_receta, 1):
            bloque = KeepTogether([
                Paragraph(
                    f"<b>{i}. {item.medicamento}</b>  "
                    f"<font size='9' color='#{GRIS_SUAVE.hexval()[2:]}'>"
                    f"{item.dosis}  ·  {item.forma}</font>",
                    ParagraphStyle('med_item', parent=estilo_dato,
                                   textColor=GRIS_TEXTO, spaceBefore=4)
                ),
                Paragraph(
                    f"<font color='#{AZUL_DATO.hexval()[2:]}'>{item.posologia}</font>",
                    ParagraphStyle('posologia', parent=estilo_normal,
                                   leftIndent=12, spaceAfter=6)
                ),
                Paragraph(item.instrucciones,
                    ParagraphStyle('instruc', parent=estilo_normal,
                                   leftIndent=12, fontSize=9,
                                   textColor=GRIS_SUAVE, spaceAfter=4)
                ) if item.instrucciones else Spacer(1, 2),
            ])
            story.append(bloque)

    # ══════════════════════════════════════════════════════════════════════════
    # INDICACIONES AL PACIENTE
    # ══════════════════════════════════════════════════════════════════════════
    if historia.indicaciones:
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_LINEA))
        story.append(Paragraph('Indicaciones al paciente', estilo_seccion))
        story.append(Paragraph(historia.indicaciones, estilo_normal))

    # ══════════════════════════════════════════════════════════════════════════
    # PRÓXIMA CONSULTA / DERIVACIÓN
    # ══════════════════════════════════════════════════════════════════════════
    extras = []
    if historia.proxima_consulta:
        extras.append(('Próxima consulta', historia.proxima_consulta.strftime('%d/%m/%Y')))
    if historia.derivacion:
        extras.append(('Derivación', historia.derivacion))

    if extras:
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_LINEA))
        for etiqueta, valor in extras:
            story.append(Paragraph(
                f"<b>{etiqueta}:</b> {valor}",
                ParagraphStyle('extra', parent=estilo_dato, spaceBefore=6)
            ))

    # ══════════════════════════════════════════════════════════════════════════
    # FIRMA DEL MÉDICO
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5*cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_LINEA))
    story.append(Spacer(1, 0.3*cm))

    firma_data = [[
        '',
        Table(
            [[Paragraph(
                f"_________________________<br/>"
                f"<b>Dr/a. {medico.get_full_name()}</b><br/>"
                f"{especialidad}<br/>"
                f"{'Mat. ' + matricula if matricula else ''}",
                estilo_firma
            )]],
            colWidths=[8*cm]
        ),
        '',
    ]]
    tabla_firma = Table(firma_data, colWidths=[4*cm, 9*cm, 4*cm])
    tabla_firma.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(tabla_firma)

    # ══════════════════════════════════════════════════════════════════════════
    # PIE DE PÁGINA
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=VERDE))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"{CONSULTORIO['nombre']}  ·  {CONSULTORIO['direccion']}  ·  {CONSULTORIO['telefono']}",
        ParagraphStyle('pie', parent=styles['Normal'], fontSize=7,
                       textColor=GRIS_SUAVE, alignment=TA_CENTER)
    ))

    # ── Construir PDF ──────────────────────────────────────────────────────────
    doc.build(story)
    return buffer.getvalue()