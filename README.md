## ラジオゾンデとXCTDを使った大気・海洋時間断面の作図

## 'no' requrements
[bsod](https://github.com/sotomita/bsod.git)と[ctdxctdxbt](https://github.com/sotomita/ctdxctdxbt.git)により変換されたデータ'のみ'を使い，作図を行います．このスクリプトは`bsod`にも`ctdxctdxbt`にも依存してないスタンドアローンです．最低限numpy, pandas, matplotlibは必要です．（サンプルデータの便宜上ctdxctdxbtがいるように見えますが，カタチだけです）

## How to use?
1. `namelist.py`を修正し，以下を指定します

- ラジオゾンデ変換後データのディレクトリパス
- ラジオゾンデの野帳ファイル
- XCTD変換後データのディレクトリパス


2. `time_seq_atm_ocean.py`内の上部にある変数を修正します

| 変数       | 説明                                                      | 
| ---------- | --------------------------------------------------------- | 
| var_sonde  | ラジオゾンデデータの変数名                                | 
| top        | ラジオゾンデの描画高度上限 m                              | 
| var_xctd   | XCTDの変数名                                              | 
| bottom     | XCTDの描画深度下限 m                                      | 
| cut_top    | XCTDの表層の欠損扱いの幅（default: 2m)  | 
| cut_bottom | XCTDの深層の欠損扱いの幅（default: 50m) | 

3. `time_seq_atm_ocean.py`を実行します

```bash
python3 time_seq_atm_ocean.py
```


