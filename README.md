# tech-wiki-skills

AI와 나눈 기술 조사 대화를 **검증된 지식 카드**로 정리하고, 필요하면 **팩트체크를 거친 블로그 글**로 승격하는 Claude Code 스킬 모음입니다. 옵시디언 vault(`raw/` → `Cards/` → `Blog-drafts/`)를 기준으로 동작합니다.

## 왜 만들었나

AI와 기술 조사를 하고 나서 정리하려고 하면 세 가지 문제에 반복해서 부딪혔습니다.

1. **스코프 번짐**: 새 용어가 나올 때마다 끝까지 파고들다가 정리를 포기하게 됩니다.
2. **근거 오염**: 대화 기록에 "적혀 있다"는 이유로 AI가 검색 없이 말한 내용이 근거처럼 굳어집니다.
3. **숫자 혼입**: 벤치마크는 실제로 있는데, 수치는 다른 연구 것이 섞여 들어갑니다. 완전한 허위보다 이쪽이 훨씬 흔하고 잡아내기도 어렵습니다.

이 스킬들은 위 세 문제를 각각 단계별 규칙으로 막습니다.

## 파이프라인

```mermaid
flowchart LR
    A[조사 대화] --> B["raw 저장<br/>+ 근거 태깅"]
    B --> C[원문 팩트체크]
    C --> D["깊이 게이트<br/>→ 카드"]
    D --> E[블로그 승격]
    E --> F[블로그 팩트체크]
    F --> G[휴머나이즈]
    G --> H[vault 구조 감사]
```

단계 사이에서는 사람의 판단이 필요한 지점(어떤 카드를 승격할지, 불일치 항목을 어떻게 할지, 파일 삭제 여부 등)마다 반드시 멈추고 확인을 받습니다.

| 스킬 | 역할 |
|---|---|
| `tech-research-card` | 대화 원문 저장과 근거 태깅, 깊이 게이트로 용어 분류, 고정 템플릿 카드 생성 |
| `tech-research-card-blog` | 카드를 블로그 초안으로 승격 (구조모드/서술모드, 이미지 슬롯, 문체 점검) |
| `tech-wiki-factcheck` | 초안의 수치·벤치마크·귀속을 항목별 웹 검색으로 재확인하고, 종합판단 문장도 따로 검증 |
| `blog-draft-structure` | 사람이 직접 쓴 **평문** 초안에 헤딩 위계·표·이미지 슬롯을 제안 (본문 문장은 건드리지 않음) |
| `tech-wiki-audit` | vault 구조가 `CLAUDE.md` 규칙에서 벗어났는지 감사 (최상위 문서, flat 구조, 깨진 링크 등) |
| `tech-wiki-pipeline` | 위 스킬(`blog-draft-structure` 제외)과 `humanize-korean`을 순서대로 호출하는 오케스트레이터 |

각 스킬 폴더의 `SKILL.md`가 실제 지침입니다. `tech-wiki-pipeline`은 얇은 래퍼라서 하위 스킬의 로직을 복사해 두지 않습니다. 하위 스킬을 고치면 파이프라인에도 그대로 반영됩니다.

## 핵심 아이디어

**깊이 게이트**: 대화에 나온 용어를 그 자리에서 4가지로 분류해서, 어디까지 팔지를 바로 정합니다.

| 분류 | 처리 |
|---|---|
| 핵심개념 | 별도 카드 |
| 핵심전제 | 카드 안에 1~2문장 정의만 |
| 비교 필수 대상 | 비교표 한 줄 분량만 |
| 인접배경 | `#추후조사` 태그만 달고 넘어감 |

**근거 태깅**: 원문을 저장할 때 수치·벤치마크 주장마다 `[실측]`, `[검색확인: URL]`, `[AI진술-미검증]` 중 하나를 붙입니다. `[AI진술-미검증]`에서 나온 내용은 카드 신뢰도가 무조건 "확인필요"에서 시작하고, 외부 검증을 거쳐야만 올라갑니다.

