using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.Server.ResponseBuilder
{
    public interface IResponseBuilder
    {
        Hackathon BuildHackathon(HackathonEntity hackathonEntity);

        HackathonList BuildHackathonList(IEnumerable<HackathonEntity> hackathonEntities);

        Enrollment BuildEnrollment(ParticipantEntity participant);
    }

    public class DefaultResponseBuilder : IResponseBuilder
    {
        public Hackathon BuildHackathon(HackathonEntity hackathonEntity)
        {
            return hackathonEntity.As<Hackathon>(h =>
            {
                h.updatedAt = hackathonEntity.Timestamp.DateTime;
            });
        }

        public HackathonList BuildHackathonList(IEnumerable<HackathonEntity> hackathonEntities)
        {
            return new HackathonList
            {
                values = hackathonEntities.Select(h => BuildHackathon(h)).ToArray(),
            };
        }

        public Enrollment BuildEnrollment(ParticipantEntity participant)
        {
            return participant.As<Enrollment>(p =>
            {
                p.updatedAt = participant.Timestamp.DateTime;
            });
        }
    }
}
