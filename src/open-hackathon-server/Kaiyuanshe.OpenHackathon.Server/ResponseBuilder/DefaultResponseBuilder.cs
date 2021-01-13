using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System.Collections.Generic;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.Server.ResponseBuilder
{
    public interface IResponseBuilder
    {
        Hackathon BuildHackathon(HackathonEntity hackathonEntity);
        HackathonList BuildHackathonList(IEnumerable<HackathonEntity> hackathonEntities);
    }

    public class DefaultResponseBuilder : IResponseBuilder
    {
        public Hackathon BuildHackathon(HackathonEntity hackathonEntity)
        {
            return new Hackathon
            {
                AutoApprove = hackathonEntity.AutoApprove,
                Banners = hackathonEntity.Banners,
                CreatorId = hackathonEntity.CreatorId,
                Detail = hackathonEntity.Detail,
                Location = hackathonEntity.Location,
                Name = hackathonEntity.Name,
                CreateTime = hackathonEntity.CreateTime,
                LastUpdateTime = hackathonEntity.Timestamp.DateTime,
                EnrollmentStartTime = hackathonEntity.EnrollmentStartTime,
                EnrollmentEndTime = hackathonEntity.EnrollmentEndTime,
                EventStartTime = hackathonEntity.EventStartTime,
                EventEndTime = hackathonEntity.EventEndTime,
                JudgeStartTime = hackathonEntity.JudgeStartTime,
                JudgeEndTime = hackathonEntity.JudgeEndTime,
                MaxEnrollment = hackathonEntity.MaxEnrollment,
                Ribbon = hackathonEntity.Ribbon,
                Status = hackathonEntity.Status,
                Summary = hackathonEntity.Summary,
                Tags = hackathonEntity.Tags
            };
        }

        public HackathonList BuildHackathonList(IEnumerable<HackathonEntity> hackathonEntities)
        {
            return new HackathonList
            {
                values = hackathonEntities.Select(h => BuildHackathon(h)).ToArray(),
            };
        }
    }
}
