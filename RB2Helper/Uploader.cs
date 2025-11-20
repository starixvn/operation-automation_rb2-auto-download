using System.Net.Http.Headers;

namespace RB2Helper;

public class Uploader
{
    private static readonly HttpClient Client = new HttpClient();

    public static async Task UploadAllFilesToInfoSite()
    {
        const string root = @"C:\RB2\Combined";
        var files = Directory.GetFiles(root, "*.xlsx", SearchOption.TopDirectoryOnly);
        foreach (var file in files)
        {
            try
            {
                var response = await UploadFile(file);
                Console.WriteLine($"Response: {response}");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Failed to upload file {file}: {ex.Message}");
            }
        }
    }

    public static async Task<string> UploadFile(string filePath)
    {
        // 2. Get the URL and file name
        const string infoSiteUrl = "https://generalexcelupload.klt2p.oneback.net/GeneralExcelUpload/UploadServiceExcel";
        var fileName = Path.GetFileName(filePath);
        Console.WriteLine($"Starting upload file: {fileName}");

        try
        {
            // 3. Prepare multipart/form-data content
            using var formData = new MultipartFormDataContent();

            // Add string fields
            formData.Add(new StringContent("agnos"), "service_name");
            formData.Add(new StringContent("true"), "is_upload_excel");

            // Read file content
            // **Important:** Ensure the file exists and you have access permissions
            await using var fileStream = File.OpenRead(filePath);

            // Set up file content
            var fileContent = new StreamContent(fileStream);

            // Assuming it's an Excel file (.xlsx), set the ContentType
            // C# does not need form.getHeaders(), HttpClient automatically creates the Boundary
            fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");

            // Add file content to form-data. The third parameter is the file name on the server.
            formData.Add(fileContent, "file", fileName);

            // 4. Set up Headers (e.g., Cookie)
            Client.DefaultRequestHeaders.Clear();
            Client.DefaultRequestHeaders.Add("Cookie", "InfoSite_UserId=699; InfoSite_UserName=Nexcel1");

            // 5. Execute the POST request (C# does not have onUploadProgress as easily as axios)
            // To achieve onUploadProgress, you would need to implement a custom HttpContent,
            // but the following is the simplest and most common way.
            Console.WriteLine("Uploading file...");

            var response = await Client.PostAsync(infoSiteUrl, formData);

            // 6. Process the response
            var responseData = await response.Content.ReadAsStringAsync();

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine($"\nUpload successful! Status: {(int)response.StatusCode}");
                return responseData;
            }
            else
            {
                Console.Error.WriteLine($"Error during upload: Status Code {(int)response.StatusCode}");
                Console.Error.WriteLine($"Response Data: {responseData}");
                throw new HttpRequestException($"Upload failed with status code: {response.StatusCode}");
            }
        }
        catch (FileNotFoundException ex)
        {
            Console.Error.WriteLine($"Error during upload: File not found at {filePath}. {ex.Message}");
            throw;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Error during upload: {ex.Message}");
            throw;
        }
    }
}