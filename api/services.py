from django.http import JsonResponse


# all our json data shell be in response field of json
def response_json_with_status_code(status_code, response):
    return JsonResponse(status=status_code, data={'response': response})
