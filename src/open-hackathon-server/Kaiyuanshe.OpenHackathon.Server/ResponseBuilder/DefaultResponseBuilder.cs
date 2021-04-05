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

        Enrollment BuildEnrollment(EnrollmentEntity participant);

        TResult BuildResourceList<TSrcItem, TResultItem, TResult>(IEnumerable<TSrcItem> items, Func<TSrcItem, TResultItem> converter, string nextLink)
            where TResult : IResourceList<TResultItem>, new();
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

        public Enrollment BuildEnrollment(EnrollmentEntity participant)
        {
            return participant.As<Enrollment>(p =>
            {
                p.updatedAt = participant.Timestamp.DateTime;
            });
        }

        public TResult BuildResourceList<TSrcItem, TResultItem, TResult>(IEnumerable<TSrcItem> items, Func<TSrcItem, TResultItem> converter, string nextLink)
            where TResult : IResourceList<TResultItem>, new()
        {
            return new TResult
            {
                value = items.Select(p => converter(p)).ToArray(),
                nextLink = nextLink,
            };
        }
    }
}
