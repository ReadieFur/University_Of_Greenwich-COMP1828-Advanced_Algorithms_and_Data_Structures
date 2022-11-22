using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using F23.StringSimilarity;
using Newtonsoft.Json;
using Tesseract;
using CSVParser.Shared;

#nullable enable
namespace CSVParser
{
    internal class OCR
    {
        public static List<OCREntry> DoOCR()
        {
            List<OCREntry> ocrEntries = new();
            TesseractEngine engine = new TesseractEngine(Path.Combine(Environment.CurrentDirectory,
                true ? "tessdata_best-4.1.0" : "tessdata_fast-4.1.0"), "eng", EngineMode.LstmOnly);
            Pix image = Pix.LoadFromFile(Path.Combine(Environment.CurrentDirectory, "./standard-tube-map-1.png"));
            image.XRes = 2735;
            image.YRes = 1909;
            using (var page = engine.Process(image, PageSegMode.AutoOsd))
            {
                ResultIterator result = page.GetIterator();
                result.Begin();
                PageIteratorLevel pageIteratorLevel = PageIteratorLevel.Word;
                while (result.Next(pageIteratorLevel))
                {
                    bool gotRect = result.TryGetBoundingBox(pageIteratorLevel, out Rect rect);
                    /*using (var graphics = Graphics.FromImage(systemImage))
                    {
                        graphics.DrawRectangle(Pens.Red, rect.X1, rect.Y1, rect.Width, rect.Height);
                    }*/

                    if (!gotRect)
                        continue;

                    string word = result.GetText(pageIteratorLevel).Trim();

                    float confidence = result.GetConfidence(pageIteratorLevel);

                    //Console.WriteLine(word);
                    //Console.WriteLine(rect);
                    //Console.WriteLine(confidence);

                    ocrEntries.Add(new()
                    {
                        Text = word.Trim(),
                        //BoundingBox = new Rectangle(rect.X1, rect.Y1, rect.Width, rect.Height),
                        PX = rect.X1,
                        PY = rect.Y1,
                        Confidence = confidence
                    });
                }
            }
            //Save the ocrEntries to a JSON file.
            File.WriteAllText(Path.Combine(Environment.CurrentDirectory, "ocrEntries.json"), JsonConvert.SerializeObject(ocrEntries));

            return ocrEntries;
        }

        public static IEnumerable<UIEntry> MatchValues(List<CSVEntry> csvEntries, List<OCREntry> ocrEntries)
        {
            //For each CSVEntry, find the closest OCREntry text.
            //This matching method isn't the best but it cleans up the data enough that it makes manually cleaning up the data feasible.
            foreach (CSVEntry csvEntry in csvEntries)
            {
                OCREntry closestEntry = ocrEntries[0];
                float closestDistance = float.MaxValue;
                foreach (OCREntry ocrEntry in ocrEntries)
                {
                    float distance = (float)new Levenshtein().Distance(csvEntry.Station.Split(' ')[0], ocrEntry.Text);
                    //If the distance is within the margin of the confidence, then we can use this entry.
                    if (100 - distance >= ocrEntry.Confidence && distance < closestDistance)
                    {
                        closestDistance = distance;
                        closestEntry = ocrEntry;
                    }
                }

                //(int px, int py) = TranslateImagePosToMapPos(closestEntry.BoundingBox.X, closestEntry.BoundingBox.Y);
                // (int px, int py) = TranslateImagePosToMapPos(closestEntry.PX, closestEntry.PY);
                const int mapWidth = 1024;
                const int mapHeight = 768;
                const int imageWidth = 2735;
                const int imageHeight = 1909;
                const int imageSpacingBottom = 53;
                const int imageSpacingRight = 0;
                const int targetWidth = mapWidth - imageSpacingRight;
                const int targetHeight = mapHeight - imageSpacingBottom;

                // int px = (int)Math.Round((double)closestEntry.BoundingBox.X / imageWidth * targetWidth);
                // int py = (int)Math.Round((double)closestEntry.BoundingBox.Y / imageHeight * targetHeight);
                int px = (int)Math.Round((double)closestEntry.PX / imageWidth * targetWidth);
                int py = (int)Math.Round((double)closestEntry.PY / imageHeight * targetHeight);

                yield return new()
                {
                    Line = csvEntry.Line.Trim(),
                    Station = csvEntry.Station.Trim(),
                    NextStation = csvEntry.NextStation!.Trim(),
                    Weight = csvEntry.Weight,
                    PX = px,
                    PY = py
                };
            }
        }
    }
}
