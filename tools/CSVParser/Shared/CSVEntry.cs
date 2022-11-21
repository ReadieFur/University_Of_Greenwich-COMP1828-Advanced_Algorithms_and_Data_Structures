#nullable enable
namespace CSVParser.Shared
{
    public class CSVEntry
    {
        public string Line { get; set; } = string.Empty;
        public string Station { get; set; } = string.Empty;
        public string? NextStation { get; set; } = string.Empty;
        public string Weight { get; set; } = string.Empty;
    }
}
