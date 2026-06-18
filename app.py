import re
import os
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv, set_key

load_dotenv()

st.set_page_config(
    page_title="스레드 대본 생성기",
    page_icon="✍️",
    layout="centered",
)

st.markdown("""
<style>
.stButton > button {
    width: 100%;
    height: 3rem;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 0.5rem;
    margin: 0.2rem 0;
}
.stTextArea textarea {
    font-size: 1rem;
    line-height: 1.7;
}
.stRadio label {
    font-size: 1rem;
    padding: 0.3rem 0;
}
@media (max-width: 768px) {
    .stButton > button {
        height: 3.8rem;
        font-size: 1.15rem;
    }
    .stTextArea textarea {
        font-size: 1.05rem;
    }
    .stRadio label {
        font-size: 1.05rem;
        padding: 0.5rem 0;
    }
}
</style>
""", unsafe_allow_html=True)

COUNTRIES = {
    "🇰🇷 한국": {"country": "한국", "foreign": False},
    "🇯🇵 일본": {"country": "일본", "foreign": True},
    "➕ 직접 입력": {"country": "", "foreign": True},
}

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def get_stored_api_key() -> str:
    # 클라우드 배포 환경: Streamlit secrets에서 읽기
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    # 로컬 환경: .env 파일에서 읽기
    return os.getenv("ANTHROPIC_API_KEY", "")


def save_api_key_locally(key: str):
    with open(ENV_PATH, "w") as f:
        f.write(f"ANTHROPIC_API_KEY={key}\n")


def build_analysis_prompt(script: str, country: str) -> str:
    return f"""당신은 {country} 스레드(Threads) 바이럴 콘텐츠 전문 분석가입니다.
{country}의 SNS 문화와 {country} 2030~40대 여성 독자층의 감수성을 깊이 이해하고 있습니다.

아래 대본이 왜 {country}에서 높은 반응을 얻었는지 분석해주세요.
분석 결과와 아이디어는 반드시 한국어로 작성하세요.

[분석할 대본]
{script}

---
다음 형식으로 출력하세요:

**📊 바이럴 구조 분석**

🪝 **후킹 전략**: 첫 문장이 {country} 2030~40대 여성의 시선을 어떻게 멈추게 하는가? (구체적 기법 명시: 의문 유발/반전 예고/공감 유도/충격/궁금증/{country} 특유의 정서 활용 등)

📐 **콘텐츠 구조**: 전체 흐름의 패턴 (예: 문제제기→공감→해결, 경험담→반전→교훈, 리스트형→점층 등)

💬 **문체와 톤**: {country} SNS 특유의 어투, 문장 길이, 줄바꿈 방식, 이모지 사용 여부

❤️ **감정 트리거**: {country} 2030~40대 여성이 공유하고 싶게 만드는 감정 (공감/놀라움/위로/분노/웃음/정보성 만족감 등)

🔚 **마무리 기법**: 끝맺음이 어떻게 여운을 남기거나 저장·공유를 유도하는가

📏 **형식 특징**: 길이, 단락 구성, {country} 스레드 특유의 시각적 구조

---
**💡 {country} 2030~40대 여성에게 잘 통할 아이디어 6가지** (한국어로 작성)
(위에서 분석한 구조와 감정 트리거를 그대로 활용할 수 있는 다른 주제)

1. [주제] — [이 주제가 {country} 2030~40대 여성에게 잘 통하는 이유]
2. [주제] — [이유]
3. [주제] — [이유]
4. [주제] — [이유]
5. [주제] — [이유]
6. [주제] — [이유]"""


def build_script_prompt(analysis: str, idea: str, country: str, is_foreign: bool) -> str:
    if is_foreign:
        lang_rule = (
            f"대본은 반드시 {country}어(현지 언어)로 작성하고, "
            f"각 버전 대본 바로 아래에 빈 줄을 하나 두고 "
            f"'🇰🇷 한국어 번역:' 이라고 표시한 뒤 한국어 번역을 추가하세요."
        )
    else:
        lang_rule = "한국어로만 작성하세요."

    return f"""당신은 {country} 스레드(Threads) 바이럴 콘텐츠 작가입니다.
{country} 2030~40대 여성의 언어 감각, 관심사, 감수성에 정통합니다.

아래 구조 분석을 바탕으로, {country} 2030~40대 여성을 타겟으로 한
새로운 주제의 대본을 3가지 버전으로 작성하세요.

[원본 바이럴 구조 분석]
{analysis}

[새로 작성할 주제]
{idea}

---
작성 규칙:
1. 원본의 후킹 전략, 구조, 문체, 감정 트리거, 마무리 기법을 충실히 반영
2. {country} 스레드 특성에 맞는 줄바꿈, 문장 호흡, 어투 사용
3. {country} 2030~40대 여성이 "이거 나 얘기다" 싶게 공감대 형성
4. 버전 차별화:
   - 버전 1: 원본 구조에 가장 충실한 정석 버전
   - 버전 2: 후킹 방식을 변주 (다른 감정 트리거 활용)
   - 버전 3: 전개 방식을 변주 (구조 변형)
5. {lang_rule}
6. 설명 없이 아래 형식으로만 출력:

**[ 버전 1 — 정석 ]**
(대본)

**[ 버전 2 — 후킹 변주 ]**
(대본)

**[ 버전 3 — 구조 변주 ]**
(대본)"""


