using System;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers
{

    public interface IAzureBlobContainer
    {
        string CreateSasToken();
    }

    public class AzureBlobContainer: IAzureBlobContainer
    {
        #region Constants
        /// <summary>
        /// The retry interval between for blob container retry operations
        /// </summary>
        static readonly int BlobContainerRetryInterval = 5;

        /// <summary>
        /// The retry count for blob container operations
        /// </summary>
        static readonly int BlobContaineRetryCount = 5;

        /// <summary>
        /// The default SAS time span in minutes
        /// </summary>
        static readonly int BlobContainerSasTimeSpan = 2; // minutes
        #endregion

        /// <summary>
        /// client to make request aganist azure blob container.
        /// </summary>
        protected readonly CloudBlobClient blobServiceProxy;

        /// <summary>
        /// proxy container that represents the azure blob container.
        /// </summary>
        protected readonly CloudBlobContainer blobContainerProxy;

        /// <summary>
        ///  The name of the blob container exists under the storage account with which this AzureBlobContainer is configured.
        /// </summary>
        protected readonly string blobName;

        /// <summary>
        /// Test-only constructor
        /// </summary>
        protected AzureBlobContainer()
        { }

        protected AzureBlobContainer(CloudStorageAccount storageAccount, string blobName)
        {
            this.blobName = blobName;
            blobServiceProxy = storageAccount.CreateCloudBlobClient();
            blobServiceProxy.DefaultRequestOptions.RetryPolicy = new Microsoft.WindowsAzure.Storage.RetryPolicies.LinearRetry(
                TimeSpan.FromSeconds(BlobContainerRetryInterval), BlobContaineRetryCount);
            blobContainerProxy = this.blobServiceProxy.GetContainerReference(this.blobName);
        }

        public string CreateSasToken()
        {
            var sasPolicy =
                new SharedAccessBlobPolicy
                {
                    SharedAccessExpiryTime = DateTime.UtcNow.AddMinutes(BlobContainerSasTimeSpan * 2),
                    SharedAccessStartTime = DateTime.UtcNow.Subtract(new TimeSpan(0, BlobContainerSasTimeSpan, 0)),
                    Permissions = SharedAccessBlobPermissions.Read | SharedAccessBlobPermissions.Write
                };
            return blobContainerProxy.GetSharedAccessSignature(sasPolicy);
        }
    }
}
