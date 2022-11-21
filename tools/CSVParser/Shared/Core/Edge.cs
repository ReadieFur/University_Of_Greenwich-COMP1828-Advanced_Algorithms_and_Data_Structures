namespace CSVParser.Shared.Core
{
    public class Edge
    {
        public long neighbouringNodeID;
        public uint weight = 1;

        public Edge(long id)
        {
            neighbouringNodeID = id;
        }
    }
}
