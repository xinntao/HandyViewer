# ![icon](handyview/icon.png) HandyView

[English](README.md) **|** [简体中文](README_CN.md) &emsp; [GitHub](https://github.com/xinntao/HandyView) **|** [Gitee码云](https://gitee.com/xinntao/HandyView)

```Handy``` *Series*:

<img src="https://gitee.com/xinntao/HandyView/raw/master/handyview/icon.png" alt="HandyView Icon" width="36" height="36"> [HandyView](https://gitee.com/xinntao/HandyView) &emsp; <img src="https://gitee.com/xinntao/HandyFigure/raw/master/icon.png" alt="HandyFigure Icon" width="36" height="36"> [HandyFigure](https://gitee.com/xinntao/HandyFigure) &emsp; <img src="https://gitee.com/xinntao/HandyCrawler/raw/master/icon.png" alt="HandyCrawler Icon" width="36" height="36"> [HandyCrawler](https://gitee.com/xinntao/HandyCrawler)
&emsp; <img src="https://gitee.com/xinntao/HandyWriting/raw/master/icon.png" alt="HandyWriting Icon" width="36" height="36"> [HandyWriting](https://gitee.com/xinntao/HandyWriting)

---

HandyView 是一款基于 PyQt5 开发的方便的图像查看器. It provided convenient ways for viewing and comparing.

## :sparkles: Features

- Switch among images **with fixed zoom ration**, which is useful when comparing image details. (Unfortunately, I cannot find such a image viewer and this is the initial motivation to develop HandyView).
- Show basic image information, for example, image path, shape, size, color type, zoom ration, etc.
- Show the position and color in the current mouse cursor.

## :eyes: Screenshot

[To be updated]

<p align="center">
  <img src="assets/screenshot.png">
</p>

## :wrench: Usage

I have now tested it on Windows. It should also work on Ubuntu (but may with some modifications).

### <img src="https://upload.wikimedia.org/wikipedia/commons/8/8d/Windows_darkblue_2012.svg" alt="Windows" height="28">

#### Dependencies

- Anaconda (Python >= 3.5)

1. Clone repo

    ```bash
    git clone https://github.com/xinntao/HandyView.git
    ```

1. Install dependent packages

    ```bash
    cd HandyView
    pip install -r requirements.txt
    ```

In the command line, run:

> python handyview/handyview.py [image_path]

#### Compile to executable program

Use `pyinstaller` to compile to executable program, so that you can **double-click the image to open** the HandyView.

1. > pyinstaller -D handyview/handyview.py -i icon.ico --windowed
1. You will see a `dist` folder containing the outputs (dll, exe, etc)
1. Copy the `handyview/icons` folder and the `handyview/icon.png` image to the `dist` folder
1. Choose the `dist/handyview/handyview.exe` as the default image viewer.

### <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Logo-ubuntu_no%28r%29-black_orange-hex.svg" alt="Ubuntu" height="24">

I used Ubuntu in the previous versions. Now I switch to Windows (with wsl) for development.
So this is not tested on Ubuntu and may be out-of-date.

1. Clone this repo `git clone git@github.com:xinntao/HandyView.git`
1. How to double click to open an image
    1. Modify the HandyView.desktop file - *Exec & Icon*
    1. Copy the .desktop file to `/usr/share/applications`
1. How to change the default image viewer
    1. Right click an image
    1. Go to `Properties` -> `Open With`
    1. Choose *HandyView*

## :hourglass_flowing_sand: TODO list

### Compare operations

- [ ] Given two directories, it can compare the corresponding images.

### Editing operation

- [ ] Simple image edit: crop, resize, color convertion, etc.
- [ ] Draw rectangular and enlarged this area.
- [ ] Make gif easily.

## :books: References

- [Qt5 doc](https://doc.qt.io/qt-5/)
- [PyQt5 doc](https://doc.qt.io/qtforpython/api.html)
- [Key name](https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.Key.html)

## :scroll: 许可和致谢

本项目使用 [MIT license](./LICENSE).

### Icons

I have used the icons from [flaticon](www.flaticon.com). The following are the source links.

- [Open icon](https://www.flaticon.com/free-icon/open_3143203?term=file%20open&page=1&position=1)
- [Refresh icon](https://www.flaticon.com/free-icon/reuse_3299869?term=refresh&page=1&position=16)
- [Include icon](https://www.flaticon.com/free-icon/add_2921226)
- [Exclude icon](https://www.flaticon.com/free-icon/remove_2921203)
- [Compare icon](https://www.flaticon.com/free-icon/file-sharing_1037325?term=file%20compare&page=1&position=2)
- [History icon](https://www.flaticon.com/free-icon/timer_2921268)

## :e-mail: 联系

若有任何问题, 请提 issue 或者电邮 `xintao.wang@outlook.com`.
