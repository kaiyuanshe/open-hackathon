using Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers;
using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;

namespace Kaiyuanshe.OpenHackathon.Server.Storage
{
    public interface IStorageContext
    {
        IStorageAccountProvider StorageAccountProvider { get; }

        IAwardTable AwardTable { get; }
        IAwardAssignmentTable AwardAssignmentTable { get; }
        IEnrollmentTable EnrollmentTable { get; }
        IExperimentTable ExperimentTable { get; }
        IHackathonTable HackathonTable { get; }
        IHackathonAdminTable HackathonAdminTable { get; }
        IJudgeTable JudgeTable { get; }
        IRatingTable RatingTable { get; }
        IRatingKindTable RatingKindTable { get; }
        ITeamTable TeamTable { get; }
        ITeamMemberTable TeamMemberTable { get; }
        ITemplateTable TemplateTable { get; }
        ITeamWorkTable TeamWorkTable { get; }
        IUserTable UserTable { get; }
        IUserTokenTable UserTokenTable { get; }
        IUserBlobContainer UserBlobContainer { get; }
        IKubernetesBlobContainer KubernetesBlobContainer { get; }
    }


    public class StorageContext : IStorageContext
    {
        public IStorageAccountProvider StorageAccountProvider { get; }

        public IAwardTable AwardTable { get; }
        public IAwardAssignmentTable AwardAssignmentTable { get; }
        public IEnrollmentTable EnrollmentTable { get; }
        public IExperimentTable ExperimentTable { get; }
        public IHackathonAdminTable HackathonAdminTable { get; }
        public IHackathonTable HackathonTable { get; }
        public IJudgeTable JudgeTable { get; }
        public IRatingTable RatingTable { get; }
        public IRatingKindTable RatingKindTable { get; }
        public ITeamTable TeamTable { get; }
        public ITeamMemberTable TeamMemberTable { get; }
        public ITeamWorkTable TeamWorkTable { get; }
        public ITemplateTable TemplateTable { get; }
        public IUserTable UserTable { get; }
        public IUserTokenTable UserTokenTable { get; }
        public IUserBlobContainer UserBlobContainer { get; }
        public IKubernetesBlobContainer KubernetesBlobContainer { get; }

        public StorageContext(IStorageAccountProvider storageAccountProvider)
        {
            StorageAccountProvider = storageAccountProvider;

            // tables
            var storageAccount = storageAccountProvider.HackathonServerStorage;
            AwardTable = new AwardTable(storageAccount, TableNames.Award);
            AwardAssignmentTable = new AwardAssignmentTable(storageAccount, TableNames.AwardAssignment);
            EnrollmentTable = new EnrollmentTable(storageAccount, TableNames.Enrollment);
            ExperimentTable = new ExperimentTable(storageAccount, TableNames.Experiment);
            HackathonAdminTable = new HackathonAdminTable(storageAccount, TableNames.HackathonAdmin);
            HackathonTable = new HackathonTable(storageAccount, TableNames.Hackathon);
            JudgeTable = new JudgeTable(storageAccount, TableNames.Judge);
            RatingTable = new RatingTable(storageAccount, TableNames.Rating);
            RatingKindTable = new RatingKindTable(storageAccount, TableNames.RatingKind);
            TeamTable = new TeamTable(storageAccount, TableNames.Team);
            TeamMemberTable = new TeamMemberTable(storageAccount, TableNames.TeamMember);
            TeamWorkTable = new TeamWorkTable(storageAccount, TableNames.TeamWork);
            TemplateTable = new TemplateTable(storageAccount, TableNames.Template);
            UserTable = new UserTable(storageAccount, TableNames.User);
            UserTokenTable = new UserTokenTable(storageAccount, TableNames.UserToken);

            // blob containers
            UserBlobContainer = new UserBlobContainer(storageAccount, BlobContainerNames.StaticWebsite);
            KubernetesBlobContainer = new KubernetesBlobContainer(storageAccount, BlobContainerNames.Kubernetes);
        }
    }
}
