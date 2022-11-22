using System.IO;
using Newtonsoft.Json;
using CSVParser.Shared.UI;

#nullable enable
namespace CSVParser.Patchers
{
    internal class UIPatcher
    {
        public static void Patch()
        {
            UIGraph sourceData = JsonConvert.DeserializeObject<UIGraph>(File.ReadAllText("./london_underground_data-auto.json"))!;
            UIGraph patchData = JsonConvert.DeserializeObject<UIGraph>(File.ReadAllText("./london_underground_data-ui-patch-data.json"))!;

            foreach (UINode node in sourceData.nodes)
            {
                UINode? patchNode = patchData.nodes.Find(n => n.label.Trim() == node.label.Trim());
                if (patchNode == null)
                    continue;

                node.px = patchNode.px;
                node.py = patchNode.py;
            }

            File.WriteAllText("./london_underground_data-ui-patched.json", JsonConvert.SerializeObject(sourceData, Formatting.Indented));
        }
    }
}
