# Скачивает фото из списка tools/fetch-images.json, кладёт на белый фон, сохраняет в WebP (до 1200 px).
import json, io, os, sys, time, urllib.request
from PIL import Image
items = json.load(open('tools/fetch-images.json'))
ok = fail = skip = 0
failed = []
for it in items:
    p = it['path']
    if os.path.exists(p):
        skip += 1; continue
    data = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(it['url'], headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=40).read(); break
        except Exception as e:
            err = str(e); time.sleep(2)
    if data is None:
        fail += 1; failed.append({'path': p, 'err': err}); continue
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        if im.mode in ('RGBA', 'LA', 'P'):
            im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
        else:
            im = im.convert('RGB')
        im.thumbnail((1200, 1200))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p, 'WEBP', quality=80, method=6)
        ok += 1
    except Exception as e:
        fail += 1; failed.append({'path': p, 'err': 'decode: ' + str(e)})
json.dump({'ok': ok, 'fail': fail, 'skip': skip, 'failed': failed}, open('tools/fetch-report.json', 'w'), ensure_ascii=False, indent=1)
print(ok, fail, skip)
