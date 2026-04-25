# My-TA-Journey

我的技术美术（TA）学习与实践项目。

## 目录结构
- `TechArt-Tools/` — 存放我开发的 TA 工具脚本（如贴图检查、批量处理等）
- `my-unity-dome/` — 我的 Unity 项目工程（用于测试工具）

## 工具列表
- `texture_checker.py` — 自动检查贴图尺寸和格式
- `material_batcher.py` — 批量合并材质（待开发）

## 如何运行
1. 克隆仓库：`git clone https://github.com/CHACHA1981/My-TA-Journey.git`
2. 进入工具目录：`cd TechArt-Tools`
3. 运行脚本：`python texture_checker.py`
   
## auto_dissolve_material.py
**功能**：自动化生成溶解材质并应用到Unity模型
**使用方法**：
1. 运行脚本：`python auto_dissolve_material.py`
2. 输入Unity项目路径
3. 在Unity中点击菜单：[TA Tools] -> [Auto Apply Dissolve Material]

**效果**：
- 自动为`Assets/Models/`下的所有模型创建溶解材质
- 材质名格式：`[模型名]_Dissolve.mat`
- 使用自定义`Dissolve_Effect.shadergraph`Shader
- 自动将材质应用到模型的Mesh Renderer
