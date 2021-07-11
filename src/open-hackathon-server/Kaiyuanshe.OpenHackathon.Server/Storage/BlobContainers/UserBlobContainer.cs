using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers
{
    /// <summary>
    /// BlobContainer for user-uploaded files. Make sure to enable Static Website on the storage account.
    /// Reference: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website
    /// </summary>
    public interface IUserBlobContainer : IAzureBlobContainer
    {
    }

    public class UserBlobContainer: AzureBlobContainer, IUserBlobContainer
    {
        public UserBlobContainer(CloudStorageAccount storageAccount, string blobContainerName)
            : base(storageAccount, blobContainerName)
        {
        }
    }
}
