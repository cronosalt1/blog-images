#!/usr/bin/env python3
"""
AI 뉴스 Blogger 포스팅 스크립트
Obsidian markdown 파일을 HTML 로 변환하여 Blogger 에 포스팅
"""

import json
import markdown
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 오늘 날짜 계산
today = datetime.now()
date_str_dash = today.strftime('%Y-%m-%d')
date_str_nodash = today.strftime('%Y%m%d')
month_dir = today.strftime('%Y%m')

# Obsidian 파일 읽기
obsidian_path = Path(f'/Volumes/Data/SynologyDrive/Study/Obsidian/Memo/Personal Project/AI News/{month_dir}/{date_str_nodash}_AI_News.md')
print(f"Reading Obsidian file: {obsidian_path}")

with open(obsidian_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

print(f"Markdown content length: {len(md_content)} chars")

# Markdown → HTML 변환
html_content = markdown.markdown(md_content, extensions=['extra', 'meta', 'toc', 'nl2br'])
print(f"HTML content length: {len(html_content)} chars")

# 토큰 로드 및 갱신
TOKEN_FILE = Path('/Users/cronos/.hermes/blog-automation/token.json')
CLIENT_SECRET_FILE = Path('/Users/cronos/.hermes/blog-automation/client_secret.json')

print(f"Loading token from: {TOKEN_FILE}")
with open(TOKEN_FILE, 'r') as f:
    token_data = json.load(f)

print(f"Token data keys: {token_data.keys()}")

creds = Credentials(
    token=token_data.get('token'),
    refresh_token=token_data.get('refresh_token'),
    token_uri=token_data.get('token_uri'),
    client_id=token_data.get('client_id'),
    client_secret=token_data.get('client_secret'),
    scopes=token_data.get('scopes', [])
)

print(f"Credentials loaded. Valid: {creds.valid}, Expired: {creds.expired if hasattr(creds, 'expired') else 'N/A'}")

if not creds.valid:
    print("Token invalid, refreshing...")
    try:
        creds.refresh(Request())
        print("Token refreshed successfully")
        with open(TOKEN_FILE, 'w') as f:
            json.dump({
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,',
                'client_id': creds.client_id,
                'client_secret':': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }, f, indent=2)
        print("Token file updated")
    except Exception as e:
        print(f"Token refresh failed: {e}")
        raise

# Blogger 에 포스팅
print("Building Blogger service...")
service = build('blogger', 'v3', credentials=creds)

# AI 이미지 URL (이미 생성된 것 사용)
ai_image_url = f"https://raw.githubusercontent.com/cronosalt1/blog-images/main/ai_news_{date_str_nodash[:8]}.png"

# HTML 콘텐츠에 AI 이미지 추가
full_html = f"""
<div style="text-align: center; margin: 20px 0;">
    <img src="{ai_image_url}" alt="AI News {date_str_dash}" style="max-width: 100%; height: auto; border-radius: 8px;">
</div>
{html_content}
"""

print("Creating blog post...")
post = service.posts().insert(
    blogId='1680453488594010619',
    body={
        'title': f'AI 뉴스 요약 - {date_str_dash}',
        'content': full_html,
        'labels': ['AI_News', 'Automation', date_str_dash, 'OpenSource', 'OpenWeights', 'LLM'],
        'status': 'LIVE'
    }
).execute()

print(f"\n✅ Post created successfully!")
print(f"📝 Title: {post.get('title', 'N/A')}")
print(f"🔗 URL: {post.get('url', 'N/A')}")
print(f"🏷️  Labels: {', '.join(post.get('labels', []))}")
print(f"📊 Status: {post.get('status', 'N/A')}")
print(f"🖼️  AI Image: {ai_image_url}")
