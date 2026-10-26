"""Browser smoke test: national city search, selection, comparison completion."""
import functools,http.server,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  page=browser.new_page()
  errors=[]
  page.on("pageerror",lambda error:errors.append(str(error)))
  page.goto(f"http://127.0.0.1:{server.server_port}/index.html")
  page.wait_for_function("document.querySelector('#lookup').textContent.includes('indexed')",timeout=15000)
  for name in ["Rochester","Steubenville","Hillsboro"]:
   page.locator("#search").fill(name)
   page.locator(".result").first.click()
  assert page.locator("#count").inner_text()=="3"
  page.locator("#generate").click()
  page.wait_for_function("document.querySelector('#status').textContent.includes('Comparison generated')",timeout=15000)
  assert page.locator("#report tbody tr").count()==3
  assert not errors,errors
  browser.close()
 print("PASS: national lookup, three-city selection and report generation")
finally:
 server.shutdown()
