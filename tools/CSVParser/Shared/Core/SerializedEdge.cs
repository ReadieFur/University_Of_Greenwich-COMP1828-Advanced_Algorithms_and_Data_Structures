namespace CSVParser.Shared.Core
{
    public class SerializedEdge
    {
        public long id;
        public uint weight = 1;

        public SerializedEdge(long id)
        {
            this.id = id;
        }
    }
}
