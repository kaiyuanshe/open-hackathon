using Kaiyuanshe.OpenHackathon.Server.Auth;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Blob;
using System;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IFileManagement
    {
        /// <summary>
        /// Get the upload URL.
        /// </summary>
        /// <returns></returns>
        Task<FileUpload> GetUploadUrlAsync(ClaimsPrincipal user, FileUpload request, CancellationToken cancellationToken = default);
    }

    public class FileManagement : ManagementClientBase, IFileManagement
    {
        public static readonly string HackathonApiStaticSite = "https://hackathon-api.static.kaiyuanshe.cn";

        private readonly ILogger Logger;

        /// <summary>
        /// The minimum SAS expiration time in minutes
        /// </summary>
        static readonly int BlobContainerMinSasExpiration = 2; // minutes

        /// <summary>
        /// The maximum SAS expiration time in minutes
        /// </summary>
        static readonly int BlobContainerMaxSasExpiration = 30; // minutes

        /// <summary>
        /// The default SAS expiration time in minutes
        /// </summary>
        static readonly int BlobContainerDefaultSasExpiration = 5; // minutes

        public FileManagement(ILogger<FileManagement> logger)
        {
            Logger = logger;
        }

        #region GetUploadUrlAsync
        internal int GetSASExpirationMinitues(FileUpload fileUpload)
        {
            var expirationInMinutes = fileUpload.expiration.GetValueOrDefault(BlobContainerDefaultSasExpiration);
            if (expirationInMinutes > BlobContainerMaxSasExpiration)
            {
                expirationInMinutes = BlobContainerMaxSasExpiration;
            }
            if (expirationInMinutes < BlobContainerMinSasExpiration)
            {
                expirationInMinutes = BlobContainerMinSasExpiration;
            }

            return expirationInMinutes;
        }


        private SharedAccessBlobPolicy GetSasPolicyForExternal(int expiration)
        {
            // get shared access policy for external users, with least privilege
            var leadingTime = BlobContainerMinSasExpiration; // avoid inconsistent timestamp between client and server
            var sasPolicy =
                new SharedAccessBlobPolicy
                {
                    SharedAccessExpiryTime = DateTime.UtcNow.AddMinutes(expiration + leadingTime),
                    SharedAccessStartTime = DateTime.UtcNow.Subtract(new TimeSpan(0, leadingTime, 0)),
                    Permissions = SharedAccessBlobPermissions.Read | SharedAccessBlobPermissions.Write
                };
            return sasPolicy;
        }

        private Tuple<string, string> GetBlobStorageBaseUrls()
        {
            var account = StorageContext.StorageAccountProvider.HackathonServerStorage;

            // read Url base
            string readUrlBase = HackathonApiStaticSite;
            if (EnvHelper.IsDevelopment() && !EnvHelper.IsRunningInTests())
            {
                // return Static WebSite url. Make sure it's enabled.
                // blob endpoint: https://accountName.blob.core.chinacloudapi.cn/
                // static website: https://accountName.z4.web.core.chinacloudapi.cn/
                string blobEndpoint = account.BlobEndpoint.AbsoluteUri.TrimEnd('/');
                readUrlBase = blobEndpoint.Replace(".blob.", ".z4.web.");
            }

            // write url base
            string writeUrlBase = account.BlobEndpoint.AbsoluteUri.TrimEnd('/');

            return Tuple.Create(readUrlBase, writeUrlBase);
        }

        public Task<FileUpload> GetUploadUrlAsync(ClaimsPrincipal user, FileUpload request, CancellationToken cancellationToken = default)
        {
            var expiration = GetSASExpirationMinitues(request);
            var accessPolicy = GetSasPolicyForExternal(expiration);

            // TOTO save upload history and apply throttling rules
            // TODO check file exitance

            string userId = ClaimsHelper.GetUserId(user);
            string blobName = $"{userId}/{DateTime.UtcNow.ToString("yyyy/MM/dd")}/{request.filename}";
            var sasToken = StorageContext.UserBlobContainer.CreateBlobSasToken(blobName, accessPolicy);

            // generate URLs
            var baseUrls = GetBlobStorageBaseUrls();
            request.expiration = expiration;
            request.url = $"{baseUrls.Item1}/{blobName}";
            request.uploadUrl = $"{baseUrls.Item2}/{BlobContainerNames.StaticWebsite}/{blobName}{sasToken}";
            return Task.FromResult(request);
        }
        #endregion
    }
}
