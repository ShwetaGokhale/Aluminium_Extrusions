from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import datetime
from django.utils import timezone
from .models import Raw_data, ProductionData


class LoraReceiveView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            data = request.data
            message = data.get('message', '')

            print(f"\n Received raw message: {message}")

            # Expected: "1234,30/10/25 17:27:58, 1.120,960, 11.366, 37 Feet3 Inch"
            parts = [p.strip() for p in message.split(",")]
            if len(parts) < 6:
                raise ValueError("Invalid message format")

            sensor_name = parts[0]
            dt_str = parts[1]
            t_factor = float(parts[2])
            die_number = parts[3]  # string for now
            length_raw = parts[5]

            # Convert datetime (timezone-aware)
            naive_dt = datetime.strptime(dt_str, "%d/%m/%y %H:%M:%S")
            reading_time = timezone.make_aware(naive_dt, timezone.get_current_timezone())

            # Convert "37 Feet3 Inch" -> 37.3
            length_num = self._convert_length(length_raw)

            #  1️ Save raw data
            raw_obj = Raw_data.objects.create(
                sensor_name=sensor_name,
                datetime=reading_time,
                t_factor=t_factor,
                die_number=die_number,
                length=length_num,
            )

            #  2️ Save refined data into ProductionData
            prod_obj = ProductionData.objects.create(
                sensor_name=sensor_name,
                datetime=reading_time,
                t_factor=t_factor,
                die_name=f"Die {die_number}",
                length=length_num,
            )

            #  Terminal logs
            print(
                f" Data saved successfully:\n"
                f"   Raw Table (ID {raw_obj.id})     → raw_machine_data\n"
                f"   Production Table (ID {prod_obj.id}) → production_data\n"
                f"   Sensor Name : {sensor_name}\n"
                f"   Date/Time   : {reading_time}\n"
                f"   T-Factor    : {t_factor}\n"
                f"   Die Number  : {die_number}\n"
                f"   Length (ft) : {length_num}\n"
            )

            return Response(
                {'status': 'ok', 'message': 'Data refined and stored successfully'},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f" Error while processing message: {e}\n")
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        data = list(Raw_data.objects.values())
        return Response({'received_data': data})

    def _convert_length(self, length_str):
        """Convert '37 Feet3 Inch' -> 37.3"""
        length_str = length_str.replace("Feet", "").replace("Inch", "").strip()
        parts = length_str.split()
        if len(parts) >= 2:
            try:
                feet = float(parts[0])
                inch = float(parts[1])
                return round(feet + inch / 10, 2)
            except ValueError:
                pass
        try:
            return float(length_str)
        except ValueError:
            return 0.0