**3축 팩트체크와 종합판단 검증**: 벤치마크가 실재하는지, 수치가 일치하는지, 귀속이 맞는지를 각각 따로 확인합니다. 그다음 개별 사실이 모두 맞더라도 "따라서 A와 B 모두 ~하다" 같은 결론 문장이 비교표의 세부 내용과 어긋나지 않는지 한 번 더 대조합니다.

**출처유형 규칙**: 직접 측정하지 않은 수치를 사용자의 결과처럼 쓰지 않습니다. 문헌조사라면 "○○ 논문에서는 A라고 보고했다"처럼 출처를 밝혀서 씁니다.

## 결과물 예시

깊이 게이트를 거친 탐색 노트:

```
## 탐색 노트: BM25 (2026-08-14)
- BM25 → 핵심개념 (별도 카드)
- TF-IDF → 핵심전제: "단어 빈도와 문서 희소성을 곱해 가중치를 매기는 고전적 방식"
- SPLADE → 비교 필수 대상: "학습된 희소 표현, 쿼리 확장을 모델이 수행"
- 역색인 압축 기법 → 인접배경 #추후조사
```

그 노트로 만든 카드 (`Cards/BM25는 어떻게 작동하는가.md`):

```markdown
## BM25는 어떻게 작동하는가?

- 정의: 단어 빈도(TF)에 포화 곡선을 씌우고 문서 길이로 정규화한 확률적 랭킹 함수.
- 왜 중요한가: 학습 없이 바로 쓸 수 있고, 하이브리드 검색에서 여전히 기준선 역할을 한다.
- 인접 개념과의 차이:

| 항목 | BM25 | TF-IDF | SPLADE |
|---|---|---|---|
| 학습 필요 | 없음 | 없음 | 있음 |
| 단어 빈도 처리 | 포화(k1) | 선형 | 모델이 가중치 결정 |

- 예시: Elasticsearch 공식 문서에서는 기본값을 k1=1.2, b=0.75로 안내한다.
- 신뢰도: 확인됨
- 출처유형: 문헌조사
- 조사일: 2026-08-14
- 관련 문서: [[SPLADE는 BM25를 대체하는가]]
- 다시 물어볼 질문:
  - 한국어 형태소 분석기를 바꾸면 k1 최적값도 달라지는가?
```

## 시작하기

### 1. 저장소 받기

```bash
git clone https://github.com/hyos0415/tech-wiki-skills.git ~/claude-skills
```

### 2. 스킬 연결

`~/.claude/skills/` 아래에 각 스킬 폴더를 링크합니다. 복사 대신 링크를 쓰면 저장소를 `git pull`하는 것만으로 스킬이 갱신됩니다.

macOS/Linux:

```bash
mkdir -p ~/.claude/skills
for name in tech-research-card tech-research-card-blog tech-wiki-factcheck tech-wiki-audit tech-wiki-pipeline blog-draft-structure; do
  ln -s "$HOME/claude-skills/$name" "$HOME/.claude/skills/$name"
done
```

Windows (PowerShell, 관리자 권한이 필요 없는 junction 사용):

```powershell
$skills = @('tech-research-card','tech-research-card-blog','tech-wiki-factcheck','tech-wiki-audit','tech-wiki-pipeline','blog-draft-structure')
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
foreach ($name in $skills) {
    New-Item -ItemType Junction -Path "$HOME\.claude\skills\$name" -Target "$HOME\claude-skills\$name"
}
```

### 3. vault 만들기

`vault-template/`을 원하는 위치에 복사하고 옵시디언에서 vault로 엽니다.

```bash
cp -r ~/claude-skills/vault-template ~/tech-wiki-vault
```

그다음 `CLAUDE.md` 맨 위의 **Vault 경로**를 실제 경로로 바꿉니다. 스킬은 vault 안의 `CLAUDE.md`를 최종 규칙으로 따르므로, 폴더 구성이나 카드 템플릿을 바꾸고 싶으면 이 파일을 고치면 됩니다.

