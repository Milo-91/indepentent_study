# indepentend_study
使用規則：

檔案下載

先將此資料夾 fork 至自己的 Github 中

git clone \<fork dir https\>


檔案上傳

git add . (增加全部更新內容)

git commit -m "message" (送出此更改並附上 message )

git push \<branch\> (將資料推送至 branch 上)

上傳成功後在 Github 上進行 pull request (請 PR 至 feature 上而非 main 上)



Game24：

確認模型路徑(model_path)、匯入方式(model_import_method)、題號(idx)與演算法(method)皆正確後執行 run.py 即可開始

parameters.py 內存有參數可以做變更

parameters.py 內 model_path 可以更改模型，不同的匯入方式需要修改之模型參數名稱也不同

parameters.py 內 model_import_method 之更改名稱與 llm_function.py 之條件名稱相同，請依照匯入方式更改名稱

更改題號的方式為更改 parameters.py 中的 initial_idx 來更改開始題號，parameters.py 中的 question_sets 來選擇跑的組數

產生過程與 llm 回應會記錄於 record folder 中的 record.txt 中，每層結果與最終結果會記錄於 record folder 中的 tree.json 中，視覺化結果存於 image folder 中的 tree.png 檔案

Crosswords：

確認模型路徑與匯入方式與題號(idx)正確後執行 run.py 即可開始

parameters.py 內存有參數可以做變更，更改 model_path 也在這裡

llm_function.py 內可更改 llm 的匯入方式，目前用手動註解方式調整

更改題號的方式為更改 parameters.py 中的 initial_idx 來更改開始題號，parameters.py 中的 question_sets

目前 crosswords 還沒將 acc 與 draw 串接進入 run.py，若想使用請手動更改操作 acc.py 與 draw.py

產生過程與 llm 回應會記錄於 record folder 中的 record.txt 中，每層結果與最終結果會記錄於 record folder 中的 tree.json 中，視覺化結果存於 image folder 中的 tree.png 檔案
