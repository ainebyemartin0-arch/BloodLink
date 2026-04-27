#!/usr/bin/env python
import re

# Read the current views.py file
with open('staff_portal/views.py', 'r') as f:
    content = f.read()

# Find and replace the blood_stock view function
old_view_pattern = r'(@login_required\s+def blood_stock\(request\):.*?return render\(request, \'staff_portal/blood_stock\.html\', context\))'

new_view = '''@login_required
def blood_stock(request):
    """Blood stock monitoring and management page."""
    # Get all blood stocks
    blood_stocks = BloodStock.objects.all().order_by('blood_type')
    
    # Calculate statistics
    total_units = blood_stocks.aggregate(total=Sum('current_units'))['total'] or 0
    critical_count = blood_stocks.filter(current_units__lte=F('critical_level')).count()
    empty_types = blood_stocks.filter(current_units=0).count()
    
    context = {
        'blood_stocks': blood_stocks,
        'total_units': total_units,
        'critical_count': critical_count,
        'empty_types': empty_types,
    }
    
    return render(request, 'staff_portal/blood_stock.html', context)'''

# Replace the function
content = re.sub(old_view_pattern, new_view, content, flags=re.DOTALL)

# Write back to file
with open('staff_portal/views.py', 'w') as f:
    f.write(content)

print("Blood stock view updated successfully!")
