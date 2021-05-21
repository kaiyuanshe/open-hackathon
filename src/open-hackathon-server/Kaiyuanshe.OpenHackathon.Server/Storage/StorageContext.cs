using Kaiyuanshe.OpenHackathon.Server.Storage.Tables;

namespace Kaiyuanshe.OpenHackathon.Server.Storage
{
    public interface IStorageContext
    {
        IAwardTable AwardTable { get; }
        IEnrollmentTable EnrollmentTable { get; }
        IHackathonTable HackathonTable { get; }
        IHackathonAdminTable HackathonAdminTable { get; }
        ITeamTable TeamTable { get; }
        ITeamMemberTable TeamMemberTable { get; }
        IUserTable UserTable { get; }
        IUserTokenTable UserTokenTable { get; }
    }


    public class StorageContext : IStorageContext
    {
        IStorageAccountProvider StorageAccountProvider { get; }

        public IAwardTable AwardTable { get; }
        public IEnrollmentTable EnrollmentTable { get; }
        public IHackathonAdminTable HackathonAdminTable { get; }
        public IHackathonTable HackathonTable { get; }
        public ITeamTable TeamTable { get; }
        public ITeamMemberTable TeamMemberTable { get; }
        public IUserTable UserTable { get; }
        public IUserTokenTable UserTokenTable { get; }

        public StorageContext(IStorageAccountProvider storageAccountProvider)
        {
            StorageAccountProvider = storageAccountProvider;

            // tables
            var storageAccount = storageAccountProvider.HackathonServerStorage;
            AwardTable = new AwardTable(storageAccount, TableNames.Award);
            EnrollmentTable = new EnrollmentTable(storageAccount, TableNames.Enrollment);
            HackathonAdminTable = new HackathonAdminTable(storageAccount, TableNames.HackathonAdmin);
            HackathonTable = new HackathonTable(storageAccount, TableNames.Hackathon);
            TeamTable = new TeamTable(storageAccount, TableNames.Team);
            TeamMemberTable = new TeamMemberTable(storageAccount, TableNames.TeamMember);
            UserTable = new UserTable(storageAccount, TableNames.User);
            UserTokenTable = new UserTokenTable(storageAccount, TableNames.UserToken);
        }
    }
}
