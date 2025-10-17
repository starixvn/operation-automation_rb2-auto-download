using NPOI.HSSF.UserModel;
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;
using System.Globalization;

namespace RB2Helper;

internal static class ExcelConverter
{
    private static readonly Dictionary<DateTime, string> MapFile = CreateMapFile();
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

    public static void Action()
    {
        var dates = MapFile.Keys.OrderBy(d => d).ToList();
        foreach (var date in dates)
        {
            CombineFile(date);
        }
    }

    private static void CombineFile(DateTime date)
    {
        if (!MapFile.ContainsKey(date) || !MapFile.ContainsKey(date.AddDays(1)))
        {
            return;
        }

        var file1 = MapFile[date];
        var file2 = MapFile[date.AddDays(1)];
        var combinedFile = Path.Combine(@"C:\RB2\Combined", $"RB2-{date:dd-MM-yyyy}sc.xlsx");
        var outputXssfWorkbook = new XSSFWorkbook();

        using var inputFileStream1 = new FileStream(file1, FileMode.Open, FileAccess.Read);
        var inputHssfWorkbook1 = new HSSFWorkbook(inputFileStream1);
        var inputHssfSheet1 = inputHssfWorkbook1.GetSheetAt(0);

        using var inputFileStream2 = new FileStream(file2, FileMode.Open, FileAccess.Read);
        var inputHssfWorkbook2 = new HSSFWorkbook(inputFileStream2);
        var inputHssfSheet2 = inputHssfWorkbook2.GetSheetAt(0);

        var outputXssfSheet = outputXssfWorkbook.CreateSheet(inputHssfSheet1.SheetName);
        // Copy column widths
        for (var colIdx = 0; colIdx < 256; colIdx++)
        {
            outputXssfSheet.SetColumnWidth(colIdx, inputHssfSheet1.GetColumnWidth(colIdx));
        }
        outputXssfSheet.DefaultRowHeight = inputHssfSheet1.DefaultRowHeight;
        outputXssfSheet.DefaultColumnWidth = inputHssfSheet1.DefaultColumnWidth;

        CopyRow(inputHssfSheet1, outputXssfSheet, outputXssfWorkbook, 0, 0);

        var from = date.AddHours(12);
        var to = date.AddHours(36).AddMinutes(-1);
        CopySheet(inputHssfSheet1, outputXssfSheet, outputXssfWorkbook, from, to);
        CopySheet(inputHssfSheet2, outputXssfSheet, outputXssfWorkbook, from, to);

        using var outputFileStream = new FileStream(combinedFile, FileMode.Create, FileAccess.Write);
        outputXssfWorkbook.Write(outputFileStream);
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
            if (string.Equals(playState.StringCellValue , "Cancelled", StringComparison.CurrentCultureIgnoreCase))
            {
                continue;
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

        // Copy font
        var sourceFont = ((HSSFWorkbook)sourceCell.Sheet.Workbook).GetFontAt(sourceCellStyle.FontIndex);
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

    public static Dictionary<DateTime, string> CreateMapFile()
    {
        var map = new Dictionary<DateTime, string>();
        var files = Directory.GetFiles(@"C:\RB2", "*.xls", SearchOption.TopDirectoryOnly);
        foreach (var file in files)
        {
            var name = Path.GetFileNameWithoutExtension(file);
            name = name.Replace("RB2-", "").Replace("sc", "");
            var date = DateTime.ParseExact(name, "dd-MM-yyyy", null);
            map[date] = file;
        }

        return map;
    }
}