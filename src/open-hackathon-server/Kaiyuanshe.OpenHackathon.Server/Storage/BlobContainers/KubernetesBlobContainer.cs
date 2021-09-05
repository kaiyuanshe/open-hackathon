using Microsoft.WindowsAzure.Storage;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers
{
    public interface IKubernetesBlobContainer
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
