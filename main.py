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
ignore_phrases = ['特にありません', '改善なし', '改善点なし', '改善点はありません', '改善点は見当たりません', '改善点は見受けられません']


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


def is_binary(text: str) -> bool:
    return 'Binary' in text


def is_ignore_message(message: str) -> bool:
    contains_phrases = [phrase in message for phrase in ignore_phrases]
    return True in contains_phrases


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
                    'content': '次のコードのレビューをお願いします\n'
                               '# レビュー条件\n'
                               '- 改善点だけ教えてください\n'
                               '- 指摘事項は箇条書きかコードで教えてください\n'
                               '- 改善点がない場合は、"改善点なし"と知らせてください\n',
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
            if is_ignore_message(response['choices'][0]['message']['content']):
                continue
            pull_request.create_issue_comment(
                f"ChatGPT コードレビュー: ``{file_name}``\n\n {response['choices'][0]['message']['content']}")
        except Exception as e:
            print(str(e))
            pull_request.create_issue_comment(
                f"ChatGPT コードレビュー: ``{file_name}``\n\n 分析できませんでした")


if __name__ == '__main__':
    run()
