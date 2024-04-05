import pulumi
import pulumi_github as github
from pulumi import ResourceOptions

from .utils import DATADIR, resource_kwargs, yaml


class Organization:
    def __init__(self, data: dict):
        self.data: dict = data
        self.name = data["organization"]["name"]
        self.repos: dict[str, github.Repository] = {}
        self.teams: dict[str, github.Team] = {}
        self.users: dict[str, github.Membership] = {}
        for repo in self.data.get("repositories", ()):
            self.repos[repo["name"]] = self.setup_repo(repo)
        for user in self.data.get("users", ()):
            self.users[user["name"]] = self.setup_user(user)
        for team in self.data.get("teams", ()):
            self.teams[team["name"]] = self.setup_team(team)


    @classmethod
    def from_yaml_path(cls, path):
        return cls(yaml.load(path))

    def setup_repo(self, repo):
        if repo["name"] in self.repos:
            raise ValueError(f"Repo {repo['name']} is duplicated.")
        repo_resource = github.Repository(
            repo["name"],
            name=repo["name"],
            allow_auto_merge=repo.get("allow_auto_merge"),
            allow_merge_commit=repo.get("allow_merge_commit"),
            allow_rebase_merge=repo.get("allow_rebase_merge"),
            allow_squash_merge=repo.get("allow_squash_merge"),
            archive_on_destroy=repo.get("archive_on_destroy"),
            archived=repo.get("archived"),
            auto_init=repo.get("auto_init"),
            # default_branch=repo.get("default_branch", "main"),
            delete_branch_on_merge=repo.get("delete_branch_on_merge"),
            description=repo.get("description"),
            gitignore_template=repo.get("gitignore_template"),
            has_downloads=repo.get("has_downloads", True),
            has_issues=repo.get("has_issues", True),
            has_projects=repo.get("has_projects", True),
            has_wiki=repo.get(
                "has_wiki", False if repo.get("visibility") == "private" else True
            ),
            homepage_url=repo.get("homepage_url"),
            ignore_vulnerability_alerts_during_read=repo.get(
                "ignore_vulnerability_alerts_during_read"
            ),
            is_template=repo.get("is_template"),
            license_template=repo.get("license_template"),
            merge_commit_message=repo.get("merge_commit_message"),
            merge_commit_title=repo.get("merge_commit_title"),
            # pages=repo.get("pages"),
            squash_merge_commit_message=repo.get("squash_merge_commit_message"),
            squash_merge_commit_title=repo.get("squash_merge_commit_title"),
            template=repo.get("template"),
            topics=repo.get("topics"),
            visibility=repo.get("visibility"),
            vulnerability_alerts=repo.get(
                "vulnerability_alerts",
                False if repo.get("visibility") == "private" else True,
            ),
            opts=ResourceOptions(**resource_kwargs(repo)),
        )
        if repo.get("default_branch"):
            github.BranchDefault(
                f"{repo['name']}-{repo['default_branch']}",
                branch=repo["default_branch"],
                repository=repo["name"],
                opts=ResourceOptions(**resource_kwargs(repo, id_key="default_branch")),
            )
        return repo_resource

    def setup_user(self, user: dict) -> github.Membership:
        return github.Membership(
            f"{self.name}-member-{user['name']}",
            username=user["name"],
            role=user.get("role", "member"),
            opts=ResourceOptions(**resource_kwargs(user)),

        )

    def setup_team(self, team: dict) -> github.Team:
        parent_team_name = team.get("parent")
        if parent_team_name:
            parent_team = self.teams.get(parent_team_name)
            if not parent_team:
                raise ValueError(
                    "Parent team not yet defined. Make sure parents show up earlier."
                )
            parent_team_id = parent_team.id
        else:
            parent_team_id = None

        team_resource = github.Team(
            team.get("slug", team["name"].lower().strip().replace(" ", "-")),
            name=team["name"],
            description=team.get("description"),
            privacy=team.get("privacy", "closed"),
            parent_team_id=parent_team_id,
            opts=ResourceOptions(**resource_kwargs(team)),
        )
        members = team.get("members", ())
        if not members:
            raise ValueError("Team entries must define 'members'.")

        for user in members:
            if isinstance(user, str):
                user = {"name": user}
            # Add a user to the newly created team
            _ = github.TeamMembership(
                f"{team['name']}-{user['name']}",
                team_id=team_resource.id,
                username=user["name"],
                role=user.get("role"),
                opts=ResourceOptions(**resource_kwargs(user)),
            )

        for repo in team.get("repositories", []):
            if repo["name"] not in self._repos:
                print(f"Repository '{repo['name']}' not managed by Pulumi. Skipping.")
                continue

            # Associate a repository with the team
            _ = github.TeamRepository(
                f"{team['name']}-{repo['name']}",
                team_id=team_resource.id,
                repository=self._repos[repo["name"]],
                permission=repo.get("permission"),
                opts=ResourceOptions(**resource_kwargs(repo)),
            )

        return team_resource


Organization.from_yaml_path(DATADIR / "github.yaml")
