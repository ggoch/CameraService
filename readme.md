車牌與車子種類辨識
===

### 第一步 安裝所需套件

假設你已安裝完python3，在專案目錄下用CMD開啟(絕對路徑不能有中文)

```cmd
建立虛擬環境病雞依賴安裝在橡木資料夾，避免汙染全域環境
python -m venv cuda

cuda\Scripts\activate

安裝yolov8框架工具
pip install ultralytics

如果要使用gpu加速運行請額外安裝pytorch工具
這行指令由pyTroch官網獲得
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

(torchvision有可能會不是gpu版本，安裝後請用pip list 確認後面是否有+cu11x)
```
啟動指令 python run.py --[mode](有 dev，prod，test三種) --db [sql](有 postgresql和mysql，預設是postgresql)

預設swagger路徑在 /docs下