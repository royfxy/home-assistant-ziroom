# home-assistant-ziroom

Home Assistant 自如（ziroom）智能硬件集成，从 [homebridge-ziroom](https://github.com/baranwang/homebridge-ziroom) 移植。

## 支持设备

- ✅ 空调（conditioner02）
- ✅ 灯（light03 / light04）
- ⏳ 窗帘、浴霸、传感器（等待适配，欢迎 PR）

## 安装

### 通过 HACS 安装

1. 打开 HACS → 集成 → 点击 ➕ 搜索 "home-assistant-ziroom" 安装
2. 重启 Home Assistant

### 手动安装

```bash
git clone https://github.com/xingyuff/home-assistant-ziroom.git
cp -r home-assistant-ziroom/custom_components/ziroom <your_config_dir>/custom_components/
```

重启 Home Assistant。

## 配置

1. 在 Home Assistant → 设置 → 设备与服务 → 添加集成，搜索 **自如 Ziroom**
2. 输入你从自如 APP 抓包得到的 Token，可选输入 hid（合同号，如果不填会自动取第一个房间）
3. 完成，设备会自动发现添加

### 如何获取 Token

方法和 homebridge-ziroom 一样，需要自行抓包获取自如 APP 登录后的 Token。

## 鸣谢

- 原项目逆向和 API 分析来自 [@baranwang](https://github.com/baranwang) 的 [homebridge-ziroom](https://github.com/baranwang/homebridge-ziroom)

## License

MIT
