from django.shortcuts import render

# Create your views here.
def demo_report(request):
    report_data = [
        {
            'id': 1,
            'name': 'John Doe',
            'dept': 'Sales',
            'location': 'New York',
            'pc': 'PC-001',
            'entry_time': '2023-10-01 09:00',
            'exit_time': '2023-10-01 17:00',
        },
        {
            'id': 2,
            'name': 'Jane Smith',
            'dept': 'Marketing',
            'location': 'Los Angeles',
            'pc': 'PC-002',
            'entry_time': '2023-10-01 09:30',
            'exit_time': '2023-10-01 17:30',
        },
    ]
    return render(request, 'reports/demo.html', {'data': report_data})