using CSVParser.Shared.Core;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MultigraphUI = CSVParser.Shared.UI;

namespace CSVParser.Patchers
{
    internal class ToMultigraph
    {
        public static void Convert()
        {
            UIGraph patchData = JsonConvert.DeserializeObject<UIGraph>(File.ReadAllText("./london_underground_data-ui-patch-data.json"))!;

            //As I only need the node information from this file, I can skip attempting to match the edges.
            MultigraphUI.UIGraph multigraph = new MultigraphUI.UIGraph
            {
                nodes = patchData.nodes.Select(n => new MultigraphUI.UINode(n.id)
                {
                    label = n.label,
                    px = n.px,
                    py = n.py
                }).ToList()
            };

            File.WriteAllText("./london_underground_data-ui-patch-data-multigraph.json", JsonConvert.SerializeObject(multigraph, Formatting.Indented));
        }

        private class UIGraph
        {
            public List<UINode> nodes = new List<UINode>();
        }

        private class UINode
        {
            public long id;
            public List<Edge> adjacencyList = new List<Edge>();
            public uint px = 0;
            public uint py = 0;
            public string label = "";

            public UINode(long id)
            {
                this.id = id;
            }
        }

        private class Edge
        {
            public long neighbouringNodeID;
            public uint weight = 1;

            public Edge(long id)
            {
                neighbouringNodeID = id;
            }
        }
    }
}
