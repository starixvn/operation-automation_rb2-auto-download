using System.IO.Compression;

namespace RB2Helper;
public class Zipper
{
    public static void ZipOriginalFile()
    {
        var files = Directory.GetFiles(@"C:\RB2", "*.xls", SearchOption.TopDirectoryOnly)
            .ToList();
        var zipFilePath = @"C:\RB2\Combined\RB2.zip";
        CreateZipFileFromList(files, zipFilePath);
    }

    public static void CreateZipFileFromList(List<string> filePaths, string zipFilePath)
    {
        try
        {
            if (File.Exists(zipFilePath))
            {
                File.Delete(zipFilePath);
            }

            using var zipToOpen = new FileStream(zipFilePath, FileMode.Create);
            using var archive = new ZipArchive(zipToOpen, ZipArchiveMode.Create);

            foreach (var filePath in filePaths)
            {
                var entryName = Path.GetFileName(filePath);
                archive.CreateEntryFromFile(filePath, entryName);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Đã xảy ra lỗi trong quá trình nén: {ex.Message}");
        }
    }
}
