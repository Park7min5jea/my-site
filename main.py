# -*- coding: utf-8 -*-
import openai
import os
import json
from dotenv import load_dotenv

# 🔐 API 키 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print("✅ API 키 확인:", bool(openai.api_key))  # 없으면 False 출력됨

# 📄 템플릿 HTML 파일 읽기
with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

# 📢 광고 코드 (예시: 애드센스)
ad_code = """
<!-- AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1110612793488080" crossorigin="anonymous"></script>
<ins class="adsbygoogle" style="display:block" data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
"""

# 🧠 GPT 호출 함수
def generate_content(index):
    prompt = f"""
    아래 형식의 JSON만 출력하세요. 설명, 인사 없이 아래 형식만 출력하세요:

    {{
      "title": "제목 {index}",
      "description": "설명 {index}",
      "content": "본문 내용 {index}"
    }}
    """

    prompt = prompt.replace("{", "{{").replace("}", "}}")  # GPT 이스케이프 처리

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 또는 gpt-4
        messages=[{"role": "user", "content": prompt}]
    )

    # GPT 응답 처리
    text = response.choices[0].message.content.strip()
    print(f"\n📥 GPT 응답 {index}:\n{text}")

    if not text:
        raise ValueError("GPT 응답이 비어 있습니다.")

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("응답에서 JSON 블록을 찾지 못했습니다:\n" + text)

    json_str = text[start:end]

    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"JSON 파싱 실패:\n{json_str}\n에러: {e}")

    if not all(k in data for k in ["title", "description", "content"]):
        raise ValueError("title / description / content 키가 빠졌습니다:\n" + str(data))

    return data

# 📂 출력 디렉토리 생성
os.makedirs("output_pages", exist_ok=True)

# 🔁 HTML 페이지 10개 생성
for i in range(1, 11):
    data = generate_content(i)

    html = template.replace("{{title}}", data["title"])\
                   .replace("{{description}}", data["description"])\
                   .replace("{{content}}", data["content"])\
                   .replace("{{ad_code}}", ad_code)\
                   .replace("{{next_link}}", f"page{i+1}.html" if i < 10 else "page1.html")

    with open(f"output_pages/page{i}.html", "w", encoding="utf-8") as f:
        f.write(html)

print("\n✅ 모든 페이지 생성 완료!")

