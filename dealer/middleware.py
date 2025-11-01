class NoCacheForAuthenticatedPages:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        resp = self.get_response(request)
        if request.user.is_authenticated:
            resp["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp["Pragma"] = "no-cache"
            resp["Expires"] = "0"
        return resp
