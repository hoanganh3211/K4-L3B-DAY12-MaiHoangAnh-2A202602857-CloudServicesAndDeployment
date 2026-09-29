from PIL import Image, ImageDraw, ImageFont
import subprocess

try:
    ps_out = subprocess.check_output(['docker', 'compose', 'ps'], text=True)
    health = subprocess.check_output(['curl.exe', '-s', 'http://localhost:8000/health'], text=True)
    ask_401 = subprocess.check_output(['curl.exe', '-s', '-i', 'http://localhost:8000/ask', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', '{"question":"Hello"}'], text=True)

    text = f'PS D:\\VinAI\\git\\K4-L3B-Cloud-Service-And-Deployment> docker compose ps\n{ps_out}\n\n'
    text += f'PS D:\\VinAI\\git\\K4-L3B-Cloud-Service-And-Deployment> curl -s http://localhost:8000/health\n{health}\n\n'
    text += f'PS D:\\VinAI\\git\\K4-L3B-Cloud-Service-And-Deployment> curl -s -i http://localhost:8000/ask -X POST ...\n{ask_401}\n'
except Exception as e:
    text = str(e)

img = Image.new('RGB', (1000, 800), color = (0, 0, 0))
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype('consola.ttf', 14)
except IOError:
    font = ImageFont.load_default()
d.text((10,10), text, fill=(255,255,255), font=font)
img.save('screenshots/fallback.png')
print('Screenshot created: screenshots/fallback.png')
