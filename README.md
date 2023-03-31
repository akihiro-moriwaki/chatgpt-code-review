# chatgpt-code-review

## Setup

```yaml: openai.yaml
name: OpenAI

on:
  pull_request:
    types: [ opened, synchronize ]

jobs:
  chatgpt_review_job:
    runs-on: ubuntu-latest
    name: ChatGPT
    steps:
      - name: ChatGPT code review
        uses: akihiro-moriwaki/chatgpt-code-review@v0.0.1
        with:
          openai_token: ${{ secrets.OPENAI_API_KEY }}
          github_token: ${{ secrets.PERSONAL_TOKEN }}
          github_pull_request_id: ${{ github.event.number }}
```