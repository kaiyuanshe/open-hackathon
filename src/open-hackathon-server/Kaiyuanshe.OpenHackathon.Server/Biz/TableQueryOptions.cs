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
    }

    public class EnrollmentQueryOptions : TableQueryOptions
    {
        public EnrollmentStatus? Status { get; set; }
    }

    public class TeamQueryOptions : TableQueryOptions
    {

    }
}
