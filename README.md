# 自如 Ziroom Home Assistant 集成

将自如智能硬件接入 Home Assistant。

## 支持的设备

- [x] 空调 (conditioner02)
- [x] 灯 (light03, light04) - 支持亮度和色温
- [x] 窗帘 (curtain01) - 支持位置控制

## 安装

### 通过 HACS 安装（推荐）

1. 打开 HACS
2. 点击「集成」
3. 点击右上角三个点，选择「自定义仓库」
4. 仓库地址：`https://github.com/royfxy/home-assistant-ziroom`
5. 类别：`集成`
6. 点击「添加」
7. 搜索「ziroom」并安装

### 手动安装

1. 将 `custom_components/ziroom/` 目录复制到你的 Home Assistant 配置目录下的 `custom_components/` 文件夹中
2. 重启 Home Assistant

## 配置

### 获取 Token

目前需要手动获取 Token。你可以：
1. 使用 Homebridge 版本的自动登录功能获取
2. 或者通过抓包方式从自如 App 获取

### 添加集成

1. 在 Home Assistant 中进入「配置」→「设备与服务」
2. 点击「添加集成」
3. 搜索「自如 Ziroom」
4. 输入你的 Token
5. 点击「提交」

## 使用

添加集成后，你的设备会自动出现在 Home Assistant 中：
- 空调作为气候实体
- 灯作为灯光实体
- 窗帘作为窗帘实体

## 测试

项目包含测试脚本，可以单独测试 API 功能：

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 创建 .env 文件
echo "ZIROOM_TOKEN=your_token" > .env

# 运行单元测试
python3 tests/unit/test_ziroom_api.py

# 列出所有灯
python3 tests/integration/test_light_control.py

# 列出所有空调
python3 tests/integration/test_aircon_control.py

# 列出所有窗帘
python3 tests/integration/test_curtain_control.py
```

## 开发

### 项目结构

```
home-assistant-ziroom/
├── custom_components/ziroom/    # Home Assistant 集成
│   ├── __init__.py
│   ├── climate.py               # 空调
│   ├── config_flow.py           # 配置流程
│   ├── const.py
│   ├── coordinator.py           # 数据协调器
│   ├── cover.py                 # 窗帘
│   ├── light.py                 # 灯
│   ├── manifest.json
│   ├── requirements.txt
│   └── ziroom_api.py            # API 客户端
└── tests/                       # 测试
    ├── unit/                     # 单元测试
    └── integration/              # 集成测试
```

## 致谢

基于 [baranwang/homebridge-ziroom](https://github.com/baranwang/homebridge-ziroom) 项目开发。
