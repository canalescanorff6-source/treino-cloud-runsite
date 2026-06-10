# Gerar APK no Google Colab

Use esta pasta `android_kivy_apk` para gerar o APK.

## Célula 1 - instalar ferramentas

```python
!apt update -y
!apt install -y zip unzip openjdk-17-jdk python3-pip git autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev lld
!python -m pip install --upgrade pip
!python -m pip install buildozer==1.5.0 cython==0.29.37 virtualenv
```

## Célula 2 - enviar o ZIP e entrar na pasta

```python
from google.colab import files
uploaded = files.upload()
```

Depois descompacte o ZIP e entre na pasta que contém o `buildozer.spec`.

## Célula 3 - compilar

```python
!buildozer -v android debug
```

## Célula 4 - baixar APK

```python
from google.colab import files
import glob, os
apks = glob.glob('/content/**/*.apk', recursive=True)
print(apks)
files.download(max(apks, key=os.path.getmtime))
```

## Dentro do app

Na tela **Configurar Render**, coloque:

```text
URL: https://SEU-APP.onrender.com
TOKEN: treino-pro-max-online-2026
```
