from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from master.models import Die, CompanyPress
from production.models import OnlineProductionReport
from raw_data.models import Raw_data

# ─────────────────────────────────────────────────────────────────────────────
#  Views for Current Production Dashboard
# ─────────────────────────────────────────────────────────────────────────────
class CurrentProductionView(View):
    """Render the current production dashboard (sensor-wise cards)"""

    def get(self, request):
        try:
            # Get all sensor names that are assigned to presses in CompanyPress
            configured_sensors = CompanyPress.objects.values_list(
                'sensor', flat=True
            ).distinct()

            # Build list with profile counts - ONLY for configured sensors
            sensors = []
            for sensor in configured_sensors:
                # Count Raw_data records for this sensor
                profile_count = Raw_data.objects.filter(sensor_name=sensor).count()
                
                # Only add sensors that have data in Raw_data
                if profile_count > 0:
                    # Get the press name(s) associated with this sensor
                    press_info = CompanyPress.objects.filter(sensor=sensor).first()
                    
                    sensors.append({
                        'sensor_name': sensor,
                        'profile_count': profile_count,
                        'press_name': press_info.name if press_info else 'N/A',
                        'company_name': press_info.company.name if press_info else 'N/A'
                    })

            # Sort by sensor name for consistent display
            sensors = sorted(sensors, key=lambda x: x['sensor_name'])

            return render(
                request,
                'current_production/current_production.html',
                {'sensors': sensors}
            )

        except Exception as e:
            print(f"Error in CurrentProductionView: {e}")
            import traceback
            traceback.print_exc()
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

            # Verify this sensor is configured in a press
            if not CompanyPress.objects.filter(sensor=sensor_name).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'Sensor not configured in any press'
                }, status=404)

            # Fetch raw data for this sensor
            raw_records = Raw_data.objects.filter(
                sensor_name=sensor_name
            ).order_by('-datetime')
            
            order_details = []

            for raw in raw_records:
                die_no = raw.die_number
                die_name = 'N/A'
                
                # Try to get die name from Die model
                if die_no:
                    try:
                        die = Die.objects.get(die_no=die_no)
                        die_name = die.die_name or die_no
                    except Die.DoesNotExist:
                        die_name = die_no

                # Try to get order number from OnlineProductionReport
                report = OnlineProductionReport.objects.filter(die_no=die_no).first()
                order_no = report.production_id if report else 'N/A'

                # Get press name from CompanyPress
                press_obj = CompanyPress.objects.filter(sensor=sensor_name).first()
                press_name = press_obj.name if press_obj else sensor_name

                order_details.append({
                    'order_no': order_no,
                    'die_name': die_name,
                    'date': raw.datetime.strftime('%Y-%m-%d') if raw.datetime else 'N/A',
                    'time': raw.datetime.strftime('%H:%M:%S') if raw.datetime else 'N/A',
                    'press': press_name,  # Show press name instead of sensor
                    'sensor': sensor_name,  # Keep sensor for reference
                    'length': float(raw.length) if raw.length else 0,
                })

            return JsonResponse({
                'success': True,
                'order_details': order_details,
                'total_records': len(order_details)
            })

        except Exception as e:
            print(f"Error in SensorDetailView: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)}, status=500)