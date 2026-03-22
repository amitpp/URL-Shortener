from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import storage

app = FastAPI(title="URL Shortener")
templates = Jinja2Templates(directory="templates")

storage.init_db()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    urls = storage.list_urls()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "urls": urls,
            "base_url": str(request.base_url).rstrip("/"),
            "url_count": len(urls),
            "max_urls": 500,
        },
    )


async def url_is_reachable(url: str) -> bool:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
            resp = await client.head(url)
            if resp.status_code == 405:  # HEAD not allowed — try GET
                resp = await client.get(url)
            return resp.status_code < 500
    except Exception:
        return False


@app.post("/shorten")
async def shorten(original_url: str = Form(...)):
    if not original_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    if not await url_is_reachable(original_url):
        raise HTTPException(status_code=400, detail="URL is not reachable")

    record = storage.create_short_url(original_url)
    if record is None:
        raise HTTPException(status_code=507, detail="Storage limit of 500 URLs reached")

    return JSONResponse(status_code=201, content=record)


@app.get("/api/urls")
async def api_list_urls():
    return storage.list_urls()


@app.delete("/api/urls/{short_code}")
async def api_delete_url(short_code: str):
    deleted = storage.delete_url(short_code)
    if not deleted:
        raise HTTPException(status_code=404, detail="Short code not found")
    return {"deleted": short_code}


# Catch-all must be last — FastAPI matches routes in declaration order
@app.get("/{short_code}")
async def redirect(short_code: str):
    record = storage.get_url(short_code)
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=record["original_url"], status_code=302)
