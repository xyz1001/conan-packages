# Conan Third-Party Packages (第三方库打包仓库)

专门用于维护与分发**官方 ConanCenter 未合入或需要定制的第三方 C/C++ 库**。通过 **GitHub Actions** 自动化跨平台构建（Windows / Linux），并将二进制包与配方托管在 **GitLab Package Registry** 上。

> [!NOTE]
> 对于个人自研或自有开源项目（如 [elevate-kit](https://github.com/xyz1001/elevate-kit)），已采用在其**自身原仓库**直接构建发布模式，本仓库专注于外部第三方库的打包。

---

## 🚀 外部用户使用方式（免登录直接拉取）

任何人均可直接在本地添加本源，无需账号或 Token：

### 1. 添加远端仓库
```bash
conan remote add xyz1001-conan https://gitlab.com/api/v4/projects/88391881/packages/conan
```

### 2. 在项目中使用包
在你的 `conanfile.py` 或 `conanfile.txt` 中引用：

```python
# conanfile.py
def requirements(self):
    self.requires("webview/0.12.0@xyz1001/stable")
```

安装并自动解析二进制（若平台无预编译会自动从配方编译）：
```bash
conan install . --build=missing
```

---

## 📦 当前已维护的第三方库列表

| 包名 | 版本 | 完整引用 | 支持平台 | 简介 |
| :--- | :--- | :--- | :--- | :--- |
| **webkit2gtk** | `system` | `webkit2gtk/system@xyz1001/stable` | Linux | WebKit GTK 系统库绑定 |
| **webview** | `0.12.0` | `webview/0.12.0@xyz1001/stable` | Windows / Linux | 轻量级跨平台 Webview C/C++ 封装 |

---

## 🛠️ 如何添加新的第三方库

### 1. 新增 Recipe 目录结构
在 `recipes/` 目录下按以下标准结构创建你的第三方库配方：

```text
recipes/
└── <你的库名>/
    └── all/
        ├── conanfile.py
        └── conandata.yml (可选，如果从官方 tarball / git 源码拉取)
```

### 2. 本地测试打包（可选）
在本地根目录下运行构建测试：
```bash
python scripts/build.py --package <你的库名>
```

### 3. 推送到 GitHub 自动发布
提交并推送到 `main` 分支：
```bash
git add recipes/<你的库名>
git commit -m "feat: add <你的库名> recipe"
git push origin main
```

推送后，**GitHub Actions** 会自动触发矩阵编译（Ubuntu + Windows），并将打好的二进制包与 Recipe 自动上传至 GitLab 仓库。

---

## ⚙️ 架构说明

* **代码与配方托管**：[GitHub (xyz1001/conan-packages)](https://github.com/xyz1001/conan-packages)
* **CI 构建平台**：GitHub Actions（免费每月 2,000 分钟，支持多操作系统矩阵构建）
* **二进制与制品存储**：[GitLab (xyz1001/conan-packages)](https://gitlab.com/xyz1001/conan-packages)（Project ID: `88391881`）
