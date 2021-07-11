using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;
using Kaiyuanshe.OpenHackathon.Server.Storage.BlobContainers;

namespace Kaiyuanshe.OpenHackathon.Server.Storage
{
    public interface IStorageContext
    {
        IStorageAccountProvider StorageAccountProvider { get; }

        IAwardTable AwardTable { get; }
        IAwardAssignmentTable AwardAssignmentTable { get; }
        IEnrollmentTable EnrollmentTable { get; }
        IHackathonTable HackathonTable { get; }
        IHackathonAdminTable HackathonAdminTable { get; }
        ITeamTable TeamTable { get; }
        ITeamMemberTable TeamMemberTable { get; }
        IUserTable UserTable { get; }
        IUserTokenTable UserTokenTable { get; }
        IUserBlobContainer UserBlobContainer { get; }
    }


    public class StorageContext : IStorageContext
    {
        public IStorageAccountProvider StorageAccountProvider { get; }

        public IAwardTable AwardTable { get; }
        public IAwardAssignmentTable AwardAssignmentTable { get; }
        public IEnrollmentTable EnrollmentTable { get; }
        public IHackathonAdminTable HackathonAdminTable { get; }
        public IHackathonTable HackathonTable { get; }
        public ITeamTable TeamTable { get; }
        public ITeamMemberTable TeamMemberTable { get; }
        public IUserTable UserTable { get; }
        public IUserTokenTable UserTokenTable { get; }
        public IUserBlobContainer UserBlobContainer { get; }

        public StorageContext(IStorageAccountProvider storageAccountProvider)
        {
            StorageAccountProvider = storageAccountProvider;

            // tables
            var storageAccount = storageAccountProvider.HackathonServerStorage;
            AwardTable = new AwardTable(storageAccount, TableNames.Award);
            AwardAssignmentTable = new AwardAssignmentTable(storageAccount, TableNames.AwardAssignment);
            EnrollmentTable = new EnrollmentTable(storageAccount, TableNames.Enrollment);
            HackathonAdminTable = new HackathonAdminTable(storageAccount, TableNames.HackathonAdmin);
            HackathonTable = new HackathonTable(storageAccount, TableNames.Hackathon);
            TeamTable = new TeamTable(storageAccount, TableNames.Team);
            TeamMemberTable = new TeamMemberTable(storageAccount, TableNames.TeamMember);
            UserTable = new UserTable(storageAccount, TableNames.User);
            UserTokenTable = new UserTokenTable(storageAccount, TableNames.UserToken);

            // blob containers
            UserBlobContainer = new UserBlobContainer(storageAccount, BlobContainerNames.StaticWebsite);
        }
    }
}
