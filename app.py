"""Streamlit image analysis app.

Displays the input image, its width/height, RGB mean values, and RGB histograms.
No external network communication is performed, and the uploaded image is never
written to disk; everything is processed in memory only.
"""

import io

import numpy as np
import streamlit as st
import torch

from analysis import mean_rgb, rgb_histograms
from image_io import load_rgb_image


def get_device() -> str:
    """Pick the best available compute device: cuda > mps > cpu."""
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main() -> None:
    st.set_page_config(page_title="画像解析アプリ", layout="centered")
    st.title("画像解析アプリ")

    device = get_device()
    st.caption(f"実行デバイス: **{device}**")

    uploaded_file = st.file_uploader(
        "PNG または JPEG 画像を1枚アップロードしてください",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is None:
        st.info("画像をアップロードすると解析結果が表示されます。")
        return

    # Read bytes into memory only; never written to disk.
    image_bytes = uploaded_file.getvalue()
    array = load_rgb_image(io.BytesIO(image_bytes))

    st.subheader("画像")
    st.image(array, use_container_width=True)

    height, width = array.shape[:2]
    col1, col2 = st.columns(2)
    col1.metric("幅 (px)", width)
    col2.metric("高さ (px)", height)

    r_mean, g_mean, b_mean = mean_rgb(array)

    st.subheader("RGB 平均値")
    col_r, col_g, col_b = st.columns(3)
    col_r.metric("R 平均", f"{r_mean:.2f}")
    col_g.metric("G 平均", f"{g_mean:.2f}")
    col_b.metric("B 平均", f"{b_mean:.2f}")

    st.subheader("RGB ヒストグラム")
    # pyarrow(st.bar_chart)に依存しないよう、matplotlibで直接描画する。
    # matplotlibは日本語フォントに対応していないため、軸ラベル等は英語表記にする。
    import matplotlib.pyplot as plt

    x = np.arange(256)
    hists = rgb_histograms(array)
    y_max = max(h.max() for h in hists.values())

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
    for ax, color, label in zip(axes, ("red", "green", "blue"), ("R", "G", "B")):
        ax.bar(x, hists[label], width=1.0, color=color, label=label)
        ax.set_ylim(0, y_max)
        ax.set_ylabel("Frequency")
        ax.legend()
    axes[-1].set_xlabel("Pixel Value")
    st.pyplot(fig)


if __name__ == "__main__":
    main()
