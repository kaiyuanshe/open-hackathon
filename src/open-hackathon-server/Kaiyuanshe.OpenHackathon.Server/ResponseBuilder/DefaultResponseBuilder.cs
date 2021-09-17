using Kaiyuanshe.OpenHackathon.Server.K8S.Models;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.ResponseBuilder
{
    public interface IResponseBuilder
    {
        Hackathon BuildHackathon(HackathonEntity hackathonEntity, HackathonRoles roles);

        HackathonAdmin BuildHackathonAdmin(HackathonAdminEntity hackathonAdminEntity, UserInfo userInfo);

        Enrollment BuildEnrollment(EnrollmentEntity enrollmentEntity, UserInfo userInfo);

        Experiment BuildExperiment(ExperimentContext context, UserInfo userInfo);

        Team BuildTeam(TeamEntity teamEntity, UserInfo creator);

        TeamMember BuildTeamMember(TeamMemberEntity teamMemberEntity, UserInfo member);

        TeamWork BuildTeamWork(TeamWorkEntity teamWorkEntity);

        Template BuildTemplate(TemplateContext context);

        Award BuildAward(AwardEntity awardEntity);

        AwardAssignment BuildAwardAssignment(AwardAssignmentEntity awardAssignmentEntity, Team team, UserInfo user);

        Judge BuildJudge(JudgeEntity judgeEntity, UserInfo userInfo);

        RatingKind BuildRatingKind(RatingKindEntity ratingKindEntity);

        Rating BuildRating(RatingEntity ratingEntity, UserInfo judge, Team team, RatingKind ratingKind);

        TResult BuildResourceList<TSrcItem, TResultItem, TResult>(
            IEnumerable<TSrcItem> items,
            Func<TSrcItem, TResultItem> converter,
            string nextLink)
            where TResult : IResourceList<TResultItem>, new();

        TResult BuildResourceList<TSrcItem1, TSrcItem2, TResultItem, TResult>(
            IEnumerable<Tuple<TSrcItem1, TSrcItem2>> items,
            Func<TSrcItem1, TSrcItem2, TResultItem> converter,
            string nextLink)
            where TResult : IResourceList<TResultItem>, new();

        TResult BuildResourceList<TSrcItem1, TSrcItem2, TSrcItem3, TResultItem, TResult>(
            IEnumerable<Tuple<TSrcItem1, TSrcItem2, TSrcItem3>> items,
            Func<TSrcItem1, TSrcItem2, TSrcItem3, TResultItem> converter,
            string nextLink)
            where TResult : IResourceList<TResultItem>, new();

        Task<TResult> BuildResourceListAsync<TSrcItem, TResultItem, TResult>(
            IEnumerable<TSrcItem> items,
            Func<TSrcItem, CancellationToken, Task<TResultItem>> converter,
            string nextLink,
            CancellationToken cancellationToken = default)
            where TResult : IResourceList<TResultItem>, new();

        Task<TResult> BuildResourceListAsync<TSrcItem1, TSrcItem2, TResultItem, TResult>(
            IEnumerable<Tuple<TSrcItem1, TSrcItem2>> items,
            Func<TSrcItem1, TSrcItem2, CancellationToken, Task<TResultItem>> converter,
            string nextLink,
            CancellationToken cancellationToken = default)
            where TResult : IResourceList<TResultItem>, new();
    }

    public class DefaultResponseBuilder : IResponseBuilder
    {
        public Hackathon BuildHackathon(HackathonEntity hackathonEntity, HackathonRoles roles)
        {
            return hackathonEntity.As<Hackathon>(h =>
            {
                h.updatedAt = hackathonEntity.Timestamp.UtcDateTime;
                h.roles = roles;
            });
        }

        public HackathonAdmin BuildHackathonAdmin(HackathonAdminEntity hackathonAdminEntity, UserInfo userInfo)
        {
            return hackathonAdminEntity.As<HackathonAdmin>(h =>
            {
                h.updatedAt = hackathonAdminEntity.Timestamp.UtcDateTime;
                h.user = userInfo;
            });
        }

        public Enrollment BuildEnrollment(EnrollmentEntity enrollment, UserInfo userInfo)
        {
            return enrollment.As<Enrollment>(p =>
            {
                p.updatedAt = enrollment.Timestamp.UtcDateTime;
                p.user = userInfo;
            });
        }

        public Experiment BuildExperiment(ExperimentContext context, UserInfo userInfo)
        {
            return context.ExperimentEntity.As<Experiment>(p =>
            {
                p.updatedAt = context.ExperimentEntity.Timestamp.UtcDateTime;
                p.user = userInfo;
                p.status = Status.FromV1Status(context.Status);
            });
        }

        public Team BuildTeam(TeamEntity teamEntity, UserInfo creator)
        {
            return teamEntity.As<Team>(p =>
            {
                p.updatedAt = teamEntity.Timestamp.UtcDateTime;
                p.creator = creator;
            });
        }

        public TeamMember BuildTeamMember(TeamMemberEntity teamMemberEntity, UserInfo member)
        {
            return teamMemberEntity.As<TeamMember>(p =>
            {
                p.updatedAt = teamMemberEntity.Timestamp.UtcDateTime;
                p.user = member;
            });
        }

        public TeamWork BuildTeamWork(TeamWorkEntity teamWorkEntity)
        {
            return teamWorkEntity.As<TeamWork>(p =>
            {
                p.updatedAt = teamWorkEntity.Timestamp.UtcDateTime;
            });
        }

        public Template BuildTemplate(TemplateContext context)
        {
            return context.TemplateEntity.As<Template>(p =>
            {
                p.updatedAt = context.TemplateEntity.Timestamp.UtcDateTime;
                p.status = Status.FromV1Status(context.Status);
            });
        }

        public Award BuildAward(AwardEntity awardEntity)
        {
            return awardEntity.As<Award>(p =>
            {
                p.updatedAt = awardEntity.Timestamp.UtcDateTime;
            });
        }

        public AwardAssignment BuildAwardAssignment(AwardAssignmentEntity awardAssignmentEntity, Team team, UserInfo user)
        {
            return awardAssignmentEntity.As<AwardAssignment>((p) =>
            {
                p.updatedAt = awardAssignmentEntity.Timestamp.UtcDateTime;
                p.user = user;
                p.team = team;
            });
        }

        public Judge BuildJudge(JudgeEntity judgeEntity, UserInfo userInfo)
        {
            return judgeEntity.As<Judge>((p) =>
            {
                p.updatedAt = judgeEntity.Timestamp.UtcDateTime;
                p.user = userInfo;
            });
        }

        public RatingKind BuildRatingKind(RatingKindEntity ratingKindEntity)
        {
            return ratingKindEntity.As<RatingKind>((p) =>
            {
                p.updatedAt = ratingKindEntity.Timestamp.UtcDateTime;
            });
        }

        public Rating BuildRating(RatingEntity ratingEntity, UserInfo judge, Team team, RatingKind ratingKind)
        {
            return ratingEntity.As<Rating>((p) =>
            {
                p.updatedAt = ratingEntity.Timestamp.UtcDateTime;
                p.judge = judge;
                p.team = team;
                p.ratingKind = ratingKind;
            });
        }

        public TResult BuildResourceList<TSrcItem, TResultItem, TResult>(
            IEnumerable<TSrcItem> items,
            Func<TSrcItem, TResultItem> converter,
            string nextLink)
            where TResult : IResourceList<TResultItem>, new()
        {
            return new TResult
            {
                value = items.Select(p => converter(p)).ToArray(),
                nextLink = nextLink,
            };
        }

        public TResult BuildResourceList<TSrcItem1, TSrcItem2, TResultItem, TResult>(
            IEnumerable<Tuple<TSrcItem1, TSrcItem2>> items,
            Func<TSrcItem1, TSrcItem2, TResultItem> converter,
            string nextLink)
           where TResult : IResourceList<TResultItem>, new()
        {
            return new TResult
            {
                value = items.Select(p => converter(p.Item1, p.Item2)).ToArray(),
                nextLink = nextLink,
            };
        }

        public TResult BuildResourceList<TSrcItem1, TSrcItem2, TSrcItem3, TResultItem, TResult>(
            IEnumerable<Tuple<TSrcItem1, TSrcItem2, TSrcItem3>> items,
            Func<TSrcItem1, TSrcItem2, TSrcItem3, TResultItem> converter,
            string nextLink)
           where TResult : IResourceList<TResultItem>, new()
        {
            return new TResult
            {
                value = items.Select(p => converter(p.Item1, p.Item2, p.Item3)).ToArray(),
                nextLink = nextLink,
            };
        }

        public async Task<TResult> BuildResourceListAsync<TSrcItem, TResultItem, TResult>(
            IEnumerable<TSrcItem> items,
            Func<TSrcItem, CancellationToken, Task<TResultItem>> converter,
            string nextLink,
            CancellationToken cancellationToken = default)
            where TResult : IResourceList<TResultItem>, new()
        {
            List<TResultItem> list = new List<TResultItem>();
            foreach (var src in items)
            {
                var resultItem = await converter(src, cancellationToken);
                if (resultItem != null)
                {
                    list.Add(resultItem);
                }
            }

            return new TResult
            {
                value = list.ToArray(),
                nextLink = nextLink,
            };
        }

        public async Task<TResult> BuildResourceListAsync<TSrcItem1, TSrcItem2, TResultItem, TResult>(
            IEnumerable<Tuple<TSrcItem1, TSrcItem2>> items,
            Func<TSrcItem1, TSrcItem2, CancellationToken, Task<TResultItem>> converter,
            string nextLink,
            CancellationToken cancellationToken = default)
            where TResult : IResourceList<TResultItem>, new()
        {
            List<TResultItem> list = new List<TResultItem>();
            foreach (var src in items)
            {
                var resultItem = await converter(src.Item1, src.Item2, cancellationToken);
                if (resultItem != null)
                {
                    list.Add(resultItem);
                }
            }

            return new TResult
            {
                value = list.ToArray(),
                nextLink = nextLink,
            };
        }

    }
}
