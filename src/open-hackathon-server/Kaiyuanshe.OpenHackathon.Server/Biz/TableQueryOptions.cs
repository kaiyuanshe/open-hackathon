using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public class TableQueryOptions
    {
        public TableContinuationToken TableContinuationToken { get; set; }
        public int? Top { get; set; }
        public TableContinuationToken Next { get; set; }
    }

    public class HackathonQueryOptions : TableQueryOptions
    {
        /// <summary>
        /// search in name/display name/desc
        /// </summary>
        public string Search { get; set; }

        /// <summary>
        /// Ordering. default to createdAt.
        /// </summary>
        public HackathonOrderBy? OrderBy { get; set; }
    }

    public class EnrollmentQueryOptions : TableQueryOptions
    {
        public EnrollmentStatus? Status { get; set; }
    }

    public class TeamQueryOptions : TableQueryOptions
    {

    }

    public class TeamMemberQueryOptions : TableQueryOptions
    {
        public TeamMemberRole? Role { get; set; }
        public TeamMemberStatus? Status { get; set; }
    }

    public class AwardQueryOptions : TableQueryOptions
    {

    }
}
