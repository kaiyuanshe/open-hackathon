using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers
{
    public interface IUserBlobContainer : IAzureBlobContainer
    {
    }

    public class UserBlobContainer: AzureBlobContainer, IUserBlobContainer
    {
        public UserBlobContainer(CloudStorageAccount storageAccount, string blobName)
            : base(storageAccount, blobName)
        {
        }
    }
}
