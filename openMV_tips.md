openMV on Linux (run by VisionBoard)

# 安装&配置

在官网上下载，选用*.tar.gz*的方式比较方便，相比于*.run*。  

安装用`tar -xzvf ...`即可。  

使用ide连接时发现需要很长时间，并且还连不上。取消后会出现弹窗，说权限不足。  
这是linux的通病，之前用arduino也是。因为“一切皆文件”，所以像USB这类在设备树都是*/dev/tty*等。当时好像是直接给连接的那个端口chmod 666来开放所有权限，但是不安全，并且每次重新连接都要再次手动执行。  

所以需要一个更加理想的方式来告知系统，哪些设备是可以开放权限的。根据openMV官方的例子，创建一个**udev规则文件**就可以实现。但是在这之前，需要先知道设备的id与节点等。  

## 设备id

插入板子，用`lsusb`命令列出当前硬件usb上连接的设备，能够看到openMV：`Bus 001 Device 015: ID 1209:abd1 Generic OpenMV Cam`，那么其*idVendor*是1209，*idProduct*是abd1。  

## 设备权限与节点

插入板子，终端运行`ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null`来查看设备文件的权限和所属用户组，我的输出为`crw-rw---- 1 root dialout 166, 0  7月12日 21:12  /dev/ttyACM0`，说明openMV的设备组是*dialout*（大部分串口设备默认是 dialout 组），属于tty。  

输入`groups`命令查看当前用户的组，如果没有，可以用`sudo usermod -aG dialout $USER`来将当前用户增加到对应的组里。  

### usb组与tty组

上面的两个操作带来一个问题：为什么用*lsusb*与*ls -l ...*都能够得到openMV的相关信息？  

答案是*lsusb*会显示所有通过usb接口**“物理连接”**的设备，无论其究竟是什么，只要物理连接，就会列出来，是**总线级别**的，无论其是否被系统加载驱动、是否正常工作、是否挂载成文件系统、是否可访问。  

而后面查看ttyACM与ttyUSB，是**功能级别**的，只有设备别正确识别、加载相关驱动后才会创建一个与之相关的文件作为节点，譬如*/dev/ttyACM\**是CDC（通信设备类）设备（openMV、Arduino等）、*/dev/ttyUSB\**是USB-Serial芯片的设备（CH340等）。  

## udev规则文件

获取id与节点后，就可以创建udev规则文件了。  

首先在*/etc/udev/rules.d*路径内创建规则文件：`sudo nano /etc/udev/rules.d/99-visionboard.rules`，其中*99-visionboard.rules*是规则文件名称，遵从*数字-名称.rules*的命名规则，数字表示加载顺序，数字越小越早加载，选择99可以确保不会被覆盖；名称随便取；只要保证后缀是*.rules*即可。  

在规则文件内写入内容，如：
```
# OpenMV Cam USB device
SUBSYSTEM=="tty", ATTR{idVendor}=="1209", ATTR{idProduct}=="abd1", MODE="0666"
```
根据得到的*tty*、*1209*、*abd1*补全内容，将其模式定为*0666*表示所有用户对设备都有读写权限。  

接下来重新加载udev规则即可：  
```
sudo udevadm control --reload-rules
sudo udevadm trigger
```
此时就可以正常连接openMV ide了。  

# 关键函数

## 板载led

## 摄像头配置

### 分辨率

使用`sensor.set_framesize()`来设置  
可以是`sensor.SVGA`，800x600（似乎这是最大能达到的）  
也可以是更小的，比如`sensor.QVGA`，320x240  

### 镜头翻转

由于光学成像原因或者硬件原因，发现图像是完全翻转的。  
用`sensor.set_hmirror()`来水平翻转  
用`sensor.set_vflip()`来垂直翻转  

## 二维码识别

在获取图片后，对图像使用`Image.find_qrcodes()`方法即可得到`QRCode`对象。  

**QRCode对象常用方法：**  
+ 位置类：  
	x()、y()、w()、h()，其中x、y是矩形左上角的坐标，w、h是矩形的宽与高，可以由rect()统一获取。  
	更精确的，用corners()可以获得从左上角开始的顺时针的四点坐标。  
+ 数据获取：使用`payload()`即可获得二维码的有效载荷字符串。  
