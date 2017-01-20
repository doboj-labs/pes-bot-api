from django.http import JsonResponse


def response_json_with_status_code(status_code, response):
    return JsonResponse(status=status_code, data={'response': response})
