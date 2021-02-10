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
    }

    public class DefaultResponseBuilder : IResponseBuilder
    {
        public Hackathon BuildHackathon(HackathonEntity hackathonEntity)
        {
            return hackathonEntity.As<Hackathon>();
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
