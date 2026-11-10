import asyncio, json, urllib.request, subprocess, time, os, base64
import websockets

os.makedirs('docs/screenshots', exist_ok=True)

proc = subprocess.Popen([
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    '--headless=new',
    '--remote-debugging-port=9222',
    '--user-data-dir=C:\\Users\\panch\\AppData\\Local\\Temp\\chrome_ss',
    '--window-size=1600,950',
    'file:///C:/Users/panch/Documents/MuscleMap/index.html'
])
time.sleep(2.5)

async def main():
    with urllib.request.urlopen('http://localhost:9222/json') as response:
        pages = json.loads(response.read())
        page = next(p for p in pages if p.get('type') == 'page')
        ws_url = page['webSocketDebuggerUrl']

    async with websockets.connect(ws_url) as ws:
        msg_id = 1
        async def send(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {'id': msg_id, 'method': method}
            if params:
                payload['params'] = params
            await ws.send(json.dumps(payload))
            while True:
                res = json.loads(await ws.recv())
                if res.get('id') == msg_id:
                    return res

        await send('Page.enable')
        await send('Runtime.enable')

        # 1. Mode Classique / Protocole : Sélection de muscles sEMG clés du membre inférieur
        js_select = """
        (function() {
            const targetIds = [
                'vastus-lateralis',
                'vastus-medialis',
                'rectus-femoris',
                'biceps-femoris-long',
                'semitendinosus',
                'tibialis-anterior',
                'gastrocnemius-medial',
                'gluteus-maximus'
            ];
            targetIds.forEach(id => {
                const card = document.querySelector('.m-card[data-id="' + id + '"]');
                if (card) card.click();
            });
            // Activer repères N° + Noms
            const btnRep = document.getElementById('btnRepBoth');
            if (btnRep) btnRep.click();
        })()
        """
        await send('Runtime.evaluate', {'expression': js_select})
        await asyncio.sleep(1)

        res1 = await send('Page.captureScreenshot', {'format': 'png'})
        with open('docs/screenshots/muscle-map-protocole.png', 'wb') as f:
            f.write(base64.b64decode(res1['result']['data']))
        print('Captured protocole screenshot')

        # 2. Mode % CMV : Heatmap
        js_heat = """
        (function() {
            const tabMvc = document.getElementById('tabMvc');
            if (tabMvc) tabMvc.click();
            const btnEx = document.getElementById('btnLoadExampleJson');
            if (btnEx) btnEx.click();
        })()
        """
        await send('Runtime.evaluate', {'expression': js_heat})
        await asyncio.sleep(1)

        res2 = await send('Page.captureScreenshot', {'format': 'png'})
        with open('docs/screenshots/muscle-map-heatmap.png', 'wb') as f:
            f.write(base64.b64decode(res2['result']['data']))
        print('Captured heatmap screenshot')

try:
    asyncio.run(main())
finally:
    proc.terminate()