```
tech-wiki-vault/
├── CLAUDE.md              # 규칙 (유일한 기준)
├── index.md               # 카드·초안 목록
├── log.md                 # 처리 이력
├── raw/                   # 원본 대화 (수정 금지)
├── Cards/                 # 자산화 카드
├── Blog-drafts/           # 블로그 초안
├── Scratch/               # 임시 작업 공간 (git 제외)
└── Templates/card-template.md
```

### 4. (선택) humanize-korean 설치

`tech-wiki-pipeline`의 휴머나이즈 단계는 별도 플러그인 [humanize-korean](https://github.com/epoko77-ai/im-not-ai)을 호출합니다. 파이프라인 전체를 쓸 계획이면 Claude Code에서 설치합니다.

```
/plugin marketplace add epoko77-ai/im-not-ai
/plugin install humanize-korean@im-not-ai
```

### 5. 사용

Claude Code를 vault 폴더에서 열고 이렇게 요청하면 됩니다.

| 하고 싶은 일 | 요청 예시 |
|---|---|
| 대화를 카드로 정리 | "이 대화 카드로 만들어줘" (대화 원문을 붙여넣기) |
| 카드를 블로그로 | "`Cards/BM25는 어떻게 작동하는가.md` 블로그로 승격해줘" |
| 초안 팩트체크 | "이 초안 팩트체크해줘" |
| 직접 쓴 글 구조 잡기 | "이 글 위계 정리해줘" |
| vault 점검 | "vault 구조 점검해줘" |
| 처음부터 끝까지 | "이 조사 전체 파이프라인 돌려줘" |

## 요구사항과 알려진 제약

- **Bash 필요**: 링크 검증과 구조 감사가 `comm`, `find`, 프로세스 치환(`<(...)`)을 씁니다. Windows에서는 Git Bash가 있으면 동작합니다.
- **macOS의 `find -regex`**: `tech-wiki-audit`의 번호 코드 파일명 검사(D 항목)는 GNU find 문법이라, BSD find를 쓰는 macOS에서는 `find -E`로 바꾸거나 GNU findutils를 설치해야 합니다.
- **과거 대화 검색은 claude.ai 전용**: `tech-research-card`가 언급하는 `conversation_search`/`recent_chats`는 claude.ai 도구입니다. Claude Code에서는 대화 원문을 직접 붙여넣거나 파일로 넘겨 주세요.
- **다이어그램 스킬 의존**: `tech-research-card-blog`와 `blog-draft-structure`는 다이어그램 슬롯을 만나면 다이어그램 스킬로 그리려고 시도합니다. 그런 스킬이 없는 환경에서는 `{이미지: ...}` 슬롯만 남고, 그림은 직접 그려야 합니다.
- **humanize-korean과 Python**: 휴머나이즈 단계는 Python이 있으면 정량 채점·결정적 게이트를 씁니다. Python이 없으면 수동 경로(진단 → 겨냥 윤문, 사람이 직접 대조 검토)로 넘어가도록 스킬 안에 안내가 있습니다.
- **모델 지정**: 대부분의 스킬이 frontmatter에서 `model: sonnet`을 지정합니다. 처음엔 분류를 haiku로 돌렸는데, "핵심전제 vs 비교 필수 대상" 같은 경계 판단에서 정확도가 떨어져 올렸습니다.
- **한국어 전용**: 지침, 템플릿, 문체 규칙이 모두 한국어 블로그 기준입니다.

## 수정할 때 원칙

- vault의 `CLAUDE.md`가 최종 규칙입니다. 규칙이 바뀌면 `CLAUDE.md`를 먼저 고치고 스킬을 맞춥니다.
- `tech-wiki-pipeline`에 개별 스킬 로직을 복사하지 않습니다(얇은 래퍼 원칙).

## 라이선스

[MIT](LICENSE)
