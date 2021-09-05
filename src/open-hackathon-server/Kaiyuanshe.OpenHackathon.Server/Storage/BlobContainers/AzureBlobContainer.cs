using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;
using System;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers
{
    public interface IAzureBlobContainer
    {
        string CreateContainerSasToken(SharedAccessBlobPolicy policy);
        string CreateBlobSasToken(string blobName, SharedAccessBlobPolicy polich);
        Task<string> DownloadBlockBlobAsync(string blobName, CancellationToken cancellationToken);
    }

    public class AzureBlobContainer : IAzureBlobContainer
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
        protected readonly string containerName;

        /// <summary>
        /// Test-only constructor
        /// </summary>
        protected AzureBlobContainer()
        { }

        protected AzureBlobContainer(CloudStorageAccount storageAccount, string containerName)
        {
            this.containerName = containerName;
            blobServiceProxy = storageAccount.CreateCloudBlobClient();
            blobServiceProxy.DefaultRequestOptions.RetryPolicy = new Microsoft.WindowsAzure.Storage.RetryPolicies.LinearRetry(
                TimeSpan.FromSeconds(BlobContainerRetryInterval), BlobContaineRetryCount);
            blobContainerProxy = blobServiceProxy.GetContainerReference(this.containerName);
            blobContainerProxy.CreateIfNotExistsAsync().Wait();
        }

        public string CreateContainerSasToken(SharedAccessBlobPolicy policy)
        {
            return blobContainerProxy.GetSharedAccessSignature(policy);
        }

        public string CreateBlobSasToken(string blobName, SharedAccessBlobPolicy policy)
        {
            var blobProxy = blobContainerProxy.GetBlobReference(blobName);
            return blobProxy.GetSharedAccessSignature(policy);
        }

        public async Task<string> DownloadBlockBlobAsync(string blobName, CancellationToken cancellationToken)
        {
            var blob = blobContainerProxy.GetBlockBlobReference(blobName);
            using (MemoryStream stream = new MemoryStream())
            {
                await blob.DownloadToStreamAsync(stream, null, null, null, cancellationToken);
                return Encoding.UTF8.GetString(stream.ToArray());
            }
        }
    }
}
