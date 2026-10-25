"""Browser smoke test: all pilot cities reach a completed report."""
import functools,http.server,threading
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
thread=threading.Thread(target=server.serve_forever,daemon=True)
thread.start()
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page()
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.route("https://api.github.com/**",lambda route:route.fulfill(status=200,content_type="application/json",body='{"workflow_runs":[]}'))
        page.goto(f"http://127.0.0.1:{server.server_port}/index.html")
        for city in ["Rochester, IN","Steubenville, OH","Hillsboro, OR"]:
            page.locator("#city").select_option(city)
            page.wait_for_function("!document.querySelector('#status').textContent.includes('Loading')",timeout=10000)
            assert "loaded successfully" in page.locator("#status").inner_text(),city
            assert page.locator("#report table tbody tr").count()>0,city
            assert "undefined" not in page.locator("#report").inner_text().lower()
        assert not errors,errors
        browser.close()
    print("PASS: all pilot city reports complete in Chromium")
finally:
    server.shutdown()
