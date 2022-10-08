# Authentication抓取教程（电脑版）
## 文字教程
1. 在浏览器页面按F12或右键选择“检查”打开控制台
2. 在网址栏输入网址 http://pdc.njtech.edu.cn/?ticket=ST-4729436-EhmVzjAndWoRz675YBZl-cas01.example.org#/dform/genericForm/wbfjIwyK
3. 在弹出的控制台里选择“Network”（“网络”）标签，并筛选“Fetch/XHR”请求
4. 在筛选到的请求里找到以loadFormListBySUrl开头的这个请求，并点击右侧的“Headers”（“标头”）标签，即可在“Request Headers”（“请求标头”）里看到Authentication字段，将引号后的内容复制下来填入脚本。

## 图片教程（Chrome浏览器）
![图片教程](./%E5%9B%BE%E7%89%87%E6%95%99%E7%A8%8B.jpg)