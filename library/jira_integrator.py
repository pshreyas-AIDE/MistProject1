from jira import JIRA
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class JiraToolkit:
    def __init__(self, server_url, email, api_token):
        # Initializing connection with a 60-second timeout to handle Zscaler lag
        self.jira = JIRA(
            server=server_url,
            basic_auth=(email, api_token),
            options = {
            'timeout': 60,
            'verify': False  # This bypasses the SSL certificate check
        }
        )

    # --- READ OPERATIONS ---

    def search_by_keyword(self, project_key, keyword):
        """Search issues in a project containing a specific text string."""
        jql = f'textfields ~ "{keyword}" ORDER BY created DESC'
        #jql = f'project = "{project_key}" AND text ~ "{keyword}" ORDER BY created DESC'
        #jql = f'project = "{project_key}" AND summary ~ "{keyword}"'
        print(jql)
        return self.jira.search_issues(jql)

    def search_by_label(self, project_key, label):
        """Search issues in a project by a specific label."""
        jql = f'project = "{project_key}" AND labels = "{label}"'
        return self.jira.search_issues(jql)

    def get_issue_details(self, issue_key):
        """Retrieve core metadata for a single ticket."""
        issue = self.jira.issue(issue_key)
        return {
            "description": issue.fields.description,
            "labels": issue.fields.labels,
            "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "None",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "summary": issue.fields.summary
        }

    def get_comments(self, issue_key):
        """Retrieve all comments as a list of strings."""
        issue = self.jira.issue(issue_key)
        comments = issue.fields.comment.comments
        return [c.body for c in comments]

    # --- WRITE OPERATIONS ---

    def create_jira(self, project_key, summary, description, labels=None, issue_type="Task"):
        """Create a new Jira ticket."""
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            'labels': labels if labels else []
        }
        new_issue = self.jira.create_issue(fields=issue_dict)
        return new_issue.key

    def add_comment(self, issue_key, comment_text):
        """Add a new comment to an existing ticket."""
        return self.jira.add_comment(issue_key, comment_text)




# jt = JiraToolkit("https://mistsys.atlassian.net/", "pshreyas@juniper.net", "")
# res=jt.search_by_keyword("MIST","cpu")
# print(res)
# for i in res:
#     print(i)
# jt = JiraToolkit("https://mistsys.atlassian.net/", "pshreyas@juniper.net", "")
# res=jt.search_by_keyword("MIST","cpu")
# for i in res:
#     print(i)
#res=jt.get_comments("MIST-182565")


