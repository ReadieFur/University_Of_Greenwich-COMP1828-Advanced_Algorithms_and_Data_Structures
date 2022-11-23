using CSVParser.Shared.Core;

namespace CSVParser.Shared.UI
{
    public class UIEdge : SerializedEdge
    {
        public string label { get; set; }

        public UIEdge(long id) : base(id) {}
    }
}
