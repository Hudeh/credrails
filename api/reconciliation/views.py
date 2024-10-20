import pandas as pd
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework_csv.renderers import CSVRenderer

class ReconcileView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer, CSVRenderer]
    parser_classes = (MultiPartParser, FormParser)

    def normalize_data(self, value):
        """Normalize data by stripping spaces and handling types safely."""
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, int) or isinstance(value, float):
            return value
        else:
            return str(value).strip()

    def reconcile_files(self, source_df, target_df):
        """Perform the reconciliation."""
        # Normalize the data in both DataFrames
        source_df = source_df.map(self.normalize_data)
        target_df = target_df.map(self.normalize_data)

        # Identify missing and mismatched records
        source_ids = set(source_df['id'])
        target_ids = set(target_df['id'])

        missing_in_target = source_df[~source_df['id'].isin(target_ids)].to_dict(orient='records')
        missing_in_source = target_df[~target_df['id'].isin(source_ids)].to_dict(orient='records')

        discrepancies = []
        common_ids = source_ids & target_ids
        for id_ in common_ids:
            source_record = source_df[source_df['id'] == id_].to_dict(orient='records')[0]
            target_record = target_df[target_df['id'] == id_].to_dict(orient='records')[0]
            diff = {k: (source_record[k], target_record[k]) for k in source_record if source_record[k] != target_record[k]}
            if diff:
                discrepancies.append({'id': id_, 'differences': diff})

        return {
            'missing_in_target': missing_in_target,
            'missing_in_source': missing_in_source,
            'discrepancies': discrepancies,
        }

    def post(self, request, *args, **kwargs):
        source_file = request.FILES.get('source_file')
        target_file = request.FILES.get('target_file')

        if not source_file or not target_file:
            return JsonResponse({'error': 'Both files are required.'}, status=400)

        try:
            source_df = pd.read_csv(source_file)
            target_df = pd.read_csv(target_file)

            report = self.reconcile_files(source_df, target_df)

            format_type = request.query_params.get('format', 'json').lower()
            if format_type == 'json':
                return JsonResponse(report)
            elif format_type == 'csv':
                return self.generate_csv_response(report)
            elif format_type == 'html':
                return self.generate_html_response(report)
            else:
                return JsonResponse({'error': 'Invalid format type.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def generate_csv_response(self, report):
        """Generate CSV response."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reconciliation_report.csv"'
        pd.DataFrame(report['discrepancies']).to_csv(response, index=False)
        return response

    def generate_html_response(self, report):
        """Generate HTML response."""
        html_content = f"""
        <html>
        <head><title>Reconciliation Report</title></head>
        <body>
            <h1>Reconciliation Report</h1>
            <h2>Missing in Target</h2>
            <pre>{report['missing_in_target']}</pre>
            <h2>Missing in Source</h2>
            <pre>{report['missing_in_source']}</pre>
            <h2>Discrepancies</h2>
            <pre>{report['discrepancies']}</pre>
        </body>
        </html>
        """
        return HttpResponse(html_content)

