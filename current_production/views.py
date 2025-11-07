from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from master.models import Die
from production.models import OnlineProductionReport
from raw_data.models import Raw_data

# ─────────────────────────────────────────────────────────────────────────────
#  Views for Current Production Dashboard
# ─────────────────────────────────────────────────────────────────────────────
class CurrentProductionView(View):
    """Render the current production dashboard (sensor-wise cards)"""

    def get(self, request):
        try:
            # Get unique sensor names from Raw_data
            sensor_names = Raw_data.objects.values_list(
                'sensor_name', flat=True
            ).distinct().order_by('sensor_name')

            # Build list with profile counts
            sensors = []
            for sensor in sensor_names:
                profile_count = Raw_data.objects.filter(sensor_name=sensor).count()
                sensors.append({
                    'sensor_name': sensor,
                    'profile_count': profile_count
                })

            return render(
                request,
                'current_production/current_production.html',
                {'sensors': sensors}
            )

        except Exception as e:
            print(f"Error in CurrentProductionView: {e}")
            return render(
                request,
                'current_production/current_production.html',
                {'sensors': []}
            )


class SensorDetailView(View):
    """API endpoint to get production details for a specific sensor"""

    def get(self, request):
        try:
            sensor_name = request.GET.get('sensor_name')
            if not sensor_name:
                return JsonResponse({'success': False, 'message': 'Sensor name required'}, status=400)

            raw_records = Raw_data.objects.filter(sensor_name=sensor_name).order_by('-datetime')
            order_details = []

            for raw in raw_records:
                die_no = raw.die_number
                die_name = 'N/A'
                if die_no:
                    try:
                        die = Die.objects.get(die_no=die_no)
                        die_name = die.die_name or die_no
                    except Die.DoesNotExist:
                        die_name = die_no

                report = OnlineProductionReport.objects.filter(die_no=die_no).first()
                order_no = report.production_id if report else 'N/A'

                order_details.append({
                    'order_no': order_no,
                    'die_name': die_name,
                    'date': raw.datetime.strftime('%Y-%m-%d') if raw.datetime else 'N/A',
                    'time': raw.datetime.strftime('%H:%M:%S') if raw.datetime else 'N/A',
                    'press': raw.sensor_name or 'N/A',
                    'length': raw.length or 0,
                })

            return JsonResponse({
                'success': True,
                'order_details': order_details,
                'total_records': len(order_details)
            })

        except Exception as e:
            print(f"Error in SensorDetailView: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
