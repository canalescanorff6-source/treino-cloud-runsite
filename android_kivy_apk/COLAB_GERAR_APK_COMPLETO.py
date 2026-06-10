# Cole este bloco no Google Colab depois de enviar o ZIP com a pasta android_kivy_apk
from google.colab import files, drive
import os, glob, shutil

drive.mount('/content/drive', force_remount=True)

!apt update -y
!apt install -y zip unzip openjdk-17-jdk python3-pip git autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev lld
!python -m pip install --upgrade pip
!python -m pip install buildozer==1.5.0 cython==0.29.37 virtualenv

print('Envie o ZIP agora')
uploaded = files.upload()
zip_name = list(uploaded.keys())[0]

%cd /content
!rm -rf /content/app
!unzip -o "$zip_name" -d /content/app

specs = glob.glob('/content/app/**/buildozer.spec', recursive=True)
print('Specs encontrados:', specs)
os.chdir(os.path.dirname(specs[0]))

!buildozer -v android debug

apks = glob.glob('/content/app/**/*.apk', recursive=True)
print('APKs encontrados:', apks)
if not apks:
    raise FileNotFoundError('Nenhum APK foi gerado.')

apk = max(apks, key=os.path.getmtime)
os.makedirs('/content/drive/MyDrive/APKs', exist_ok=True)
destino = '/content/drive/MyDrive/APKs/treino_pro_max_online.apk'
shutil.copy(apk, destino)
print('Salvo no Drive:', destino)
files.download(destino)
