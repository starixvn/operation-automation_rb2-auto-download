using NPOI.HSSF.UserModel;
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;

namespace RB2Helper;

internal static class ExcelMerger
{
    private const string RootDirectory = @"C:\RB2\Combined";
    public static void Prepare()
    {
        if (!Directory.Exists(RootDirectory))
        {
            Directory.CreateDirectory(RootDirectory);
        }
        else
        {
            // Delete all files in the directory
            var files = Directory.GetFiles(RootDirectory);
            foreach (var file in files)
            {
                File.Delete(file);
            }
        }
    }

    public static void Action(string sport)
    {
        List<FileStream> fileStreams = [];
        List<HSSFWorkbook> workbooks = [];
        try
        {
            var files = Directory.GetFiles(@"C:\RB2", "*.xls", SearchOption.TopDirectoryOnly);
            if (files.Length == 0)
            {
                Console.WriteLine("No files are detected");
                return;
            }

            fileStreams = files.Select(f => new FileStream(f, FileMode.Open, FileAccess.Read)).ToList();
            workbooks = fileStreams.Select(fs => new HSSFWorkbook(fs)).ToList();
            var sheets = workbooks.Select(wb => wb.GetSheetAt(0)).ToList();
            var dates = ExcelHelper.GetAllDateTime(sheets);

            if (sport == "sc")
            {
                for (var i = 0; i < 14; i++)
                {
                    var date = DateTime.Today.AddDays(i);
                    var from = date.AddHours(12);
                    var to = from.AddDays(1).AddMinutes(-1);
                    CombineFileForSoccer(date, from, to, sheets);
                }
            }
            else
            {
                var sunday0 = GetPreviousSunday(DateTime.Today);
                var sunday1 = sunday0.AddDays(7);
                var sunday2 = sunday1.AddDays(7);
                var from1 = DateTime.Today.AddHours(12);
                var to1 = sunday1.AddHours(12).AddMinutes(-1);
                var from2 = sunday1.AddHours(12);
                var to2 = sunday2.AddHours(12).AddMinutes(-1);

                CombineFileForOtherSports(sport, sheets, sunday0, from1, to1);
                CombineFileForOtherSports(sport, sheets, sunday1, from2, to2);
            }
        }
        catch (Exception e)
        {
            Console.WriteLine(e.Message);
        }
        finally
        {
            fileStreams.ForEach(f => f.Dispose());
            workbooks.ForEach(w =>
            {
                w.Close();
                w.Dispose();
            });
        }
    }

    private static void CombineFileForOtherSports(string sport, List<ISheet> sheets, DateTime date, DateTime dateFrom, DateTime dateTo)
    {
        var combinedFile = Path.Combine(@"C:\RB2\Combined", $"RB2-{date:dd-MM-yyyy}{sport}.xlsx");

        using var outputXssfWorkbook = new XSSFWorkbook();
        var outputXssfSheet = outputXssfWorkbook.CreateSheet("RB fixtures");

        // Copy column widths
        for (var colIdx = 0; colIdx < 256; colIdx++)
        {
            outputXssfSheet.SetColumnWidth(colIdx, sheets[0].GetColumnWidth(colIdx));
        }
        outputXssfSheet.DefaultRowHeight = sheets[0].DefaultRowHeight;
        outputXssfSheet.DefaultColumnWidth = sheets[0].DefaultColumnWidth;

        ExcelHelper.CopyRow(sheets[0], outputXssfSheet, outputXssfWorkbook, 0, 0);

        ExcelHelper.CopySheet(sheets, outputXssfSheet, outputXssfWorkbook, dateFrom, dateTo);

        var sportType = GetSportType(sport);
        InsertSportType(outputXssfWorkbook, outputXssfSheet, sportType);

        using var outputFileStream = new FileStream(combinedFile, FileMode.Create, FileAccess.Write);
        outputXssfWorkbook.Write(outputFileStream);
    }

    private static void InsertSportType(XSSFWorkbook workbook, ISheet sheet, string sportType)
    {
        var headerRow = sheet.GetRow(0);
        var headerCell = headerRow.CreateCell(2);
        headerCell.SetCellValue("Sports");
        ExcelHelper.CopyCellStyleXlsx(headerRow.GetCell(1), headerCell, workbook);

        for (var rowIndex = 1; rowIndex <= sheet.LastRowNum; rowIndex++)
        {
            var row = sheet.GetRow(rowIndex);
            var cell = row.CreateCell(2);
            cell.SetCellValue(sportType);
            ExcelHelper.CopyCellStyleXlsx(row.GetCell(1), cell, workbook);
        }

        sheet.AutoSizeColumn(2);
    }

    private static void CombineFileForSoccer(DateTime date, DateTime dateFrom, DateTime dateTo, List<ISheet> sheets)
    {
        var combinedFile = Path.Combine(@"C:\RB2\Combined", $"RB2-{date:dd-MM-yyyy}sc.xlsx");

        using var outputXssfWorkbook = new XSSFWorkbook();
        var outputXssfSheet = outputXssfWorkbook.CreateSheet("RB fixtures");

        // Copy column widths
        for (var colIdx = 0; colIdx < 256; colIdx++)
        {
            outputXssfSheet.SetColumnWidth(colIdx, sheets[0].GetColumnWidth(colIdx));
        }
        outputXssfSheet.DefaultRowHeight = sheets[0].DefaultRowHeight;
        outputXssfSheet.DefaultColumnWidth = sheets[0].DefaultColumnWidth;

        ExcelHelper.CopyRow(sheets[0], outputXssfSheet, outputXssfWorkbook, 0, 0);

        ExcelHelper.CopySheet(sheets, outputXssfSheet, outputXssfWorkbook, dateFrom, dateTo);
        
        using var outputFileStream = new FileStream(combinedFile, FileMode.Create, FileAccess.Write);
        outputXssfWorkbook.Write(outputFileStream);
    }

    
    private static string GetSportType(string sport)
    {
        return sport switch
        {
            "sc" => "Soccer",
            "ck" => "Cricket",
            "i.hockey" => "Ice Hockey",
            "bb" => "Basketball",
            "tennis" => "Tennis",
            _ => "Other Sports"
        };
    }

    public static DateTime GetPreviousSunday(DateTime date)
    {
        // DayOfWeek returns: Sunday (0), Monday (1), ..., Saturday (6)
        var dayOfWeek = (int)date.DayOfWeek;
        return date.AddDays(-dayOfWeek);
    }
}