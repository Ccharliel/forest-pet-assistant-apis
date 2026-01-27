from fastapi import Request

async def get_public_domin(request: Request, call_next):
    """get public domin from request"""
    headers = request.headers
    # get scheme
    if "x-forwarded-proto" in headers:
        scheme = headers["x-forwarded-proto"].split(",")[0].strip()
    else:
        scheme = request.url.scheme
    # get host
    if "x-forwarded-host" in headers:
        host = headers["x-forwarded-host"].split(",")[0].strip()
    elif "host" in headers:
        host = headers["host"]
    else:
        host = "localhost"
    # remove normal port
    if scheme == "https" and host.endswith(":443"):
        host = host[:-4]  # remove :443
    elif scheme == "http" and host.endswith(":80"):
        host = host[:-3]  # remove :80
    # get public_domain
    request.state.public_domain = f"{scheme}://{host}"
    response = await call_next(request)
    return response