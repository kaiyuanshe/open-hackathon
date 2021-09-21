using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;

namespace Kaiyuanshe.OpenHackathon.Server.K8S.Models
{
    public class ExperimentContext
    {
        public ExperimentEntity ExperimentEntity { get; set; }
        public ExperimentStatus Status { get; set; }
    }
}
