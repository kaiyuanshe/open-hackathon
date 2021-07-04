using System;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers
{

    public interface IAzureBlobContainer
    {
        string CreateContainerSasToken(int expiration);
        string CreateBlobSasToken(int expiration, string blobName);
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
            blobContainerProxy = this.blobServiceProxy.GetContainerReference(this.containerName);
            blobContainerProxy.CreateIfNotExistsAsync().Wait();
        }

        protected SharedAccessBlobPolicy CreateSasPolicy(int expiration)
        {
            if (expiration > 0)
            {
                expiration = Math.Min(expiration, BlobContainerMaxSasExpiration);
                expiration = Math.Max(expiration, BlobContainerMinSasExpiration);
            }
            else
            {
                expiration = BlobContainerDefaultSasExpiration;
            }
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

        public string CreateContainerSasToken(int expiration)
        {
            var sasPolicy = this.CreateSasPolicy(expiration);
            return blobContainerProxy.GetSharedAccessSignature(sasPolicy);
        }

        public string CreateBlobSasToken(int expiration, string blobName)
        {
            var sasPolicy = this.CreateSasPolicy(expiration);
            var blobProxy = blobContainerProxy.GetBlobReference(blobName);
            return blobProxy.GetSharedAccessSignature(sasPolicy);
        }
    }
}
