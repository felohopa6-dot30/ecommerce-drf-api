from django.http import JsonResponse

def handler404(request, exception):
    message = ('Page not found')
    response = JsonResponse({"error": message}, status=404)
    response.status_code = 404
    return response

def handler500(request):
    message = ("Internal server error")
    response = JsonResponse({"error": message}, status=500)
    response.status_code = 500
    return response
