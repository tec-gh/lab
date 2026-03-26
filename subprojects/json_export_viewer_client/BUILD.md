# BUILD æé 

ãã®ææ¸ã¯ `json_export_viewer_client` ã `PyInstaller` ã§ `exe` åããæé ã§ãã

## 1. åæ

- OS: Windows
- Python 3.9 ä»¥ä¸
- `pip` ãå©ç¨å¯è½
- ãã«ãå¯¾è±¡: `d:\project\subprojects\json_export_viewer_client`

## 2. ä¾å­å°å¥

```bash
cd D:\project\subprojects\json_export_viewer_client
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

## 3. ãã«ã

```bash
pyinstaller --noconfirm --onefile --name json_export_viewer_client main.py
```

## 4. çæç©

ãã«ãå¾ãä»¥ä¸ãçæããã¾ãã

```text
dist\json_export_viewer_client.exe
```

å¿è¦ã«å¿ãã¦ãéå¸ç¨ãã©ã«ããä»¥ä¸ã®ããã«ã¾ã¨ãã¦ãã ããã

```text
json_export_viewer_client/
  json_export_viewer_client.exe
  config.ini
  README.md
  sample_data/
```

## 5. éå¸æã®æ³¨æ

- `config.ini` ã¯ `exe` ã¨åããã©ã«ãã«éç½®ãã¦ãã ãã
- `json_folder` ã¯éå¸å PC ã«å­å¨ãããã¹ã¸å¤æ´ãã¦ãã ãã
- `web` ã¢ã¼ãã§ãã­ã¼ã«ã« PC ä¸ã® `json_folder` ãèª­ã¿è¾¼ã¿ã¾ã
- ç¾å¨ã® UI ã¯ä¸è¦§ä¸­å¿ã§ãè©³ç´°ã«ã¼ãã¯ããã¾ãã
- ãµã³ãã«ç¢ºèªç¨ã« `sample_data/records_export.json` ãåæ¢±ã§ãã¾ã

## 6. åãã«ã

ã½ã¼ã¹æ´æ°å¾ã¯ååº¦ä»¥ä¸ãå®è¡ãã¾ãã

```bash
pyinstaller --noconfirm --onefile --name json_export_viewer_client main.py
```

## 7. è£è¶³

å¿è¦ã«å¿ãã¦ä»¥ä¸ãè¿½å ã§ãã¾ãã

- `--icon` ã«ããã¢ã¤ã³ã³åãè¾¼ã¿
- `--add-data` ã«ããè¿½å ãã¡ã¤ã«åæ¢±
- `spec` ãã¡ã¤ã«ãç¨ããè©³ç´°å¶å¾¡
