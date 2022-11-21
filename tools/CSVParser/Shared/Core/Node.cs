using System.Collections.Generic;

namespace CSVParser.Shared.Core
{
    public class Node
    {
        public long id;
        public List<Edge> adjacencyList = new List<Edge>();

        public Node(long id)
        {
            this.id = id;
        }
    }
}
