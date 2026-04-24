import os
import sys

UNITY_CSHARP_SCRIPT = r'''using UnityEditor;
using UnityEngine;
using System.IO;
using System.Linq;

public class AutoDissolveMaterial : EditorWindow
{
    private int processedCount = 0;
    private int errorCount = 0;

    [MenuItem("TA Tools/Auto Apply Dissolve Material")]
    public static void ShowWindow()
    {
        GetWindow(typeof(AutoDissolveMaterial), true, "Auto Dissolve Material").Show();
        EditorApplication.update += ((AutoDissolveMaterial)EditorWindow.GetWindow(typeof(AutoDissolveMaterial))).OnGUIUpdate;
    }

    private void OnGUIUpdate()
    {
        EditorApplication.update -= OnGUIUpdate;
        ApplyDissolveMaterials();
    }

    void OnGUI()
    {
        GUILayout.Label("Automatically apply dissolve material to all FBX and Prefab models.", EditorStyles.boldLabel);
        if (GUILayout.Button("Run Now"))
        {
            ApplyDissolveMaterials();
        }
    }

    private void ApplyDissolveMaterials()
    {
        processedCount = 0;
        errorCount = 0;
        string modelsFolder = "Assets/Models";
        string[] allFiles = Directory.Exists(modelsFolder)
            ? Directory.GetFiles(modelsFolder, "*.*", SearchOption.AllDirectories)
            .Where(f => f.EndsWith(".fbx", System.StringComparison.OrdinalIgnoreCase)
                     || f.EndsWith(".prefab", System.StringComparison.OrdinalIgnoreCase)).ToArray()
            : null;

        if (allFiles == null || allFiles.Length == 0)
        {
            Debug.LogError("No .fbx or .prefab files found in Assets/Models directory!");
            EditorUtility.DisplayDialog("Auto Dissolve Material", "No FBX or Prefab files found in Assets/Models!", "OK");
            return;
        }

        int total = allFiles.Length;
        for (int i = 0; i < total; i++)
        {
            string assetPath = allFiles[i].Replace("\\", "/");
            EditorUtility.DisplayProgressBar("Auto Dissolve Material", $"Processing {Path.GetFileName(assetPath)} ({i + 1}/{total})", (float)i / total);

            try
            {
                GameObject obj = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
                if (obj == null)
                {
                    Debug.LogError($"Could not load asset: {assetPath}");
                    errorCount++;
                    continue;
                }

                string modelName = obj.name;
                string matDir = Path.GetDirectoryName(assetPath)?.Replace("\\", "/");
                if(string.IsNullOrEmpty(matDir)) matDir = "Assets/Models";
                string matName = $"{modelName}_Dissolve.mat";
                string matPath = $"{matDir}/{matName}";

                Shader dissolveShader = Shader.Find("Dissolve_Effect");
                if (dissolveShader == null)
                {
                    Debug.LogError("Could not find shader: Dissolve_Effect. Please make sure it exists.");
                    errorCount++;
                    continue;
                }

                Material mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
                if (mat == null)
                {
                    mat = new Material(dissolveShader);
                    AssetDatabase.CreateAsset(mat, matPath);
                    Debug.Log($"Created new material: {matPath}");
                }
                else
                {
                    mat.shader = dissolveShader;
                    EditorUtility.SetDirty(mat);
                }

                bool applied = false;

                // If this is a prefab
                if (assetPath.EndsWith(".prefab", System.StringComparison.OrdinalIgnoreCase))
                {
                    var renderers = obj.GetComponentsInChildren<MeshRenderer>(true);
                    if (renderers.Length == 0)
                        renderers = obj.GetComponents<MeshRenderer>();

                    if(renderers.Length > 0)
                    {
                        foreach (var renderer in renderers)
                        {
                            var mats = renderer.sharedMaterials;
                            for (int j = 0; j < mats.Length; j++)
                            {
                                mats[j] = mat;
                            }
                            renderer.sharedMaterials = mats;
                            EditorUtility.SetDirty(renderer);
                        }
                        // Save prefab changes
                        PrefabUtility.SavePrefabAsset(obj);
                        applied = true;
                    }
                }
                else if (assetPath.EndsWith(".fbx", System.StringComparison.OrdinalIgnoreCase))
                {
                    // FBX files are models, cannot be edited directly, but we can create a prefab (optional)
                    // Or reimport by script, but let's focus on prefabs and log.
                    Debug.Log($"FBX model found: {assetPath}. Please create a prefab to apply material.");
                }
                processedCount++;
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Exception processing {assetPath}: {ex.Message}");
                errorCount++;
            }
        }
        EditorUtility.ClearProgressBar();
        EditorUtility.DisplayDialog("Auto Dissolve Material",
            $"Processed: {processedCount}\nErrors: {errorCount}", "OK");
    }
}
'''

def create_csharp_script(unity_root):
    editor_folder = os.path.join(unity_root, 'Assets', 'Editor')
    cs_path = os.path.join(editor_folder, 'AutoDissolveMaterial.cs')
    try:
        if not os.path.exists(os.path.join(unity_root, 'Assets')):
            print('错误：未找到 Unity 项目 Assets 目录。')
            return False
        os.makedirs(editor_folder, exist_ok=True)
        with open(cs_path, 'w', encoding='utf-8') as f:
            f.write(UNITY_CSHARP_SCRIPT)
        print(f"成功生成: {cs_path}")
        return True
    except Exception as e:
        print(f"生成 C# 脚本失败: {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="为 Unity 项目的模型自动生成和应用溶解材质的 C# 编辑器脚本")
    parser.add_argument('unity_project_root', help='Unity 项目根目录路径')
    args = parser.parse_args()

    unity_root = args.unity_project_root

    if not os.path.isdir(unity_root):
        print("错误：指定的 Unity 项目路径不存在。")
        sys.exit(1)

    result = create_csharp_script(unity_root)
    if result:
        print("C# 编辑器脚本已生成，请在 Unity 编辑器中使用 [TA Tools/Auto Apply Dissolve Material] 菜单。")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()