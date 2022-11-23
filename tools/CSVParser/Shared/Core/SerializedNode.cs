using System.Collections.Generic;

namespace CSVParser.Shared.Core
{
    public class SerializedNode
    {
        public long id;
        public Dictionary<long, List<SerializedEdge>> adjacencyList = new();

        public SerializedNode(long id)
        {
            this.id = id;
        }
    }
}
