from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import pandas as pd
import io
from .models import Equipment, DatasetHistory

class EquipmentUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES['file']
        df = pd.read_csv(file)
        
        # 1. Save Current Equipment Data to Database
        for _, row in df.iterrows():
            Equipment.objects.create(
                name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=row['Flowrate'],
                pressure=row['Pressure'],
                temperature=row['Temperature']
            )
        
        # 2. Log this specific upload to Dataset History
        DatasetHistory.objects.create(
            file_name=file.name,
            total_count=len(df),
            avg_pressure=df['Pressure'].mean()
        )

        # 3. Fetch Last 5 Uploads for the History Sidebar
        history_qs = DatasetHistory.objects.all().order_by('-id')[:5]
        history_list = [{
            "filename": h.file_name,
            "date": h.uploaded_at.strftime("%d/%m/%Y, %H:%M"),
            "count": h.total_count,
            "avg_p": round(h.avg_pressure, 2)
        } for h in history_qs]
        
        # 4. Prepare Dashboard Stats for React
        stats = {
            "total_count": len(df),
            "avg_pressure": round(float(df['Pressure'].mean()), 2),
            "max_temp": int(df['Temperature'].max()),
            "avg_flowrate": round(float(df['Flowrate'].mean()), 2),
            "type_distribution": df['Type'].value_counts().to_dict(),
            "raw_data": df.to_dict(orient='records'),
            "history": history_list
        }
        
        return Response(stats)

class PDFReportView(APIView):
    def get(self, request):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Chemical Equipment Summary Report")
        
        p.setFont("Helvetica", 12)
        y = 750
        # List items from database for the PDF report
        for eq in Equipment.objects.all().order_by('-id')[:15]:
            p.drawString(100, y, f"Item: {eq.name} | Type: {eq.equipment_type} | Pressure: {eq.pressure} bar")
            y -= 25
            if y < 50:
                p.showPage()
                y = 800
                
        p.showPage()
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')