import argparse
import openai
import os
import requests
from github import Github

# arguments
parser = argparse.ArgumentParser()
parser.add_argument('--openai_api_key', help='Your OpenAI API Key', required=True)
parser.add_argument('--github_token', help='Your Github Token', required=True)
parser.add_argument('--github_pull_request_id', help='Your Github PR ID', required=True)
args = parser.parse_args()

openai.api_key = args.openai_api_key
github = Github(args.github_token)
repo_str = os.getenv('GITHUB_REPOSITORY')


def get_content_patch() -> str:
    url = f'https://api.github.com/repos/{repo_str}/pulls/{args.github_pull_request_id}'
    headers = {
        'Authorization': f'token {args.github_token}',
        'Accept': 'application/vnd.github.v3.diff'
    }
    response = requests.request('GET', url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)

    return response.text


def is_binary(text) -> bool:
    return 'Binary' in text


def run():
    content = get_content_patch()
    if len(content) == 0:
        return

    repo = github.get_repo(repo_str)
    pull_request = repo.get_pull(int(args.github_pull_request_id))

    diff_contents = content.split('diff')
    for diff_content in diff_contents:
        if len(diff_content) == 0:
            continue

        try:
            if is_binary(diff_content):
                continue
            arr = diff_content.split('b/')
            if len(arr) <= 1:
                continue
            file_name = diff_content.split('b/')[1].splitlines()[0]

            messages = [
                {
                    'role': 'user',
                    'content': '次のコードのレビューをお願いします',
                },
                {
                    'role': 'user',
                    'content': diff_content,
                }
            ]
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=messages,
            )
            pull_request.create_issue_comment(
                f"ChatGPT コードレビュー: ``{file_name}``\n\n {response['choices'][0]['message']['content']}")
        except Exception as e:
            raise Exception(e)
            

if __name__ == '__main__':
    run()
