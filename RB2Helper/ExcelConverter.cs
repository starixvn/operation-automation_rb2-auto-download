using NPOI.HSSF.UserModel;
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;
using System.Globalization;

namespace RB2Helper;

internal static class ExcelConverter
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
            var dates = GetAllDateTime(sheets);

            if (sport == "sc")
            {
                foreach (var date in dates)
                {
                    var from = date.AddHours(12);
                    var to = from.AddDays(1).AddMinutes(-1);
                    CombineFileForSoccer(date, from, to, sheets);
                }
            }
            else
            {
                CombineFileForOtherSports(sport, dates, sheets);
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

    private static void CombineFileForOtherSports(string sport, List<DateTime> dates, List<ISheet> sheets)
    {
        
        var date = dates.Min();
        var from = date.AddYears(-1);
        var to = date.AddYears(1);
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

        CopyRow(sheets[0], outputXssfSheet, outputXssfWorkbook, 0, 0);


        foreach (var sheet in sheets)
        {
            CopySheet(sheet, outputXssfSheet, outputXssfWorkbook, from, to);
        }


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
        CopyCellStyleXlsx(headerRow.GetCell(1), headerCell, workbook);

        for (var rowIndex = 1; rowIndex <= sheet.LastRowNum; rowIndex++)
        {
            var row = sheet.GetRow(rowIndex);
            var cell = row.CreateCell(2);
            cell.SetCellValue(sportType);
            CopyCellStyleXlsx(row.GetCell(1), cell, workbook);
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

        CopyRow(sheets[0], outputXssfSheet, outputXssfWorkbook, 0, 0);


        foreach (var sheet in sheets)
        {
            CopySheet(sheet, outputXssfSheet, outputXssfWorkbook, dateFrom, dateTo);
        }

        using var outputFileStream = new FileStream(combinedFile, FileMode.Create, FileAccess.Write);
        outputXssfWorkbook.Write(outputFileStream);
    }

    private static List<DateTime> GetAllDateTime(List<ISheet> sheets)
    {
        var dates = new List<DateTime>();

        foreach (var sheet in sheets)
        {
            for (var rowIdx = 1; rowIdx <= sheet.LastRowNum; rowIdx++)
            {
                var row = sheet.GetRow(rowIdx);
                if (row == null)
                {
                    continue;
                }
                var dateCell = row.GetCell(6);
                var dateTime = GetStartTime(dateCell.StringCellValue);
                if (dateTime != DateTime.MinValue && !dates.Contains(dateTime))
                {
                    dates.Add(dateTime);
                }
            }
        }

        return dates.Select(d => d.Date).Distinct().ToList();
    }

    private static void CopySheet(ISheet inputHssfSheet, ISheet outputXssfSheet, XSSFWorkbook outputXssfWorkbook, DateTime dateFrom, DateTime dateTo)
    {
        var destRowIndex = outputXssfSheet.LastRowNum + 1;
        for (var rowIdx = 1; rowIdx <= inputHssfSheet.LastRowNum; rowIdx++)
        {
            var hssfRow = inputHssfSheet.GetRow(rowIdx);
            if (hssfRow == null)
            {
                continue;
            }

            var dateCell = hssfRow.GetCell(6);
            var dateTime = GetStartTime(dateCell.StringCellValue);

            if (dateTime < dateFrom || dateTime > dateTo)
            {
                continue;
            }

            var playState = hssfRow.GetCell(10);
            if (string.Equals(playState.StringCellValue, "Cancelled", StringComparison.CurrentCultureIgnoreCase))
            {
                continue;
            }

            var xssfRow = outputXssfSheet.CreateRow(destRowIndex);
            for (var cellIdx = 0; cellIdx < hssfRow.LastCellNum; cellIdx++)
            {
                var hssfCell = hssfRow.GetCell(cellIdx);
                if (hssfCell == null)
                {
                    continue;
                }
                var xssfCell = xssfRow.CreateCell(cellIdx);
                CopyCellValue(hssfCell, xssfCell);
                CopyCellStyle(hssfCell, xssfCell, outputXssfWorkbook);
            }

            destRowIndex++;
        }
    }

    private static void CopyRow(
        ISheet inputHssfSheet,
        ISheet outputXssfSheet,
        XSSFWorkbook outputXssfWorkbook,
        int rowIdx,
        int destRowIndex)
    {
        var hssfRow = inputHssfSheet.GetRow(rowIdx);
        if (hssfRow == null)
        {
            return;
        }

        var xssfRow = outputXssfSheet.CreateRow(destRowIndex);
        for (var cellIdx = 0; cellIdx < hssfRow.LastCellNum; cellIdx++)
        {
            var hssfCell = hssfRow.GetCell(cellIdx);
            if (hssfCell != null)
            {
                var xssfCell = xssfRow.CreateCell(cellIdx);
                CopyCellValue(hssfCell, xssfCell);
                CopyCellStyle(hssfCell, xssfCell, outputXssfWorkbook);
            }
        }
    }

    private static void CopyCellValue(ICell sourceCell, ICell targetCell)
    {
        switch (sourceCell.CellType)
        {
            case CellType.Numeric:
                if (DateUtil.IsCellDateFormatted(sourceCell))
                {
                    var dateValue = sourceCell.DateCellValue;
                    if (dateValue.HasValue)
                    {
                        targetCell.SetCellValue(dateValue.Value);
                    }
                }
                else
                {
                    targetCell.SetCellValue(sourceCell.NumericCellValue);
                }
                break;
            case CellType.String:
                targetCell.SetCellValue(sourceCell.StringCellValue);
                break;
            case CellType.Boolean:
                targetCell.SetCellValue(sourceCell.BooleanCellValue);
                break;
            case CellType.Formula:
                targetCell.SetCellFormula(sourceCell.CellFormula);
                break;
            case CellType.Error:
                targetCell.SetCellErrorValue(sourceCell.ErrorCellValue);
                break;
            case CellType.Blank:
                // Leave blank
                break;
            default:
                targetCell.SetCellValue(sourceCell.ToString());
                break;
        }
    }

    private static void CopyCellStyle(ICell sourceCell, ICell targetCell, XSSFWorkbook targetWorkbook)
    {
        CopyCellStyleInternal(sourceCell, targetCell, targetWorkbook, isSourceXlsx: false);
    }

    private static void CopyCellStyleXlsx(ICell sourceCell, ICell targetCell, XSSFWorkbook targetWorkbook)
    {
        CopyCellStyleInternal(sourceCell, targetCell, targetWorkbook, isSourceXlsx: true);
    }

    private static void CopyCellStyleInternal(ICell sourceCell, ICell targetCell, XSSFWorkbook targetWorkbook, bool isSourceXlsx)
    {
        var sourceCellStyle = sourceCell.CellStyle;
        var targetCellStyle = targetWorkbook.CreateCellStyle();

        // Copy alignment
        targetCellStyle.Alignment = sourceCellStyle.Alignment;
        targetCellStyle.VerticalAlignment = sourceCellStyle.VerticalAlignment;
        targetCellStyle.Rotation = sourceCellStyle.Rotation;
        targetCellStyle.WrapText = sourceCellStyle.WrapText;
        targetCellStyle.Indention = sourceCellStyle.Indention;

        // Copy borders
        targetCellStyle.BorderLeft = sourceCellStyle.BorderLeft;
        targetCellStyle.BorderRight = sourceCellStyle.BorderRight;
        targetCellStyle.BorderTop = sourceCellStyle.BorderTop;
        targetCellStyle.BorderBottom = sourceCellStyle.BorderBottom;
        targetCellStyle.LeftBorderColor = sourceCellStyle.LeftBorderColor;
        targetCellStyle.RightBorderColor = sourceCellStyle.RightBorderColor;
        targetCellStyle.TopBorderColor = sourceCellStyle.TopBorderColor;
        targetCellStyle.BottomBorderColor = sourceCellStyle.BottomBorderColor;

        // Copy fill/background
        targetCellStyle.FillPattern = sourceCellStyle.FillPattern;
        targetCellStyle.FillForegroundColor = sourceCellStyle.FillForegroundColor;
        targetCellStyle.FillBackgroundColor = sourceCellStyle.FillBackgroundColor;

        // Copy font - handle both HSSF and XSSF workbooks
        var sourceWorkbook = sourceCell.Sheet.Workbook;
        var sourceFont = isSourceXlsx 
            ? sourceWorkbook.GetFontAt(sourceCellStyle.FontIndex)
            : ((HSSFWorkbook)sourceWorkbook).GetFontAt(sourceCellStyle.FontIndex);
        
        var targetFont = targetWorkbook.CreateFont();
        targetFont.FontName = sourceFont.FontName;
        targetFont.FontHeightInPoints = sourceFont.FontHeightInPoints;
        targetFont.IsBold = sourceFont.IsBold;
        targetFont.IsItalic = sourceFont.IsItalic;
        targetFont.IsStrikeout = sourceFont.IsStrikeout;
        targetFont.Underline = sourceFont.Underline;
        targetFont.Color = sourceFont.Color;
        targetCellStyle.SetFont(targetFont);

        // Copy number format
        targetCellStyle.DataFormat = targetWorkbook.CreateDataFormat().GetFormat(sourceCellStyle.GetDataFormatString());

        // Copy protection
        targetCellStyle.IsLocked = sourceCellStyle.IsLocked;
        targetCellStyle.IsHidden = sourceCellStyle.IsHidden;

        // Apply the style to the target cell
        targetCell.CellStyle = targetCellStyle;
    }

    private static DateTime GetStartTime(string dateString)
    {
        const string dateFormat = "dd.MM.yyyy - HH:mm";

        var success = DateTime.TryParseExact(
            dateString,
            dateFormat,
            CultureInfo.InvariantCulture,
            DateTimeStyles.None,
            out var dtObject
        );

        return success ? dtObject : DateTime.MinValue;
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
}