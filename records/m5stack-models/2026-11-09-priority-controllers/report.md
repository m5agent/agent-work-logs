# 执行报告

源码基线为 `f998b2d655a310156ff1de1eaff3854a7cca7122`。发布提交为 `de6cddc065674ecb53bba29c7fe90d9ab4ee32f7`。新增四款各自官方 CAD 衍生结构、可见接口、输入和显示组件。Paper 系列的反射式表面使用竖屏坐标，Cardputer 提供 56 键扫描元数据，CoreMatrix 接收 256 字节强度帧。官方原始参考文件仅作为来源记录。局部内藏补建件与行程仍为外观推导。

## 执行命令

在源码提交运行以下命令。浏览器复验使用同一个静态生产入口和各型号 URL。

```sh
npm ci --ignore-scripts
npm run catalog
node scripts/check-priority-hosts.mjs
npm run check:demo
npm run check:controllers
npm run check:connections
npm run check:input-picking
npm run build
node scripts/check-atom-stick-artwork-build.mjs
```

在含 [浏览器脚本](code/verify-pages.mjs) 的目录中可用 Playwright 复验。用 `CHROME_PATH` 指定 Chrome 可执行文件或预先安装 Playwright Chromium。

```sh
npm install --no-save playwright-core@1.65.0
node verify-pages.mjs https://yuyun2000.github.io/m5stack-models/ ./captures
```

## 验证边界

浏览器执行 WebGL 生产页面，抓取正、背和立体视图及校准帧。浏览器输入包含 PaperS3 的触控开始、移动和结束，以及初代 Cardputer 的焦点键盘按下与释放。每款还验证相应的面板实体键命令可达。帧缓冲、按键、连接和像素专项另有 Node 检查。设备验证标签为 `virtual-device validation`，限定于 Three.js 外观层。固件镜像、芯片、总线时序与实物配合未执行。

## 回滚

通过原仓库撤销发布提交并由既有 GitHub Actions 重新部署。线上运行编号与静态资源摘要在 [run.json](run.json) 和 [证据目录](evidence/)。