def parse_ideas(text: str) -> list[str]:
    ideas = []
    for match in re.finditer(r'^\s*([1-6])\.\s+(.+)', text, re.MULTILINE):
        ideas.append(match.group(2).strip())
    return ideas[:6]


def parse_scripts(text: str) -> list[str]:
    pattern = r'\*\*\[ 버전 \d[^\]]*\]\*\*\s*\n(.*?)(?=\n\*\*\[ 버전 \d|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    return [m.strip() for m in matches] if len(matches) == 3 else [text]


def call_claude(prompt: str, max_tokens: int) -> str:
    client = Anthropic(api_key=st.session_state.api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ── API 키 확인 ──────────────────────────────────────────────────────────────

st.title("✍️ 스레드 대본 생성기")

if "api_key" not in st.session_state:
    st.session_state.api_key = get_stored_api_key()

if not st.session_state.api_key:
    st.markdown("### 🔑 시작 전: API 키 입력")
    st.markdown(
        "[console.anthropic.com](https://console.anthropic.com) 에서 발급받은 "
        "Claude API 키를 입력해주세요. 한 번만 입력하면 저장돼요."
    )
    key_input = st.text_input("API 키", type="password", placeholder="sk-ant-...")
    if st.button("✅ 저장하고 시작하기", type="primary"):
        if key_input.strip().startswith("sk-ant-"):
            st.session_state.api_key = key_input.strip()
            save_api_key_locally(key_input.strip())
            st.success("저장됐어요! 다음부터는 자동으로 입력돼요.")
            st.rerun()
        else:
            st.error("올바른 API 키 형식이 아니에요. 'sk-ant-'로 시작하는 키를 입력해주세요.")
    st.stop()

# ── 사이드바 ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ 설정")
    st.caption("API 키가 저장되어 있습니다.")
    if st.button("🔑 API 키 변경"):
        st.session_state.api_key = ""
        save_api_key_locally("")
        st.rerun()

# ── 본문 ─────────────────────────────────────────────────────────────────────

st.caption("떡상한 대본 분석 → 아이디어 6개 → 새 대본 3개")

country_key = st.selectbox("🌏 국가 선택", list(COUNTRIES.keys()))
cfg = COUNTRIES[country_key]

if country_key == "➕ 직접 입력":
    custom = st.text_input("국가명을 입력하세요 (예: 미국, 인도네시아)")
    country = custom.strip() or "해당 국가"
    is_foreign = True
else:
    country = cfg["country"]
    is_foreign = cfg["foreign"]

st.divider()

# ── STEP 1 ──────────────────────────────────────────────────────────────────
st.markdown("### 1단계: 대본 분석")
script_input = st.text_area(
    "떡상한 스레드 대본을 붙여넣으세요",
    placeholder="대본을 여기에 붙여넣으세요...",
    height=200,
)

if st.button("🔍 분석하기", type="primary"):
    if not script_input.strip():
        st.warning("대본을 먼저 입력해주세요.")
    else:
        with st.spinner("분석 중입니다... (약 20~30초)"):
            try:
                analysis = call_claude(
                    build_analysis_prompt(script_input.strip(), country),
                    max_tokens=2000,
                )
                st.session_state.analysis = analysis
                st.session_state.ideas = parse_ideas(analysis)
                st.session_state.country = country
                st.session_state.is_foreign = is_foreign
                st.session_state.scripts = None
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# ── STEP 2 ──────────────────────────────────────────────────────────────────
if st.session_state.get("analysis"):
    st.divider()
    st.markdown(st.session_state.analysis)

    st.divider()
    st.markdown("### 2단계: 아이디어 선택")

    ideas = st.session_state.get("ideas", [])
    if ideas:
        selected = st.radio(
            "아이디어를 하나 선택하세요",
            ideas,
            label_visibility="collapsed",
        )
    else:
        selected = st.text_input("아이디어를 직접 입력하세요")

    if st.button("✍️ 대본 3개 작성하기", type="primary"):
        if not selected:
            st.warning("아이디어를 선택해주세요.")
        else:
            with st.spinner("대본 작성 중입니다... (약 30~40초)"):
                try:
                    raw = call_claude(
                        build_script_prompt(
                            st.session_state.analysis,
                            selected,
                            st.session_state.country,
                            st.session_state.is_foreign,
                        ),
                        max_tokens=4000,
                    )
                    st.session_state.scripts = parse_scripts(raw)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# ── STEP 3 ──────────────────────────────────────────────────────────────────
if st.session_state.get("scripts"):
    st.divider()
    st.markdown("### 3단계: 대본 선택 및 복사")
    st.caption("텍스트를 클릭 → Ctrl+A(전체선택) → Ctrl+C(복사) 하세요.")

    labels = ["버전 1 — 정석", "버전 2 — 후킹 변주", "버전 3 — 구조 변주"]
    for i, (label, content) in enumerate(zip(labels, st.session_state.scripts)):
        st.markdown(f"**{label}**")
        st.text_area(
            label,
            value=content,
            height=280,
            key=f"script_{i}",
            label_visibility="collapsed",
        )
