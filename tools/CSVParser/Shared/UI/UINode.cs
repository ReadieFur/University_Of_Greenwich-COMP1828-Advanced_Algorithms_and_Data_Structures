using System.Collections.Generic;
using CSVParser.Shared.Core;

namespace CSVParser.Shared.UI
{
    public class UINode : SerializedNode
    {
        public uint px = 0;
        public uint py = 0;
        public string label = "";
        new public Dictionary<long, List<UIEdge>> adjacencyList = new();

        public UINode(long id) : base(id) {}
    }
}
