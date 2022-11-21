using System.Collections.Generic;
using CSVParser.Shared.Core;

namespace CSVParser.Shared.UI
{
    public class UINode : Node
    {
        public uint px = 0;
        public uint py = 0;
        public string label = "";
        new public List<UIEdge> adjacencyList = new List<UIEdge>();

        public UINode(long id) : base(id) {}
    }
}
