using UnityEditor;
using UnityEngine;
using System.IO;

public class AutoDissolveMaterial : EditorWindow
{
    private string shaderPath = "MyDissolve"; // 修改为你的 Shader 路径

    [MenuItem("TA Tools/Auto Apply Dissolve Material")]
    static void Init()
    {
        AutoDissolveMaterial window = (AutoDissolveMaterial)EditorWindow.GetWindow(typeof(AutoDissolveMaterial));
        window.Show();
        ApplyDissolveMaterials();
    }

    static void ApplyDissolveMaterials()
    {
        string modelsFolder = "Assets/Models";
        string[] modelFiles = Directory.GetFiles(modelsFolder, "*.*", SearchOption.AllDirectories);

        foreach (string filePath in modelFiles)
        {
            string ext = Path.GetExtension(filePath).ToLower();
            if (ext == ".fbx" || ext == ".prefab")
            {
                ApplyMaterialToModel(filePath);
            }
        }
        Debug.Log("Auto Apply Dissolve Material Completed!");
    }

    static void ApplyMaterialToModel(string modelPath)
    {
        // 加载模型
        GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
        if (model == null) return;

        // 创建材质
        Material dissolveMat = new Material(Shader.Find("Shaders/Dissolve_Effect"));
        dissolveMat.name = model.name + "_Dissolve";

        // 应用材质
        Renderer renderer = model.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.sharedMaterial = dissolveMat;
        }

        // 保存材质球
        string matPath = Path.GetDirectoryName(modelPath) + "/" + dissolveMat.name + ".mat";
        AssetDatabase.CreateAsset(dissolveMat, matPath);
        AssetDatabase.SaveAssets();
    }
}