using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers
{
    public interface IKubernetesBlobContainer : IAzureBlobContainer
    {
    }

    public class KubernetesBlobContainer : AzureBlobContainer, IKubernetesBlobContainer
    {
        public KubernetesBlobContainer(CloudStorageAccount storageAccount, string blobContainerName)
              : base(storageAccount, blobContainerName)
        {
        }
    }
}
