# 第6回 デバッグ実習 配布code

第5回で `mean_rgb()` を切り出した画像解析アプリに、画像読込関数 `load_rgb_image()`（`image_io.py`）を追加した版である。
このアプリには **不具合が1件** 含まれている。症状を再現し、仮説と検証で原因を特定してから最小修正を入れる。

## 構成

```text
lesson06_debug/
├── app.py              Streamlitアプリ（画像の読込は load_rgb_image() を使う）
├── analysis.py         mean_rgb() / rgb_histograms()（第5回と同じ）
├── image_io.py         load_rgb_image()
├── test_analysis.py    第5回のtest 5件
├── conftest.py         tests/ 以下のtestから import できるようにするための空file
├── requirements.txt
├── sample.png          RGB PNG（640×480）
├── sample_rgba.png     RGBA PNG（sample.png に alpha channel を追加）
└── tests/
    └── data/
        ├── red_1px.png      赤1 pixel（RGBA）
        └── red_1px_rgb.png  赤1 pixel（RGB）
```

## 準備（WSL2のUbuntu）

第5回と同じpyenvの仮想環境を使う。

```text
$ cp -r lesson06_debug_starter ~/lesson06_debug
$ cd ~/lesson06_debug
$ pyenv local $(cd ~/practice && pyenv version-name)
$ python -m pip install -r requirements.txt
$ git init
$ git add .
$ git commit -m "Start lesson06 debug"
$ pytest -q
.....                                                                    [100%]
5 passed
```

## 症状の確認

```text
$ streamlit run app.py
```

1. `sample.png` をuploadする → 画像、幅・高さ、RGB平均、histogramが表示される
2. `sample_rgba.png` をuploadする → 何が起きるかを記録する

画面に表示された内容と、terminalに出たTracebackの最後の数行を `DEBUG_REPORT.md` に記録する。

## 注意

- `analysis.py` と `test_analysis.py` の期待値は変更しない（第5回で決めた入力契約である）
- 再現用testは `tests/test_color.py` として自分で作成する
- 修正は原因へ直接対応する1箇所だけにする
